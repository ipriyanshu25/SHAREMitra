import os
import base64
import re
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, Blueprint
from werkzeug.utils import secure_filename
from pymongo import MongoClient

image_analysis_bp = Blueprint('image_analysis', __name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# OpenAI API key (replace this with a valid key in production)
OPENAI_API_KEY = "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"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client['enoylity']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_recent_task_links(days=3):
    try:
        threshold_date = datetime.utcnow() - timedelta(days=days)
        recent_tasks = db.task.find({"created_at": {"$gte": threshold_date}}).sort("created_at", -1)
        links = [task["link"] for task in recent_tasks if "link" in task]
        return links
    except Exception as e:
        print(f"Error fetching recent task links: {str(e)}")
        return []


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

            assistant_content_clean = re.sub(r"```(?:json)?", "", assistant_content).replace("```", "").strip()

            try:
                content = json.loads(assistant_content_clean)
            except json.JSONDecodeError:
                return {
                    "verified": False,
                    "message": "OpenAI response is not valid JSON",
                    "details": assistant_content
                }

            verified = (
                content.get("is_whatsapp_screenshot", False)
                and content.get("contains_expected_link", False)
            )

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
        return {
            "verified": False,
            "message": f"Error processing image: {str(e)}"
        }


@image_analysis_bp.route('/api/verify', methods=['POST'])
def verify_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No image selected"}), 400

    if not file or not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    recent_links = get_recent_task_links(days=3)
    if not recent_links:
        return jsonify({"error": "No recent task links available"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    for link in recent_links:
        result = analyze_image_with_openai(file_path, link)
        if result.get("verified"):
            return jsonify({
                "verified": True,
                "matched_link": link,
                "details": result.get("details", {})
            }), 200

    return jsonify({
        "verified": False,
        "message": "No matching link found in the image"
    }), 200



@image_analysis_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API is running"})





# import base64
# import re
# import json
# import requests
# from datetime import datetime, timedelta
# from flask import Flask, request, jsonify, Blueprint
# from pymongo import MongoClient

# image_analysis_bp = Blueprint('image_analysis', __name__)

# # Allowed file extensions
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# # OpenAI API key (replace this with a valid key in production)
# OPENAI_API_KEY = "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"
# OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# # MongoDB connection
# client = MongoClient("mongodb://localhost:27017")
# db = client['enoylity']

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def get_recent_task_links(days=3):
#     try:
#         threshold_date = datetime.utcnow() - timedelta(days=days)
#         recent_tasks = db.task.find({"created_at": {"$gte": threshold_date}}).sort("created_at", -1)
#         links = [task["link"] for task in recent_tasks if "link" in task]
#         return links
#     except Exception as e:
#         print(f"Error fetching recent task links: {str(e)}")
#         return []

# def analyze_image_with_openai_base64(base64_image, expected_link):
#     try:
#         prompt = f"""
#         Analyze this image and determine if it's a screenshot of a WhatsApp broadcast message.

#         Specifically check for:
#         1. Is this clearly a WhatsApp interface?
#         2. Does the screenshot contain this exact link or URL: '{expected_link}'?
#         3. What is the timestamp or time of the message (if visible)?

#         Format your response as JSON with these fields:
#         - is_whatsapp_screenshot (boolean)
#         - contains_expected_link (boolean)
#         - timestamp (string, format as shown in image)
#         - confidence_score (1-10)
#         - reason (brief explanation)
#         """

#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {OPENAI_API_KEY}"
#         }

#         payload = {
#             "model": "gpt-4o",
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": [
#                         {"type": "text", "text": prompt},
#                         {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
#                     ]
#                 }
#             ],
#             "max_tokens": 500
#         }

#         response = requests.post(OPENAI_API_URL, headers=headers, json=payload)

#         if response.status_code == 200:
#             result = response.json()
#             assistant_content = result["choices"][0]["message"]["content"]

#             assistant_content_clean = re.sub(r"```(?:json)?", "", assistant_content).replace("```", "").strip()

#             try:
#                 content = json.loads(assistant_content_clean)
#             except json.JSONDecodeError:
#                 return {
#                     "verified": False,
#                     "message": "OpenAI response is not valid JSON",
#                     "details": assistant_content
#                 }

#             verified = (
#                 content.get("is_whatsapp_screenshot", False)
#                 and content.get("contains_expected_link", False)
#             )

#             return {
#                 "verified": verified,
#                 "message": "Image analyzed successfully",
#                 "details": content
#             }
#         else:
#             return {
#                 "verified": False,
#                 "message": f"API Error: {response.status_code}",
#                 "details": response.text
#             }

#     except Exception as e:
#         return {
#             "verified": False,
#             "message": f"Error processing image: {str(e)}"
#         }

# def analyze_participant_image_base64(base64_image):
#     try:
#         prompt = """
#         Analyze this image and extract the number of participants shown in a WhatsApp group or broadcast list.

#         Respond with the following JSON format:
#         - participant_count (integer)
#         - is_valid_participant_count (boolean, true if >= 100)
#         - confidence_score (1-10)
#         - reason (brief explanation)
#         """

#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {OPENAI_API_KEY}"
#         }

#         payload = {
#             "model": "gpt-4o",
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": [
#                         {"type": "text", "text": prompt},
#                         {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
#                     ]
#                 }
#             ],
#             "max_tokens": 300
#         }

#         response = requests.post(OPENAI_API_URL, headers=headers, json=payload)

#         if response.status_code == 200:
#             result = response.json()
#             assistant_content = result["choices"][0]["message"]["content"]
#             assistant_content_clean = re.sub(r"```(?:json)?", "", assistant_content).replace("```", "").strip()
#             try:
#                 return json.loads(assistant_content_clean)
#             except json.JSONDecodeError:
#                 return {
#                     "is_valid_participant_count": False,
#                     "message": "OpenAI response is not valid JSON",
#                     "details": assistant_content
#                 }
#         else:
#             return {
#                 "is_valid_participant_count": False,
#                 "message": f"API Error: {response.status_code}",
#                 "details": response.text
#             }

#     except Exception as e:
#         return {
#             "is_valid_participant_count": False,
#             "message": f"Error analyzing participant image: {str(e)}"
#         }

# @image_analysis_bp.route('/api/verify', methods=['POST'])
# def verify_image():
#     if 'message_image' not in request.files or 'participant_image' not in request.files:
#         return jsonify({"error": "Both message_image and participant_image are required"}), 400

#     message_file = request.files['message_image']
#     participant_file = request.files['participant_image']

#     if message_file.filename == '' or participant_file.filename == '':
#         return jsonify({"error": "Both images must be selected"}), 400

#     if not (allowed_file(message_file.filename) and allowed_file(participant_file.filename)):
#         return jsonify({"error": "File type not allowed"}), 400

#     # Read files as base64
#     message_image_base64 = base64.b64encode(message_file.read()).decode('utf-8')
#     participant_image_base64 = base64.b64encode(participant_file.read()).decode('utf-8')

#     # Get recent links
#     recent_links = get_recent_task_links(days=3)
#     if not recent_links:
#         return jsonify({"error": "No recent task links available"}), 400

#     for link in recent_links:
#         result = analyze_image_with_openai_base64(message_image_base64, link)
#         if result.get("verified"):
#             participant_result = analyze_participant_image_base64(participant_image_base64)
#             if participant_result.get("is_valid_participant_count"):
#                 return jsonify({
#                     "verified": True,
#                     "matched_link": link,
#                     "details": {
#                         "message_verification": result.get("details", {}),
#                         "participant_verification": participant_result
#                     }
#                 }), 200
#             else:
#                 return jsonify({
#                     "verified": False,
#                     "message": "Participant count less than 100",
#                     "details": participant_result
#                 }), 200

#     return jsonify({
#         "verified": False,
#         "message": "No matching link found in the message image"
#     }), 200

# @image_analysis_bp.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({"status": "healthy", "message": "API is running"})
