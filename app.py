from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
import re

from task_list import task_list_bp    # routes from task_list.py
from image_analysis import image_analysis_bp  # routes from image_analysis.py
from payment_details import payment_details_bp
app = Flask(__name__)

# Enable CORS
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["enolity"]

# Register blueprints so that the routes defined in the blueprints become active.
# You can also provide a URL prefix if you want.
app.register_blueprint(task_list_bp, url_prefix="/task")
app.register_blueprint(image_analysis_bp, url_prefix="/image")
app.register_blueprint(payment_details_bp, url_prefix="/payment")

@app.route("/login", methods=['POST'])
def login():
    input_data = request.get_json()
    email = input_data['email']
    password = input_data['password']
    
    # Retrieve the user by email
    user = db.useres.find_one({'email': email})
    
    # Check if user exists and verify the password
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({
            'status': 1,
            'msg': "User exists",
            'classs': "success",
            'user': user
        })
    else:
        return jsonify({
            'status': 0,
            'msg': "User not exists",
            'classs': "danger"
        })

@app.route("/register", methods=['POST'])
def register():
    input_data = request.get_json()
    
    name = input_data.get('fullName')
    email = input_data.get('email')
    phonenumber = input_data.get('phonenumber')
    password = input_data.get('password')

    # Validate phone number (10-digit numeric)
    if not re.fullmatch(r"\d{10}", phonenumber):
        return jsonify({
            'status': 0,
            'msg': "Phone number must be exactly 10 digits.",
            'class': "error"
        })

    # Validate password strength
    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,16}$", password):
        return jsonify({
            'status': 0,
            'msg': "Password must be 8-16 characters long, include uppercase, lowercase, a number, and a special character.",
            'class': "error"
        })

    if "gmail" in password.lower():
        return jsonify({
            'status': 0,
            'msg': "Password should not contain 'gmail'.",
            'class': "error"
        })

    # Check if the email is already registered
    existing_user = db.useres.find_one({'email': email})
    if existing_user:
        return jsonify({
            'status': 0,
            'msg': "User with this email already exists.",
            'class': "error"
        })

    # Limit registrations per phone number to 3
    email_count = db.useres.count_documents({'phonenumber': phonenumber})
    if email_count >= 3:
        return jsonify({
            'status': 0,
            'msg': "A maximum of 3 email addresses can be registered with this phone number.",
            'class': "error"
        })

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Assign a unique ID
    count = db.useres.count_documents({})
    new_user = {
        "_id": count + 1,
        "fullName": name,
        "email": email,
        "phonenumber": phonenumber,
        "password": hashed_password.decode('utf-8')
    }

    db.useres.insert_one(new_user)
    
    return jsonify({
        'status': 1,
        'msg': "User registered successfully",
        'class': "success"
    })

if __name__ == '__main__':
    app.run(debug=True)






# @app.route("/register", methods=['POST'])
# def register():
#     input_data = request.get_json()
    
#     name = input_data.get('fullName')
#     email = input_data.get('email')
#     phonenumber = input_data.get('phonenumber')
#     password = input_data.get('password')

#     if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,16}$", password):
#         return jsonify({
#             'status': 0,
#             'msg': "Password must be 8-16 characters long, include uppercase, lowercase, a number, and a special character.",
#             'class': "error"
#         })

#     if "gmail" in password.lower():
#         return jsonify({
#             'status': 0,
#             'msg': "Password should not contain 'gmail'.",
#             'class': "error"
#         })

#     user = db.useres.find_one({'email': email})
#     if user:
#         return jsonify({
#             'status': 0,
#             'msg': "User already exists",
#             'class': "error"
#         })

#     hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

#     count = db.useres.count_documents({})
#     new_user = {
#         "_id": count + 1,
#         "fullName": name,
#         "email": email,
#         "phonenumber": phonenumber,
#         "password": hashed_password.decode('utf-8')
#     }

#     db.useres.insert_one(new_user)
    
#     return jsonify({
#         'status': 1,
#         'msg': "User registered successfully",
#         'class': "success"
#     })