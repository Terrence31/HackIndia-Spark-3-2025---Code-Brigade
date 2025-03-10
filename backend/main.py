import flask as Flask
from flask_cors import CORS
from flask import request, jsonify
import json
import os
from ragchat.app import ragchat_pipeline, response

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploaded_docs"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ragchat_chain = ragchat_pipeline()


@app.route('/ragchat', methods=['POST'])
def query():
    try:
        data = request.json
        query = data.get('query')
        if not query:
            return jsonify({'error': 'Query Not Provided'}), 400
        answer = response(query, ragchat_chain)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    