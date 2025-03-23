import os, json
from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
from google import genai
from google.genai import types
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
import re

app = Flask(__name__)

def get_document_ai_client(location: str):
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    return documentai.DocumentProcessorServiceClient(client_options=opts)

def remove_personal_information(pdf_name):
    pdf_name = re.sub(r'\b(?:Name|Date|Medical Record|SSN):?\s*\w+\b', '[REDACTED]', pdf_name)
    return pdf_name

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
    
@app.route('/gemini', methods={'POST'})
def gemini_call(): 

    file = request.files['file']

    if file.filename == '':
        return {"error": "No file selected"}, 400

    reader = PdfReader(file)

    page = reader.pages[0]

    randomString = page.extract_text()
    stringResult = randomString.split("COMPREHENSIVE METABOLIC PANEL")

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction="These are the results from a blood test, could you filter all of the /n and give a basic summary of what the results mean (explain like im a 4th grader)."
        ),
        contents=stringResult[1]
    )

    print(response.text)
    return jsonify({"payload":  response.text }), 200 

app.route('/improvisedparse', methods={'POST'})
def improvisedParse():

    # Check if file is in the request
    if 'file' not in request.files:
        return {"error": "No file part in the request"}, 400

    file = request.files['file']
    
    if file.filename == '':
        return {"error": "No file selected"}, 400

    # Document AI parameters
    project_id = os.environ['GOOGLE_CLOUD_PROJECT_ID']
    location = "us"
    processor_display_name = "My Processor"

    client = get_document_ai_client(location)

    parent = client.common_location_path(project_id, location)

    processor = client.create_processor(
        parent=parent,
        processor=documentai.Processor(
            type_="OCR_PROCESSOR",
            display_name=processor_display_name,
        ),
    )
    print(f"Processor Name: {processor.name}")

    file_content = file.read()

    raw_document = documentai.RawDocument(
        content=file_content,
        mime_type="application/pdf",
    )

    request = documentai.ProcessRequest(name=processor.name, raw_document=raw_document)

    result = client.process_document(request=request)
    document = result.document

    extracted_text = document.text

    cleaned_text = remove_personal_information(extracted_text)

    gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        config=genai.types.GenerateContentConfig(
            system_instruction="These are the results from a blood test. Could you filter all of the '/n' and give a basic summary of what the results mean? (Explain like I'm a 4th grader)."
        ),
        contents=cleaned_text
    )

    print(response.text)
    return jsonify({"payload": response.text}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))