import json
import logging
from flask import request, jsonify
from cores.chatbot import  get_file_hint_stream_helper, get_answer_stream_helper
from flask import Blueprint



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/chatbot_api.log", mode="w")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

routes = Blueprint("chatbot_api", __name__, url_prefix="/api/chatbot")


@routes.route("get_answer_stream", methods=["POST"])
def get_answer_stream():
    try:
        data = request.form
        question = data.get("question", "").strip()
        if not question:
            return jsonify({"error": "Empty question"}), 400
        
        return get_answer_stream_helper(question)
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({"error": "Internal server error"}), 500

@routes.route("get_files_hint_stream", methods=["GET"])
def get_files_hint_stream():
    try:
        files_hint_stream = get_file_hint_stream_helper()
        logger.info(f"Files Hint: {files_hint_stream}")
        return files_hint_stream
    except Exception as e:
        logger.error(f"Error getting files hint: {e}")
        return jsonify({"error": "Internal server error"}), 500

