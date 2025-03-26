# from flask import Blueprint, request, jsonify
# from pymongo import MongoClient
# import bcrypt
# import re
# from bson import ObjectId

# user_bp = Blueprint('user', __name__)

# # Connect to MongoDB
# client = MongoClient("mongodb://localhost:27017")
# db = client["enolity"]

# @user_bp.route("/profile", methods=["GET"])
# def get_profile():
#     """
#     Fetch the logged-in user's details using their userId.
#     The userId should be provided as a query parameter named "user_id".
#     """
#     user_id = request.args.get("user_id")
#     if not user_id:
#         return jsonify({"status": 0, "msg": "User ID is required to fetch profile details.", "class": "error"}), 400

#     user = db.users.find_one({"userId": user_id})
#     if not user:
#         return jsonify({"status": 0, "msg": "User not found.", "class": "error"}), 404

#     user.pop("password", None)
#     user["_id"] = str(user["_id"])
#     return jsonify({"status": 1, "msg": "User details fetched successfully.", "class": "success", "user": user})



# @user_bp.route("/update_details", methods=["POST"])
# def update_details():
#     """
#     Update user details based on the user's unique ID.
#     The request must include the "_id" field.
#     All fields (including email) can be updated except the "_id".
#     """
#     input_data = request.get_json()
#     if not input_data or "_id" not in input_data:
#         return jsonify({"status": 0, "msg": "User ID is required to update details.", "class": "error"}), 400

#     user_id_str = input_data["_id"]
#     try:
#         user_id = ObjectId(user_id_str)
#     except Exception:
#         return jsonify({"status": 0, "msg": "Invalid user ID.", "class": "error"}), 400

#     update_data = input_data.copy()
#     update_data.pop("_id", None)  # Prevent updating the unique ID

#     if "phonenumber" in update_data:
#         phonenumber = update_data["phonenumber"]
#         if not re.fullmatch(r"\d{10}", phonenumber):
#             return jsonify({"status": 400, "msg": "Phone number must be exactly 10 digits."}), 400

#     result = db.users.update_one({"_id": user_id}, {"$set": update_data})
#     if result.matched_count == 0:
#         return jsonify({"status": 404, "msg": "User not found."}), 404

#     return jsonify({"status": 200, "msg": "User details updated successfully."}), 200


# @user_bp.route("/get_id_by_email", methods=["GET"])
# def get_id_by_email():
#     """
#     Fetch the user's unique ID based on their email.
#     The email should be provided as a query parameter.
#     """
#     email = request.args.get("email")
#     if not email:
#         return jsonify({"status": 400, "msg": "Email parameter is required."}), 400

#     user = db.users.find_one({"email": email})
#     if not user:
#         return jsonify({"status": 404, "msg": "User not found."}), 404

#     return jsonify({
#         "status": 200,
#         "msg": "User ID retrieved successfully.",
#         "id": str(user.get("_id"))
#     }), 200


# @user_bp.route("/update_password", methods=["POST"])
# def update_password():
#     """
#     Update the user's password.
#     Requires:
#       - _id (unique identifier)
#       - old_password (to verify identity)
#       - new_password (which will be validated and hashed)
#     """
#     input_data = request.get_json()
#     if not input_data or not all(k in input_data for k in ("_id", "old_password", "new_password")):
#         return jsonify({"status": 0, "msg": "User ID, old_password, and new_password are required.", "class": "error"}), 400

#     user_id_str = input_data["_id"]
#     try:
#         user_id = ObjectId(user_id_str)
#     except Exception:
#         return jsonify({"status": 0, "msg": "Invalid user ID.", "class": "error"}), 400

#     old_password = input_data["old_password"]
#     new_password = input_data["new_password"]

#     if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,16}$", new_password):
#         return jsonify({
#             "status": 400,
#             "msg": "Password must be 8-16 characters long, include uppercase, lowercase, a number, and a special character.",
#         }), 400

#     if "gmail" in new_password.lower():
#         return jsonify({
#             "status": 400,
#             "msg": "Password should not contain 'gmail'.",
#         }), 400

#     user = db.users.find_one({"_id": user_id})
#     if not user:
#         return jsonify({"status": 404, "msg": "User not found."}), 404

#     if not bcrypt.checkpw(old_password.encode('utf-8'), user['password'].encode('utf-8')):
#         return jsonify({"status": 400, "msg": "Old password is incorrect."}), 400

#     hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
#     db.users.update_one({"_id": user_id}, {"$set": {"password": hashed_new_password}})

#     return jsonify({"status": 200, "msg": "Password updated successfully."})


# # @user_bp.route("/getuser", methods=["GET"])
# # def get_user():
# #     """
# #     Admin endpoint to search for a user by unique ID.
# #     The user ID should be provided as a query parameter named "id".
# #     """
# #     user_id_str = request.args.get("id")
# #     if not user_id_str:
# #         return jsonify({"status": 0, "msg": "User ID query parameter is required."}), 400

# #     try:
# #         user_id = ObjectId(user_id_str)
# #     except Exception:
# #         return jsonify({"status": 400, "msg": "Invalid user ID."}), 400

# #     user = db.users.find_one({"_id": user_id})
# #     if not user:
# #         return jsonify({"status": 400, "msg": "User not found."}), 404

# #     user.pop("password", None)
# #     user["_id"] = str(user["_id"])
# #     return jsonify({"status": 200, "user": user})



# @user_bp.route("/getuser", methods=["GET"])
# def get_user():
#     """
#     Admin endpoint to search for a user using their email address.
#     Query parameter: ?email=user@example.com
#     """
#     email = request.args.get("email")
#     if not email:
#         return jsonify({"status": 0, "msg": "Email query parameter is required."}), 400

#     user = db.users.find_one({"email": email})
#     if not user:
#         return jsonify({"status": 404, "msg": "User not found."}), 404

#     user.pop("password", None)
#     user["_id"] = str(user["_id"])
#     return jsonify({"status": 200, "user": user}), 200



# @user_bp.route("/all", methods=["GET"])
# def get_all_users():
#     all_users_cursor = db.users.find({})
#     all_users = []

#     for usr in all_users_cursor:
#         print("Fetched User:", usr)  # 👈 Log to terminal
#         usr["_id"] = str(usr["_id"])
#         usr.pop("password", None)
#         all_users.append(usr)

#     print("Total Users Fetched:", len(all_users))  # 👈 Log to terminal
#     print("Users in this MongoDB:", list(db.users.find({})))
#     return jsonify({"status": 200, "users": all_users}), 200





from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import re
import bcrypt
from bson import ObjectId

user_bp = Blueprint('user', __name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["enoylity"]

@user_bp.route("/profile", methods=["GET"])
def get_profile():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": 0, "msg": "User ID is required.", "class": "error"}), 400

    user = db.users.find_one({"userId": user_id})
    if not user:
        return jsonify({"status": 0, "msg": "User not found.", "class": "error"}), 404

    user.pop("password", None)
    user["_id"] = str(user["_id"])
    return jsonify({"status": 1, "msg": "User profile fetched.", "class": "success", "user": user})


@user_bp.route("/update_details", methods=["POST"])
def update_details():
    input_data = request.get_json()
    user_id = input_data.get("user_id")
    if not user_id:
        return jsonify({"status": 0, "msg": "User ID is required.", "class": "error"}), 400

    update_data = input_data.copy()
    update_data.pop("user_id", None)

    if "phonenumber" in update_data:
        if not re.fullmatch(r"\d{10}", update_data["phonenumber"]):
            return jsonify({"status": 0, "msg": "Phone number must be exactly 10 digits.", "class": "error"}), 400

    result = db.users.update_one({"userId": user_id}, {"$set": update_data})
    if result.matched_count == 0:
        return jsonify({"status": 0, "msg": "User not found.", "class": "error"}), 404

    return jsonify({"status": 1, "msg": "User details updated successfully.", "class": "success"})


@user_bp.route("/get_id_by_email", methods=["GET"])
def get_id_by_email():
    email = request.args.get("email")
    if not email:
        return jsonify({"status": 0, "msg": "Email is required.", "class": "error"}), 400

    user = db.users.find_one({"email": email})
    if not user:
        return jsonify({"status": 0, "msg": "User not found.", "class": "error"}), 404

    return jsonify({"status": 1, "msg": "User ID fetched.", "id": user["userId"]})


@user_bp.route("/update_password", methods=["POST"])
def update_password():
    input_data = request.get_json()
    user_id = input_data.get("user_id")
    old_password = input_data.get("old_password")
    new_password = input_data.get("new_password")

    if not all([user_id, old_password, new_password]):
        return jsonify({"status": 0, "msg": "All fields are required.", "class": "error"}), 400

    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,16}$", new_password):
        return jsonify({"status": 0, "msg": "Password must be 8-16 characters with upper, lower, number and special character.", "class": "error"}), 400

    if "gmail" in new_password.lower():
        return jsonify({"status": 0, "msg": "Password should not contain 'gmail'.", "class": "error"}), 400

    user = db.users.find_one({"userId": user_id})
    if not user or not bcrypt.checkpw(old_password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({"status": 0, "msg": "Old password is incorrect.", "class": "error"}), 400

    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.users.update_one({"userId": user_id}, {"$set": {"password": hashed_new_password}})

    return jsonify({"status": 1, "msg": "Password updated successfully.", "class": "success"})


@user_bp.route("/getuser", methods=["GET"])
def get_user_by_email():
    email = request.args.get("email")
    if not email:
        return jsonify({"status": 0, "msg": "Email is required.", "class": "error"}), 400

    user = db.users.find_one({"email": email})
    if not user:
        return jsonify({"status": 0, "msg": "User not found.", "class": "error"}), 404

    user.pop("password", None)
    user["_id"] = str(user["_id"])
    return jsonify({"status": 1, "user": user})


@user_bp.route("/all", methods=["GET"])
def get_all_users():
    users = []
    for user in db.users.find({}):
        user["_id"] = str(user["_id"])
        user.pop("password", None)
        users.append(user)

    return jsonify({"status": 200, "users": users}),200
