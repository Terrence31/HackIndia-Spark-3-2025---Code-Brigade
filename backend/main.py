from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from io import BytesIO  

from summarise.app import summarize_document, translate_text, load_document

app = Flask(__name__)
CORS(app)

# Route to summarize a document (file or directory)
@app.route("/summarize", methods=["POST"])
def summarize():
    file_path = request.files.get("file_path")

    try:
        if file_path:
            file_content = file_path.read()
            temp_file = BytesIO(file_content)  
            summary = summarize_document(load_document(temp_file))    

        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to translate summarized text
@app.route("/translate", methods=["POST"])
def translate():
    data = request.json
    text = data.get("text")
    source_lang = data.get("source_lang")
    target_lang = data.get("target_lang")

    try:
        translated_text = translate_text(text, source_lang, target_lang)
        return jsonify({
            "translated_text": translated_text,
            "source_language": source_lang,
            "target_language": target_lang
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
