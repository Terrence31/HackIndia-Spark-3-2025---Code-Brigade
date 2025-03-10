from flask import Flask
from flask_cors import CORS
from flask import request, jsonify
import json
import os
from ragchat.app import ragchat_pipeline, response

app = Flask(__name__)
CORS(app)

file = "C:/Users/Samuel Mesquita/Downloads/CV-Bu6JGepv.pdf"
ragchat_chain = ragchat_pipeline(file)


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
    

if __name__ == '__main__':
    app.run(debug=True, port=8888)
    