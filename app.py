from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import requests
import json
import sys

# Add user site-packages to path to find openai module
import site
sys.path.append(site.getusersitepackages())

from openai import OpenAI

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

load_dotenv()
AIMLAPI_KEY = os.getenv('AIMLAPI_KEY')

def extract_text_from_pdf(pdf_path):
    try:
        # Try extracting text directly
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
            if text.strip():
                return text
    except Exception:
        pass

    # Fallback to OCR if direct extraction fails
    try:
        images = convert_from_path(pdf_path)
        text = ''
        for image in images:
            text += pytesseract.image_to_string(image) + '\n'
        return text
    except Exception as e:
        return f"Error during OCR: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('js', filename)

@app.route('/uploads/<path:filename>')
def serve_pdf(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        text = extract_text_from_pdf(file_path)
        return jsonify({'text': text, 'filename': filename})
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    query = data.get('query')
    context = data.get('context')
    if not query or not context:
        return jsonify({'error': 'Query and context required'}), 400

    try:
        client = OpenAI(
            base_url="https://api.aimlapi.com/v1",
            api_key=AIMLAPI_KEY,
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided PDF content."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
            ]
        )
        
        answer = response.choices[0].message.content
        return jsonify({'answer': answer})
    except Exception as e:
        # Fallback to local processing if API fails
        print(f"API error: {str(e)}")
        
        # Simple keyword-based response
        context_lower = context.lower()
        query_lower = query.lower()
        
        # Extract relevant sentences from context that might contain answer
        sentences = context.replace('\n', ' ').split('.')
        relevant_sentences = []
        
        # Find sentences that contain words from the query
        query_words = set(query_lower.split())
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_lower = sentence.lower()
            matching_words = sum(1 for word in query_words if word in sentence_lower)
            
            if matching_words > 0:
                relevant_sentences.append(sentence)
        
        if relevant_sentences:
            # Construct a response using the most relevant sentences
            answer = f"Based on the document, I found these relevant details: {'. '.join(relevant_sentences[:3])}."
        else:
            # Generic response if no relevant sentences found
            answer = f"I've reviewed the document but couldn't find specific information about '{query}'. The document appears to be about {' '.join(context.split()[:20])}..."
        
        return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)