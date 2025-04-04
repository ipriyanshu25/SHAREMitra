from flask import Blueprint, request, jsonify
import datetime
from bson.objectid import ObjectId
from passlib.hash import bcrypt
import uuid
import random
import string
import re
from db import db  # Ensure this imports your configured PyMongo instance

user_bp = Blueprint("user", __name__, url_prefix="/user")

def generate_referral_code(length=6):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

def generate_short_id(prefix="usr"):
    suffix = uuid.uuid4().hex[:6]
    return f"{prefix}_{suffix}"

def is_valid_name(name: str) -> bool:
    return len(name) <= 50

def is_valid_email(email: str) -> bool:
    if len(email) < 5 or len(email) > 100:
        return False
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def is_valid_phone(phone: str) -> bool:
    pattern = r"^[0-9]{10}$"
    return bool(re.match(pattern, phone))

def is_valid_password(password: str) -> bool:
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,16}$'
    return bool(re.match(pattern, password))

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    name = data.get("name", "")
    email = data.get("email", "")
    phone = data.get("phone", "")
    password = data.get("password", "")
    state = data.get("state", "")
    city = data.get("city", "")
    dob = data.get("dob", "")  # Expecting YYYY-MM-DD format
    used_referral_code = data.get("referralCode")

    if not name or not is_valid_name(name):
        return jsonify({"error": "Invalid name (max 50 chars)."}), 400
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format or length (5-100 chars)."}), 400
    if not is_valid_phone(phone):
        return jsonify({"error": "Phone must be exactly 10 digits."}), 400
    if not is_valid_password(password):
        return jsonify({"error": "Password must be 8-16 chars with uppercase, lowercase, digit, and special char."}), 400
    if not state or not city:
        return jsonify({"error": "State and city are required."}), 400
    try:
        dob_parsed = datetime.datetime.strptime(dob, "%Y-%m-%d").date().isoformat()
    except ValueError:
        return jsonify({"error": "Invalid date of birth format (YYYY-MM-DD required)."}), 400

    existing_user = db.users.find_one({"$or": [{"email": email}, {"phone": phone}]})
    if existing_user:
        if existing_user["email"] == email:
            return jsonify({"error": "Email already registered."}), 400
        else:
            return jsonify({"error": "Phone number already registered."}), 400

    user_id_str = str(ObjectId())

    referral_code = generate_referral_code(6)
    while db.users.find_one({"referralCode": referral_code}):
        referral_code = generate_referral_code(6)

    password_hash = bcrypt.hash(password)

    referred_by = None
    if used_referral_code:
        referrer = db.users.find_one({"referralCode": used_referral_code})
        if not referrer:
            return jsonify({"error": "Invalid referral code."}), 400
        referred_by = used_referral_code
        db.users.update_one({"referralCode": used_referral_code}, {"$inc": {"referralCount": 1}})

    user_doc = {
        "userId": user_id_str,
        "referralCode": referral_code,
        "referredBy": referred_by,
        "referralCount": 0,
        "name": name,
        "email": email,
        "phone": phone,
        "state": state,
        "city": city,
        "dob": dob_parsed,
        "passwordHash": password_hash,
        "razorpay_contact_id": None,
        "razorpay_fund_account_id": None,
        "totalPayoutAmount": 0,
        "createdAt": datetime.datetime.utcnow(),
        "updatedAt": datetime.datetime.utcnow()
    }

    db.users.insert_one(user_doc)
    
    # Immediately create a wallet for the user with initial total money 0
    wallet_doc = {
         "userId": user_id_str,
         "total_earning": 0,
         "withdrawn": 0,
         "balance": 0,
         "tasks": [],
         "createdAt": datetime.datetime.utcnow(),
         "updatedAt": datetime.datetime.utcnow()
    }
    db.wallet.insert_one(wallet_doc)

    return jsonify({
        "message": "User registered successfully",
        "userId": user_id_str
    }), 201

@user_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    identifier = data.get("identifier", "")  # User provides either email or phone
    password = data.get("password", "")

    if not password:
        return jsonify({"error": "Password is required"}), 400
    if not identifier:
        return jsonify({"error": "Email or phone is required"}), 400

    query = {}
    if re.match(r"^[0-9]{10}$", identifier):
        query["phone"] = identifier
    elif re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", identifier):
        query["email"] = identifier
    else:
        return jsonify({"error": "Invalid email or phone format."}), 400

    user_doc = db.users.find_one(query, {"passwordHash": 1, "_id": 0})
    if not user_doc:
        return jsonify({"error": "Invalid credentials"}), 401

    if not bcrypt.verify(password, user_doc["passwordHash"]):
        return jsonify({"error": "Invalid credentials"}), 401

    # Ensure that a wallet exists for the user. If not, return an error.
    wallet = db.wallet.find_one({"userId": user_doc["userId"]})
    if not wallet:
        return jsonify({"error": "Invalid user. Wallet not found."}), 400

    user_data = db.users.find_one(query, {"passwordHash": 0, "_id": 0})
    return jsonify({
        "message": "Login successful",
        "user": user_data
    }), 200


@user_bp.route("/getlist", methods=["POST"])
def get_user_list():
    data = request.get_json() or {}
    keyword = data.get("keyword", "")
    try:
        page = int(data.get("page", 0))
    except ValueError:
        return jsonify({"error": "Page must be an integer."}), 400
    try:
        per_page = int(data.get("per_page", 50))
    except ValueError:
        return jsonify({"error": "per_page must be an integer."}), 400

    query = {}
    if keyword:
        query = {
            "$or": [
                {"name": {"$regex": keyword, "$options": "i"}},
                {"email": {"$regex": keyword, "$options": "i"}},
                {"phone": {"$regex": keyword, "$options": "i"}}
            ]
        }

    total_items = db.users.count_documents(query)
    users_cursor = db.users.find(query, {"_id": 0, "passwordHash": 0}).skip(page * per_page).limit(per_page)
    users_list = list(users_cursor)

    return jsonify({
        "total": total_items,
        "page": page,
        "per_page": per_page,
        "users": users_list
    }), 200

@user_bp.route("/getbyid", methods=["GET"])
def get_user_by_id():
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify({"error": "userId query parameter is required"}), 400

    user_doc = db.users.find_one({"userId": user_id}, {
        "_id": 0,
        "passwordHash": 0
    })
    if not user_doc:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user_doc), 200

@user_bp.route("/delete", methods=["POST"])
def delete_user():
    data = request.json or {}
    user_id = data.get("userId")
    if not user_id:
        return jsonify({"error": "userId is required in the body"}), 400

    result = db.users.delete_one({"userId": user_id})
    if result.deleted_count == 0:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "User deleted successfully"}), 200

@user_bp.route("/updatedetails", methods=["POST"])
def update_user_details():
    data = request.json or {}
    user_id = data.get("userId")
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    update_fields = {}
    if "name" in data:
        if not is_valid_name(data["name"]):
            return jsonify({"error": "Invalid name (max 50 chars)."}), 400
        update_fields["name"] = data["name"]

    if "email" in data:
        if not is_valid_email(data["email"]):
            return jsonify({"error": "Invalid email or length exceeded."}), 400
        existing_email = db.users.find_one(
            {"email": data["email"], "userId": {"$ne": user_id}}
        )
        if existing_email:
            return jsonify({"error": "Email is already used by another account."}), 400
        update_fields["email"] = data["email"]

    if "phone" in data:
        if not is_valid_phone(data["phone"]):
            return jsonify({"error": "Phone must be exactly 10 digits."}), 400
        existing_phone = db.users.find_one(
            {"phone": data["phone"], "userId": {"$ne": user_id}}
        )
        if existing_phone:
            return jsonify({"error": "Phone number is already used by another account."}), 400
        update_fields["phone"] = data["phone"]

    if not update_fields:
        return jsonify({"error": "No valid fields to update."}), 400

    update_fields["updatedAt"] = datetime.datetime.utcnow()

    result = db.users.update_one(
        {"userId": user_id},
        {"$set": update_fields}
    )
    if result.matched_count == 0:
        return jsonify({"error": "User not found."}), 404

    return jsonify({"message": "User details updated."}), 200

@user_bp.route("/updatepassword", methods=["POST"])
def update_password():
    data = request.json or {}
    user_id = data.get("userId")
    old_password = data.get("oldPassword", "")
    new_password = data.get("newPassword", "")

    if not user_id or not old_password or not new_password:
        return jsonify({"error": "userId, oldPassword, and newPassword are required"}), 400

    if not is_valid_password(new_password):
        return jsonify({
            "error": (
                "Password must be 8-16 chars, include uppercase, lowercase, "
                "digit, and special character."
            )
        }), 400

    user_doc = db.users.find_one({"userId": user_id})
    if not user_doc:
        return jsonify({"error": "User not found"}), 404

    if not bcrypt.verify(old_password, user_doc["passwordHash"]):
        return jsonify({"error": "Old password is incorrect"}), 401

    new_hash = bcrypt.hash(new_password)
    db.users.update_one(
        {"_id": user_doc["_id"]},
        {
            "$set": {
                "passwordHash": new_hash,
                "updatedAt": datetime.datetime.utcnow()
            }
        }
    )
    return jsonify({"message": "Password updated successfully"}), 200

@user_bp.route("/referrals", methods=["GET"])
def get_referrals():
    referral_code = request.args.get("referralCode")
    if not referral_code:
        return jsonify({"error": "referralCode query param required"}), 400

    referrer = db.users.find_one({"referralCode": referral_code})
    if not referrer:
        return jsonify({"error": "Invalid referral code"}), 404

    referred_users = list(db.users.find(
        {"referredBy": referral_code},
        {"_id": 0, "passwordHash": 0}
    ))

    return jsonify({
        "referralCount": len(referred_users),
        "referredUsers": referred_users
    }), 200







