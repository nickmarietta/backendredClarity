import os, json
from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
from google import genai
from google.genai import types
from flask_cors import CORS
from google.cloud import translate_v2 as translate

app = Flask(__name__)
CORS(app)
translate_client = translate.Client()

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
        system_instruction="You are RedClarity, an assistant specializing in PDF document analysis. Your responses must be "
        "formatted in simple, clean text that can be directly displayed in a SvelteKit application. When analyzing PDF content:"
        "1. Provide a brief 1-2 sentence summary of the document first"
        "2. Present your analysis as plain text with clear formatting:- Use simple bullet points (just "-" at the start of lines)- Avoid markdown formatting like bold, italics, or code blocks- Keep paragraphs short (3-4 lines maximum)- Use blank lines between sections"
        "3. Focus only on the most relevant information from the document"
        "4. Limit your response to the most important 3-5 key points"
        "5. Use simple, jargon-free language that anyone can understand"
        "Your response should be easily rendered in a SvelteKit text component without requiring special formatting or markdown processing.",
        response_mime_type="text/plain"
    ),
    contents=stringResult[1]
)
    questions = client.models.generate_content(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are a chatbot for the redClarity app. After scanning and analyzing the PDF document, provide the user "
        "with 4 relevant questions they might want to ask their physician or doctor based on the results. The questions should be "
        "simple, clear, and focused on key concerns that could be addressed in a medical setting.",
        response_mime_type="text/plain"
    ),
    contents=stringResult[1]
)

    print(response.text)
    return jsonify({"payload":  response.text }, {"questions": questions.text}), 200 

@app.route('/spanish', methods={'POST'})
def translateToSpanish():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': 'Missing text field'}), 400
    
    text = data['text']
    result = translate_client.translate(text, target_language='es')
    
    return jsonify({'translated_text': result['translatedText']}), 200

@app.route('/english', methods={'POST'})
def translateToEnglish():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': 'Missing text field'}), 400
    
    text = data['text']
    result = translate_client.translate(text, target_language='en')
    
    return jsonify({'translated_text': result['translatedText']}), 200

@app.route('/french', methods={'POST'})
def translateToFrench():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': 'Missing text field'}), 400
    
    text = data['text']
    result = translate_client.translate(text, target_language='fr')
    
    return jsonify({'translated_text': result['translatedText']}), 200

@app.route('/vietnamese', methods={'POST'})
def translateToVietnamese():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': 'Missing text field'}), 400
    
    text = data['text']
    result = translate_client.translate(text, target_language='vi')
    
    return jsonify({'translated_text': result['translatedText']}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))