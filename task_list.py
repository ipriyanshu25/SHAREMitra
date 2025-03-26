from flask import Flask,request, jsonify , Blueprint
from pymongo import MongoClient
from datetime import datetime,timedelta
from bson.objectid import ObjectId
import re

task_list_bp = Blueprint("task", __name__)

client = MongoClient("mongodb://localhost:27017")
db = client['enoylity']

URL_REGEX = re.compile(
    r'^(https?:\/\/)?'  # http:// or https://
    r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,})'  # domain
    r'(:\d+)?(\/.'
    '*)?$'  # port and path
)

@task_list_bp.route("/display-message", methods=['POST'])
def display_message():
    data = request.get_json()
    title = data.get("title")
    message = data.get("message")
    task_link = data.get("link")
    if not message:
        return jsonify({"status": 0, "msg": "Message cannot be empty!", "class": "error"})
    if not task_link or not re.match(URL_REGEX, task_link):
        return jsonify({"status": 0, "msg": "Invalid URL format", "class": "error"})

    new_task ={
        "title" : title,
        "message" : message,
        "link" : task_link,
        "created_at":datetime.utcnow()
    }
    result = db.task.insert_one(new_task)
    if result.inserted_id:
        return jsonify({"status": 200, "msg": "Task message added succefylly"})
    else:
        return jsonify({"status": 404, "msg":"Failed to add Task"})




@task_list_bp.route("/tasks", methods=['GET'])
def get_tasks():
    """Retrieve tasks in reverse order (newest first) and mark new tasks (within last 72 hours)"""
    tasks = list(db.task.find().sort("created_at", -1))
    
    # Calculate the threshold datetime (72 hours ago)
    now = datetime.utcnow()
    threshold = now - timedelta(hours=72)
    
    task_list = [
        {
            "id": str(task["_id"]),  # Convert ObjectId to string
            "title": task["title"],
            "message": task["message"],
            "link": task["link"],
            "created_at": task["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
            "isNew": 1 if task["created_at"] >= threshold else 0
        }
        for task in tasks
    ]
    
    return jsonify({"status": 200, "tasks": task_list})

@task_list_bp.route("/delete/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        result = db.task.delete_one({"_id": ObjectId(task_id)})
        if result.deleted_count == 1:
            return jsonify({"status": 200, "msg": "Task deleted successfully"}), 200
        else:
            return jsonify({"status": 404, "msg": "Task not found"}), 404
    except Exception as e:
        return jsonify({"status": 500, "msg": f"Error deleting task: {str(e)}"}), 500


