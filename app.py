from flask import Flask
from flask_cors import CORS
from authentication import auth_bp
from task_list import task_list_bp    
# from image_analysis import image_analysis_bp  
from payment_details import payment_details_bp
from user import user_bp



app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(task_list_bp, url_prefix="/task")
# app.register_blueprint(image_analysis_bp, url_prefix="/image")
app.register_blueprint(payment_details_bp, url_prefix="/payment")
app.register_blueprint(user_bp, url_prefix="/user")

if __name__ == '__main__':
    app.run(debug=True)
