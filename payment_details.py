from flask import Flask, request, jsonify, Blueprint
from pymongo import MongoClient
from datetime import datetime
import re
import requests
from bson import ObjectId

payment_details_bp = Blueprint("payment", __name__)

# Connect to MongoDB and use a database called "enoylity"
client = MongoClient("mongodb://localhost:27017")
db = client["enoylity"]

def validate_ifsc(ifsc_code: str):
    """
    Validate the IFSC code format and check whether it exists using the Razorpay IFSC API.
    The expected format is 11 characters: first 4 alphabets, followed by '0', and then 6 alphanumeric characters.
    
    Returns:
      (bool, dict or str): A tuple where the first element is True if the IFSC code is valid,
                           and the second element contains the bank details (if valid) or an error message.
    """
    pattern = r'^[A-Za-z]{4}0[A-Za-z0-9]{6}$'
    if not re.match(pattern, ifsc_code):
        return False, "IFSC code does not match the expected format (e.g., SBIN0005943)."
    
    try:
        response = requests.get(f"https://ifsc.razorpay.com/{ifsc_code}")
        if response.status_code == 200:
            data = response.json()
            return True, data  # data contains bank, branch, address, etc.
        else:
            return False, "IFSC code not found or invalid."
    except Exception as e:
        return False, f"Error while validating IFSC code: {str(e)}"

@payment_details_bp.route("/payment-details", methods=["POST"])
def payment_details():
    data = request.get_json()
    payment_method = data.get("paymentMethod")
    user_id = data.get("userId")

    if not payment_method:
        return jsonify({"status": 0, "msg": "Payment method not provided"}), 400
    if not user_id:
        return jsonify({"status": 0, "msg": "User ID is required"}), 400

    # Check if payment method already exists for this user
    existing_payment = db.payment.find_one({
        "userId": user_id,
        "paymentMethod": 1 if payment_method == "bank" else 0
    })

    if payment_method == "bank":
        accountHolder = data.get("accountHolder")
        accountNumber = data.get("accountNumber")
        ifsc = data.get("ifsc")
        bankName = data.get("bankName")
        if not (accountHolder and accountNumber and ifsc and bankName):
            return jsonify({"status": 0, "msg": "Incomplete bank details"}), 400

        valid, bank_info = validate_ifsc(ifsc)
        if not valid:
            return jsonify({"status": 404, "msg": "Invalid IFSC code"}), 404

        document = {
            "userId": user_id,
            "paymentMethod": 1,
            "accountHolder": accountHolder,
            "accountNumber": accountNumber,
            "ifsc": ifsc,
            "bankName": bankName,
            "ifscDetails": bank_info,
            "created_at": datetime.utcnow()
        }

    elif payment_method == "upi":
        upiId = data.get("upiId")
        if not upiId:
            return jsonify({"status": 0, "msg": "UPI ID not provided"}), 400

        document = {
            "userId": user_id,
            "paymentMethod": 0,
            "upiId": upiId,
            "created_at": datetime.utcnow()
        }

    else:
        return jsonify({"status": 0, "msg": "Invalid payment method"}), 400

    if existing_payment:
        result = db.payment.update_one(
            {"_id": existing_payment["_id"]},
            {"$set": document}
        )
        if result.modified_count > 0:
            return jsonify({"status": 200, "msg": "Payment details updated successfully"})
        else:
            return jsonify({"status": 200, "msg": "No changes detected in payment details"})
    else:
        # Create new payment
        document["paymentId"] = str(ObjectId())
        result = db.payment.insert_one(document)
        if result.inserted_id:
            return jsonify({"status": 200, "msg": "Payment details saved successfully"})
        else:
            return jsonify({"status": 500, "msg": "Failed to save payment details"}), 500

def payment_details():
    data = request.get_json()

    # Ensure paymentMethod is provided in the payload
    payment_method = data.get("paymentMethod")
    if not payment_method:
        return jsonify({"status": 0, "msg": "Payment method not provided"}), 400

    # Ensure userId is provided
    user_id = data.get("userId")
    if not user_id:
        return jsonify({"status": 0, "msg": "User ID is required"}), 400

    # Generate a new paymentId for this payment document.
    payment_id = str(ObjectId())

    # Process Bank Account details
    if payment_method == "bank":
        accountHolder = data.get("accountHolder")
        accountNumber = data.get("accountNumber")
        ifsc = data.get("ifsc")
        bankName = data.get("bankName")
        if not (accountHolder and accountNumber and ifsc and bankName):
            return jsonify({"status": 0, "msg": "Incomplete bank details"}), 400

        # Validate IFSC code and retrieve bank details
        valid, bank_info = validate_ifsc(ifsc)
        if not valid:
            return jsonify({"status": 404, "msg": "Invalid IFSC code"}), 404

        # Prepare document with IFSC details included, along with userId and paymentId
        document = {
            "userId": user_id,
            "paymentId": payment_id,
            "paymentMethod": 1,  # 1 indicates bank account details
            "accountHolder": accountHolder,
            "accountNumber": accountNumber,
            "ifsc": ifsc,
            "bankName": bankName,
            "ifscDetails": bank_info,  # Store the complete bank details returned by the API
            "created_at": datetime.utcnow()
        }

    # Process UPI details
    elif payment_method == "upi":
        upiId = data.get("upiId")
        if not upiId:
            return jsonify({"status": 0, "msg": "UPI ID not provided"}), 400

        document = {
            "userId": user_id,
            "paymentId": payment_id,
            "paymentMethod": 0,  # 0 indicates UPI details
            "upiId": upiId,
            "created_at": datetime.utcnow()
        }
    else:
        return jsonify({"status": 0, "msg": "Invalid payment method"}), 400

    result = db.payment.insert_one(document)
    if result.inserted_id:
        return jsonify({"status": 200, "msg": "Payment details saved successfully"})
    else:
        return jsonify({"status": 404, "msg": "Failed to save payment details"}), 500


@payment_details_bp.route("/payment-details/user/<user_id>", methods=["GET"])
def get_payment_details_by_user(user_id):
    """
    Fetch payment details for a specific user by their user ID.
    """
    # Query the payment collection for documents with the matching userId.
    payments = list(db.payment.find({"userId": user_id}))
    if not payments:
        return jsonify({"status": 404, "msg": "No payment details found for this user"}), 404

    # Convert ObjectId and datetime fields for JSON serialization.
    for payment in payments:
        payment["_id"] = str(payment["_id"])
        if "created_at" in payment and isinstance(payment["created_at"], datetime):
            payment["created_at"] = payment["created_at"].isoformat()

    return jsonify({
        "status": 200,
        "msg": "Payment details retrieved successfully",
        "payments": payments
    }), 200






