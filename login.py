from flask import Flask, request, jsonify
import requests
import random
import datetime
import os

app = Flask(__name__)

# In-memory store for OTPs.
# In production, use a persistent storage like Redis or a database.
otp_store = {}

def generate_otp(length=4):
    """Generate a numeric OTP of a given length."""
    return ''.join(random.choices("0123456789", k=length))

@app.route('/login', methods=['POST'])
def send_otp():
    """
    Expects a JSON payload:
    {
        "phone": "10-digit number"
    }
    This endpoint generates an OTP, saves it with a 5-minute expiry, and sends it via Fast2SMS.
    """
    data = request.get_json() or {}
    phone = data.get("phone")
    if not phone:
        return jsonify({"error": "Phone number is required."}), 400

    # Generate OTP and set expiry (5 minutes from now)
    otp = generate_otp(4)
    expiry_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    otp_store[phone] = {"otp": otp, "expires": expiry_time}

    # Prepare Fast2SMS API request
    url = "https://www.fast2sms.com/dev/bulkV2"
    api_key = os.environ.get("FAST2SMS_API_KEY", "30YlkFZVrtRHCnOIs7PDUajxwEB4evX1SfmW8cMQiGJhLTpbz6FaB3tfYDXniMQNkThgoylJPA8VH15E")
    # The payload sets 'variables_values' to the OTP and sends it to the given phone number.
    payload = f"variables_values={otp}&route=otp&numbers={phone}"
    headers = {
        'authorization': api_key,
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
    }
    
    try:
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code != 200:
            return jsonify({"error": f"Failed to send OTP: {response.text}"}), 500
    except Exception as e:
        return jsonify({"error": f"Exception occurred: {str(e)}"}), 500

    return jsonify({"message": "OTP sent successfully."}), 200

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    """
    Expects a JSON payload:
    {
        "phone": "10-digit number",
        "otp": "the received OTP"
    }
    This endpoint validates the OTP. If correct and not expired, it returns a successful login message.
    """
    data = request.get_json() or {}
    phone = data.get("phone")
    user_otp = data.get("otp")
    if not phone or not user_otp:
        return jsonify({"error": "Phone number and OTP are required."}), 400

    record = otp_store.get(phone)
    if not record:
        return jsonify({"error": "OTP not found for this phone number."}), 404

    # Check if the OTP has expired
    if datetime.datetime.utcnow() > record["expires"]:
        return jsonify({"error": "OTP has expired."}), 400

    if user_otp == record["otp"]:
        # Successful OTP verification; remove the OTP record.
        otp_store.pop(phone)
        return jsonify({"message": "Logged in successfully."}), 200
    else:
        return jsonify({"error": "Invalid OTP."}), 400

if __name__ == '__main__':
    app.run(debug=True)
