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
import glob
import time

# Add user site-packages to path to find openai module
import site
sys.path.append(site.getusersitepackages())

from openai import OpenAI

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Dictionary to track session files
session_files = {}

load_dotenv()
AIMLAPI_KEY = os.getenv('AIMLAPI_KEY')

# Periodic cleanup function to remove old files (can be called by a scheduler)
def cleanup_old_files():
    # Remove files older than 1 hour
    cutoff_time = time.time() - 3600
    
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                os.remove(file_path)
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

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

def extract_text_from_image(image_path):
    try:
        # Use OCR to extract text from the image
        text = pytesseract.image_to_string(image_path)
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
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get session ID from the request
    session_id = request.form.get('sessionId', 'default')
    
    # Create a unique filename with session ID to avoid conflicts
    original_filename = secure_filename(file.filename)
    filename = f"{session_id}_{int(time.time())}_{original_filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Track this file with the session
    if session_id not in session_files:
        session_files[session_id] = []
    session_files[session_id].append(file_path)
    
    # Check if the file is a PDF
    if original_filename.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
        return jsonify({'text': text, 'filename': filename, 'isImage': False})
    # Check if the file is an image
    elif any(original_filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']):
        text = extract_text_from_image(file_path)
        return jsonify({'text': text, 'filename': filename, 'isImage': True})
    else:
        # Remove the file if it's not a supported type
        os.remove(file_path)
        session_files[session_id].remove(file_path)
        return jsonify({'error': 'Invalid file type. Please upload a PDF or image file.'}), 400

@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    data = request.get_json()
    session_id = data.get('sessionId')
    
    if session_id and session_id in session_files:
        # Delete all files associated with this session
        for file_path in session_files[session_id]:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {str(e)}")
        
        # Clear the session files list
        session_files.pop(session_id, None)
    
    return jsonify({'success': True})

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
    # Clean up any existing files before starting
    cleanup_old_files()
    app.run(debug=True)