import os
from PyPDF2 import PdfReader
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def hello_world():
    """Example Hello World route."""
    name = os.environ.get("NAME", "World")
    return f"Hello {name}!"

@app.route('/files', methods=['POST'])
def file_parser():
    data = request.files['file']
    return {data.filename}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))