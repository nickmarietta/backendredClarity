import os, json
from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
from google import genai
from google.genai import types

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

@app.route('/parse', methods={'POST'})
def parsing_file():
    try:
        
        if 'file' not in request.files:
            return {"error": "No file part in the request"}, 400

        file = request.files['file']
        

        if file.filename == '':
            return {"error": "No file selected"}, 400

        reader = PdfReader(file)

        page = reader.pages[0]

        randomString = page.extract_text()
        stringResult = randomString.split("COMPREHENSIVE METABOLIC PANEL")
        print(stringResult[1])
        return jsonify({"payload":  stringResult[1] }), 200 
        
    except Exception as e:
        app.logger.error(f"Error processing file: {str(e)}")
        return {"error": f"File processing error: {str(e)}"}, 500
    
@app.route('/gemini', methods={'GET'})
def gemini_call():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction="say hi who."
        ),
        contents="Hello there"
    )

    print(response.text)
    return jsonify({"payload":  response.text }), 200 

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))