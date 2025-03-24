# # from flask import Flask, request, jsonify
# # import pytesseract
# # from PIL import Image
# # import os

# # app = Flask(__name__)

# # # Set Tesseract path if necessary (for Windows)
# # # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# # UPLOAD_FOLDER = "uploads"
# # os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure upload folder exists
# # app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# # @app.route("/upload-image", methods=['POST'])
# # def upload_image():
# #     """Endpoint to upload an image and extract text using Tesseract OCR."""
# #     if "image" not in request.files:
# #         return jsonify({"status": 0, "msg": "No image file provided", "class": "error"})

# #     file = request.files["image"]

# #     if file.filename == "":
# #         return jsonify({"status": 0, "msg": "No selected file", "class": "error"})

# #     # Save the file
# #     filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
# #     file.save(filepath)

# #     # Process the image with Tesseract OCR
# #     try:
# #         image = Image.open(filepath)
# #         extracted_text = pytesseract.image_to_string(image)  # Default language: English

# #         return jsonify({
# #             "status": 1,
# #             "msg": "Text extracted successfully",
# #             "extracted_text": extracted_text.strip(),
# #             "class": "success"
# #         })
    
# #     except Exception as e:
# #         return jsonify({"status": 0, "msg": str(e), "class": "error"})
    
# # @app.route("/test-message", methods=['POST'])
# # def test_message():
# #     """Tests the text comparison logic separately."""
# #     data = request.get_json()
# #     input_text = data.get("text1", "").strip().lower()
# #     extracted_text = data.get("text2", "").strip().lower()

# #     if not input_text or not extracted_text:
# #         return jsonify({"status": 0, "msg": "Both text1 and text2 are required", "class": "error"})

# #     # Compare texts
# #     if input_text == extracted_text:
# #         return jsonify({"status": 1, "msg": "Text matched!", "class": "success"})
# #     else:
# #         return jsonify({"status": 0, "msg": "Text did not match!", "class": "error"})


# # from flask import Flask, request, jsonify
# # import pytesseract
# # from PIL import Image
# # import os

# # app = Flask(__name__)

# # # Set Tesseract path if necessary (for Windows)
# # # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# # UPLOAD_FOLDER = "uploads"
# # os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure upload folder exists
# # app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# # # ✅ **Predefined Text for Matching**
# # PREDEFINED_TEXT = "This is test message"

# # @app.route("/upload-image", methods=['POST'])
# # def upload_image():
# #     """Uploads an image, extracts text using Tesseract OCR, and compares with a predefined text."""
# #     if "image" not in request.files:
# #         return jsonify({"status": 0, "msg": "No image file provided", "class": "error"})

# #     file = request.files["image"]

# #     if file.filename == "":
# #         return jsonify({"status": 0, "msg": "No selected file", "class": "error"})

# #     # Save the file
# #     filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
# #     file.save(filepath)

# #     # Process the image with Tesseract OCR
# #     try:
# #         image = Image.open(filepath)
# #         extracted_text = pytesseract.image_to_string(image).strip().lower()  # Extracted text

# #         # ✅ **Compare Extracted Text with Predefined Text**
# #         if extracted_text == PREDEFINED_TEXT.lower():
# #             return jsonify({
# #                 "status": 1,
# #                 "msg": "Text matched!",
# #                 "extracted_text": extracted_text,
# #                 "class": "success"
# #             })
# #         else:
# #             return jsonify({
# #                 "status": 0,
# #                 "msg": "Text did not match!",
# #                 "extracted_text": extracted_text,
# #                 "expected_text": PREDEFINED_TEXT,
# #                 "class": "error"
# #             })

# #     except Exception as e:
# #         return jsonify({"status": 0, "msg": str(e), "class": "error"})








# from flask import Flask, request, jsonify
# import pytesseract
# from PIL import Image
# import os
# from fuzzywuzzy import fuzz  

# app = Flask(__name__)

# # Set Tesseract path if necessary (for Windows)
# # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure upload folder exists
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# PREDEFINED_TEXT = "this is a test message!"

# @app.route("/upload-image", methods=['POST'])
# def upload_image():
#     """Uploads an image, extracts text using Tesseract OCR, and checks if it matches at least 90%."""
#     if "image" not in request.files:
#         return jsonify({"status": 0, "msg": "No image file provided", "class": "error"})

#     file = request.files["image"]

#     if file.filename == "":
#         return jsonify({"status": 0, "msg": "No selected file", "class": "error"})

#     # Save the file
#     filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
#     file.save(filepath)

#     # Process the image with Tesseract OCR
#     try:
#         image = Image.open(filepath)
#         extracted_text = pytesseract.image_to_string(image).strip().lower()  # Extracted text

#         # ✅ **Calculate similarity percentage**
#         match_percentage = fuzz.ratio(extracted_text, PREDEFINED_TEXT.lower())  # Compare texts

#         # ✅ **Allow match if similarity is 75% or more**
#         if match_percentage >= 75:
#             return jsonify({
#                 "status": 1,
#                 "msg": "Text matched!",
#                 "extracted_text": extracted_text,
#                 "match_percentage": match_percentage,
#                 "class": "success"
#             })
#         else:
#             return jsonify({
#                 "status": 0,
#                 "msg": "Text did not match!",
#                 "extracted_text": extracted_text,
#                 "expected_text": PREDEFINED_TEXT,
#                 "match_percentage": match_percentage,
#                 "class": "error"
#             })

#     except Exception as e:
#         return jsonify({"status": 0, "msg": str(e), "class": "error"})


# if __name__ == "__main__":
#     app.run(debug=True)











# # from flask import Flask, request, jsonify, Blueprint
# # from pymongo import MongoClient
# # from PIL import Image
# # import pytesseract
# # import io

# # image_analysis_bp = Blueprint("image_analysis", __name__)

# # # Connect to MongoDB (same database as task_list.py)
# # client = MongoClient("mongodb://localhost:27017") 
# # db = client.task_manager
# # tasks_collection = db.tasks

# # @image_analysis_bp.route("/validate-images", methods=["POST"])
# # def validate_images():
# #     # Ensure both images are provided
# #     if "shared_message" not in request.files or "group_members" not in request.files:
# #         return jsonify({
# #             "status": 0, 
# #             "msg": "Both shared_message and group_members images are required", 
# #             "class": "error"
# #         }), 400

# #     shared_file = request.files["shared_message"]
# #     members_file = request.files["group_members"]

# #     # Process the shared message image
# #     try:
# #         shared_img = Image.open(shared_file.stream)
# #     except Exception:
# #         return jsonify({
# #             "status": 0, 
# #             "msg": "Shared message image is not correct", 
# #             "class": "error"
# #         }), 400

# #     extracted_shared_text = pytesseract.image_to_string(shared_img)

# #     # Process the group members image
# #     try:
# #         members_img = Image.open(members_file.stream)
# #     except Exception:
# #         return jsonify({
# #             "status": 0, 
# #             "msg": "Group members image is not correct", 
# #             "class": "error"
# #         }), 400

# #     extracted_members_text = pytesseract.image_to_string(members_img)

# #     # Retrieve the most recent task from MongoDB (expected shared message)
# #     recent_task = tasks_collection.find_one(sort=[("created_at", -1)])
# #     if not recent_task:
# #         return jsonify({
# #             "status": 0, 
# #             "msg": "No task available", 
# #             "class": "error"
# #         }), 404 

# #     expected_task = recent_task["message"]
# #     #expected_task = "This is a test message"


# #     # Validate shared message image: expected task should appear in the extracted text
# #     shared_valid = expected_task in extracted_shared_text

# #     # Validate group members image: extract digits and compare with a threshold
# #     digits = "".join(filter(str.isdigit, extracted_members_text))
# #     group_count = None
# #     if digits:
# #         try:
# #             group_count = int(digits)
# #             # Define a threshold (adjust as needed)
# #             expected_group_threshold = 250
# #             members_valid = group_count >= expected_group_threshold
# #         except ValueError:
# #             members_valid = False
# #     else:
# #         members_valid = False

# #     # Final validation: both images must pass their checks
# #     result = 1 if shared_valid and members_valid else 0

# #     return jsonify({
# #         "status": 200,
# #         "result": result,
# #         "expected_task": expected_task,
# #         "extracted_shared_text": extracted_shared_text,
# #         "group_count": group_count,
# #         "members_valid": members_valid
# #     })








from flask import Flask, request, jsonify
import os
import base64
from werkzeug.utils import secure_filename
import requests
import json

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# OpenAI API key (Replace with a new, valid key)
OPENAI_API_KEY = "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"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def encode_image_to_base64(image_path):
    """Encode image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_image_with_openai(image_path, expected_link):
    try:
        base64_image = encode_image_to_base64(image_path)

        prompt = f"""
        Analyze this image and determine if it's a screenshot of a WhatsApp broadcast message.

        Specifically check for:
        1. Is this clearly a WhatsApp interface?
        2. Does the screenshot contain this exact link or URL: '{expected_link}'?
        3. What is the timestamp or time of the message (if visible)?

        Format your response as JSON with these fields:
        - is_whatsapp_screenshot (boolean)
        - contains_expected_link (boolean)
        - timestamp (string, format as shown in image)
        - confidence_score (1-10)
        - reason (brief explanation)
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            "max_tokens": 500
        }

        response = requests.post(OPENAI_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            assistant_content = result["choices"][0]["message"]["content"]
            
            try:
                content = json.loads(assistant_content)
            except json.JSONDecodeError:
                return {
                    "verified": False,
                    "message": "OpenAI response is not valid JSON",
                    "details": assistant_content
                }

            verified = content.get("is_whatsapp_screenshot", False) and content.get("contains_expected_link", False)

            return {
                "verified": verified,
                "message": "Image analyzed successfully",
                "details": content
            }
        else:
            return {
                "verified": False,
                "message": f"API Error: {response.status_code}",
                "details": response.text
            }

    except Exception as e:
        return {"verified": False, "message": f"Error processing image: {str(e)}"}


@app.route('/api/verify', methods=['POST'])
def verify_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No image selected"}), 400

    expected_link = request.form.get('expected_link', '')
    if not expected_link:
        return jsonify({"error": "Expected link not provided"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        result = analyze_image_with_openai(file_path, expected_link)

        return jsonify(result)
    else:
        return jsonify({"error": "File type not allowed"}), 400


@app.route('/api/check_openai_key', methods=['GET'])
def check_openai_api_key():
    """Check if the OpenAI API key is valid and working"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Test message to check API functionality."}
            ],
            "max_tokens": 20
        }

        response = requests.post(OPENAI_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return jsonify({"status": "success", "message": "OpenAI API key is working"}), 200
        else:
            return jsonify({"status": "error", "message": f"API Error: {response.status_code}", "details": response.text}), response.status_code

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error checking API key: {str(e)}"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API is running"})