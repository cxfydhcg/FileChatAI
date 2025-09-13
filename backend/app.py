
from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from routes import chatbot_api
from flask_cors import CORS
load_dotenv()
from utils.vector import create_vector_store
def create_app():
    app = Flask(__name__)
    CORS(app)
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.register_blueprint(chatbot_api.routes)

    return app




if __name__ == "__main__":
    app = create_app()
    
    files = ["customers.csv", "detail.csv", "pricelist.csv", "inventory.csv"]
    for file in files:
        create_vector_store(file)
    
    @app.route("/")
    def home():
        return "This is FileChatAI"
    # db = SQLAlchemy(app)
    app.run(host="0.0.0.0", port=int(os.getenv('PORT', 5000)), threaded=True, debug=True)