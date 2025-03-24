from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import bcrypt
import re

user_bp = Blueprint('user', __name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["enolity"]

@user_bp.route("/profile", methods=["GET"])
def get_profile():
    """
    Fetch the logged-in user's details using their unique ID.
    The user ID should be provided as a query parameter named "id".
    """
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": 0, "msg": "User ID is required to fetch profile details.", "class": "error"}), 400
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"status": 0, "msg": "Invalid user ID.", "class": "error"}), 400

    user = db.useres.find_one({"_id": user_id})
    if not user:
        return jsonify({"status": 0, "msg": "User not found.", "class": "error"}), 404

    # Remove sensitive information such as password.
    user.pop("password", None)
    return jsonify({"status": 1, "msg": "User details fetched successfully.", "class": "success", "user": user})

@user_bp.route("/update_details", methods=["POST"])
def update_details():
    """
    Update user details based on the user's unique ID.
    The request must include the "_id" field.  
    All fields (including email) can be updated except the "_id".
    """
    input_data = request.get_json()
    if not input_data or "_id" not in input_data:
        return jsonify({"status": 0, "msg": "User ID is required to update details.", "class": "error"}), 400

    user_id = input_data["_id"]
    # Allow email update by NOT removing it from the update payload.
    update_data = input_data.copy()
    update_data.pop("_id", None)  # Prevent updating the unique ID

    # Validate phone number if provided.
    if "phonenumber" in update_data:
        phonenumber = update_data["phonenumber"]
        if not re.fullmatch(r"\d{10}", phonenumber):
            return jsonify({"status": 400, "msg": "Phone number must be exactly 10 digits."}), 400

    result = db.useres.update_one({"_id": user_id}, {"$set": update_data})
    if result.matched_count == 0:
        return jsonify({"status": 404, "msg": "User not found."}), 404

    return jsonify({"status": 200, "msg": "User details updated successfully."}), 200

@user_bp.route("/get_id_by_email", methods=["GET"])
def get_id_by_email():
    """
    Fetch the user's unique ID based on their email.
    The email should be provided as a query parameter.
    """
    email = request.args.get("email")
    if not email:
        return jsonify({"status": 400, "msg": "Email parameter is required."}), 400

    user = db.useres.find_one({"email": email})
    if not user:
        return jsonify({"status": 404, "msg": "User not found."}), 404
    
    return jsonify({
        "status": 200,
        "msg": "User ID retrieved successfully.",
        "id": user.get("_id")
    }), 200


@user_bp.route("/update_password", methods=["POST"])
def update_password():
    """
    Update the user's password.
    Requires:
      - _id (unique identifier)
      - old_password (to verify identity)
      - new_password (which will be validated and hashed)
    """
    input_data = request.get_json()
    if not input_data or not all(k in input_data for k in ("_id", "old_password", "new_password")):
        return jsonify({"status": 0, "msg": "User ID, old_password, and new_password are required.", "class": "error"}), 400

    user_id = input_data["_id"]
    old_password = input_data["old_password"]
    new_password = input_data["new_password"]

    # Validate new password strength.
    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,16}$", new_password):
        return jsonify({
            "status": 400,
            "msg": "Password must be 8-16 characters long, include uppercase, lowercase, a number, and a special character.",
        }), 400
    if "gmail" in new_password.lower():
        return jsonify({
            "status": 400,
            "msg": "Password should not contain 'gmail'.",
        }), 400

    # Retrieve user details from the database.
    user = db.useres.find_one({"_id": user_id})
    if not user:
        return jsonify({"status": 404, "msg": "User not found."}), 404

    # Verify the old password.
    if not bcrypt.checkpw(old_password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({"status": 400, "msg": "Old password is incorrect."}), 400

    # Hash and update the new password.
    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.useres.update_one({"_id": user_id}, {"$set": {"password": hashed_new_password}})
    
    return jsonify({"status": 200, "msg": "Password updated successfully."})

@user_bp.route("/getuser", methods=["GET"])
def get_user():
    """
    Admin endpoint to search for a user by unique ID.
    The user ID should be provided as a query parameter named "id".
    """
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": 0, "msg": "User ID query parameter is required."}), 400
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"status": 400, "msg": "Invalid user ID."}), 400

    user = db.useres.find_one({"_id": user_id})
    if not user:
        return jsonify({"status": 400, "msg": "User not found."}), 404

    # Remove sensitive information such as password.
    user.pop("password", None)
    return jsonify({"status": 200, "user": user})
