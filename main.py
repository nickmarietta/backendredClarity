import os, json
from flask import Flask, request
from PyPDF2 import PdfReader

app = Flask(__name__)

@app.route("/", methods={"GET"})
def hello_world():
    """Example Hello World route."""
    name = os.environ.get("NAME", "World")
    return f"Hello {name}!"

@app.route('/files', methods=['POST'])
def file_parser():
    try:
        
        if 'file' not in request.files:
            return {"error": "No file part in the request"}, 400

        file = request.files['file']
        

        if file.filename == '':
            return {"error": "No file selected"}, 400

        return {"filename": file.filename}, 200
        
    except Exception as e:
        app.logger.error(f"Error processing file: {str(e)}")
        return {"error": f"File processing error: {str(e)}"}, 500

@app.rout('/parse', methods={'POST'})
def parsing_file():
    try:
        
        if 'file' not in request.files:
            return {"error": "No file part in the request"}, 400

        file = request.files['file']
        

        if file.filename == '':
            return {"error": "No file selected"}, 400

        reader = PdfReader("EXAMPLEBLOODTEST.pdf")

        page = reader.pages[0]

        randomString = page.extract_text()
        stringResult = randomString.split("COMPREHENSIVE METABOLIC PANEL")
        print(stringResult[1])
        return {stringResult[1]}, 200
        
    except Exception as e:
        app.logger.error(f"Error processing file: {str(e)}")
        return {"error": f"File processing error: {str(e)}"}, 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))