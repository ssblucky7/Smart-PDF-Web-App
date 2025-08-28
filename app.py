"""
Smart PDF Q&A System - Production Ready Application
Secure Flask application for PDF text extraction and AI-powered Q&A
"""
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join
import os
import logging
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import time
import re
from collections import Counter
from markupsafe import escape

# Configure secure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Flask app configuration
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE', '16777216'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise ValueError("SECRET_KEY environment variable is required")

# Ensure upload directory exists
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except OSError as e:
    logger.error(f"Failed to create upload directory: {e}")
    raise

# Security constants
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
MAX_CONTEXT_LENGTH = 2000
MAX_PAGES_OCR = 10

# Session storage (in production, use Redis or database)
session_files = {}
session_content = {}

class SecureQASystem:
    """Secure Q&A system with proper error handling and validation"""
    
    def __init__(self):
        """Initialize HF client with proper error handling"""
        try:
            hf_token = os.getenv('HF_TOKEN')
            if not hf_token:
                raise ValueError("HF_TOKEN environment variable is required")
            
            logger.info("Initializing Hugging Face client")
            self.client = InferenceClient(token=hf_token)
            logger.info("HF client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize HF client: {e}")
            self.client = None
    
    def _sanitize_text(self, text):
        """Sanitize text input to prevent XSS"""
        if not isinstance(text, str):
            return ""
        return escape(text.strip())
    
    def _extract_sentences(self, text):
        """Extract sentences with proper validation"""
        if not text or not isinstance(text, str):
            return []
        
        sentences = re.split(r'[.!?\n]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _find_relevant_content(self, query, context):
        """Find relevant content using secure keyword matching"""
        if not query or not context:
            return []
        
        sentences = self._extract_sentences(context)
        if not sentences:
            return []
        
        query_words = set(query.lower().split())
        scored_sentences = []
        
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            score = len(query_words & sentence_words)
            if score > 0:
                scored_sentences.append((score, sentence))
        
        scored_sentences.sort(reverse=True)
        return [sent for _, sent in scored_sentences[:3]]
    
    def generate_answer(self, query, context):
        """Generate secure answer with proper validation"""
        if not query or not context:
            return "Invalid input provided"
        
        # Sanitize inputs
        query = self._sanitize_text(query)
        context = context[:MAX_CONTEXT_LENGTH] if len(context) > MAX_CONTEXT_LENGTH else context
        
        # Try HF API first
        if self.client:
            try:
                result = self.client.question_answering(
                    question=query,
                    context=context,
                    model="distilbert/distilbert-base-cased-distilled-squad"
                )
                
                if isinstance(result, dict) and 'answer' in result:
                    answer = self._sanitize_text(result['answer'])
                    logger.info(f"HF API success - Score: {result.get('score', 0)}")
                    return answer
                    
            except Exception as e:
                logger.warning(f"HF API failed: {e}")
        
        # Fallback to local processing
        return self._generate_local_answer(query, context)
    
    def _generate_local_answer(self, query, context):
        """Generate answer using local processing with enhanced reasoning"""
        logger.info("Using local fallback system")
        
        relevant_sentences = self._find_relevant_content(query, context)
        if not relevant_sentences:
            return "No relevant information found in the document"
        
        query_lower = query.lower()
        primary_sentence = self._sanitize_text(relevant_sentences[0])
        
        # Enhanced reasoning based on question type
        if any(word in query_lower for word in ['what', 'define']):
            return f"According to the document: {primary_sentence}"
        elif any(word in query_lower for word in ['how', 'process']):
            return f"The process described is: {primary_sentence}"
        elif any(word in query_lower for word in ['why', 'reason']):
            return f"The explanation provided is: {primary_sentence}"
        elif any(word in query_lower for word in ['when', 'where', 'who']):
            return f"Based on the document: {primary_sentence}"
        else:
            return f"From the document: {primary_sentence}"

# Initialize QA system
qa_system = SecureQASystem()

def secure_cleanup_files():
    """Secure file cleanup with proper error handling"""
    cutoff_time = time.time() - 3600
    
    try:
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            return
            
        for filename in os.listdir(upload_folder):
            file_path = safe_join(upload_folder, filename)
            if not file_path:
                continue
                
            try:
                if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                    os.remove(file_path)
                    logger.info(f"Cleaned up old file: {filename}")
            except OSError as e:
                logger.warning(f"Failed to remove file {filename}: {e}")
                
    except OSError as e:
        logger.error(f"Cleanup error: {e}")

def secure_extract_pdf_text(pdf_path):
    """Secure PDF text extraction with proper error handling"""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError("PDF file not found")
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text_parts = []
            
            for page in reader.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    logger.warning(f"Failed to extract text from page: {e}")
                    continue
            
            if text_parts:
                return '\n'.join(text_parts)
                
    except PyPDF2.errors.PdfReadError as e:
        logger.warning(f"PDF read error: {e}")
    except Exception as e:
        logger.error(f"Unexpected PDF error: {e}")
    
    # OCR fallback with memory optimization
    try:
        images = convert_from_path(pdf_path, first_page=1, last_page=MAX_PAGES_OCR)
        text_parts = []
        
        for image in images:
            try:
                text = pytesseract.image_to_string(image)
                if text.strip():
                    text_parts.append(text)
            except pytesseract.TesseractError as e:
                logger.warning(f"OCR error: {e}")
                continue
        
        return '\n'.join(text_parts) if text_parts else "No text could be extracted"
        
    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        return "Text extraction failed"

def secure_extract_image_text(image_path):
    """Secure image text extraction"""
    if not os.path.exists(image_path):
        raise FileNotFoundError("Image file not found")
    
    try:
        return pytesseract.image_to_string(image_path)
    except pytesseract.TesseractError as e:
        logger.error(f"Tesseract error: {e}")
        return f"OCR processing failed: {e}"
    except Exception as e:
        logger.error(f"Image processing error: {e}")
        return "Image processing failed"

@app.before_request
def log_request():
    """Log incoming requests securely"""
    logger.info(f"Request: {request.method} {request.endpoint} - IP: {request.remote_addr}")

@app.after_request
def log_response(response):
    """Log responses securely"""
    logger.info(f"Response: {response.status_code} - {request.method} {request.endpoint}")
    return response

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files securely"""
    safe_path = safe_join('js', secure_filename(filename))
    if safe_path and os.path.exists(safe_path):
        return send_from_directory('js', secure_filename(filename))
    logger.warning(f"Attempted access to invalid JS file: {filename}")
    return "File not found", 404

@app.route('/uploads/<path:filename>')
def serve_file(filename):
    """Serve uploaded files securely"""
    safe_filename = secure_filename(filename)
    safe_path = safe_join(app.config['UPLOAD_FOLDER'], safe_filename)
    
    if safe_path and os.path.exists(safe_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], safe_filename)
    
    logger.warning(f"Attempted access to invalid file: {filename}")
    return "File not found", 404

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle secure file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate session ID
        session_id = request.form.get('sessionId', '').strip()
        if not session_id or not re.match(r'^[a-zA-Z0-9_-]{10,50}$', session_id):
            return jsonify({'error': 'Invalid session ID'}), 400
        
        # Secure filename handling
        original_filename = secure_filename(file.filename)
        if not original_filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        file_ext = os.path.splitext(original_filename.lower())[1]
        if file_ext not in ALLOWED_EXTENSIONS:
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Create secure file path
        timestamp = int(time.time())
        filename = f"{session_id}_{timestamp}_{original_filename}"
        file_path = safe_join(app.config['UPLOAD_FOLDER'], filename)
        
        if not file_path:
            return jsonify({'error': 'Invalid file path'}), 400
        
        # Save file securely
        file.save(file_path)
        logger.info(f"File uploaded: {filename}")
        
        # Initialize session tracking
        if session_id not in session_files:
            session_files[session_id] = []
            session_content[session_id] = ''
        session_files[session_id].append(file_path)
        
        # Process file based on type
        try:
            if file_ext == '.pdf':
                text = secure_extract_pdf_text(file_path)
                session_content[session_id] = text
                return jsonify({
                    'text': escape(text),
                    'filename': filename,
                    'isImage': False
                })
            else:
                text = secure_extract_image_text(file_path)
                session_content[session_id] = text
                return jsonify({
                    'text': escape(text),
                    'filename': filename,
                    'isImage': True
                })
                
        except Exception as e:
            logger.error(f"File processing error: {e}")
            # Clean up failed file
            try:
                os.remove(file_path)
                session_files[session_id].remove(file_path)
            except (OSError, ValueError):
                pass
            return jsonify({'error': 'File processing failed'}), 500
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Handle secure file cleanup"""
    try:
        data = request.get_json()
        if not data or not isinstance(data, dict):
            return jsonify({'error': 'Invalid request'}), 400
        
        session_id = data.get('sessionId', '').strip()
        if not session_id or session_id not in session_files:
            return jsonify({'success': True})
        
        # Clean up files securely
        for file_path in session_files[session_id]:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up file: {file_path}")
            except OSError as e:
                logger.warning(f"Failed to remove file {file_path}: {e}")
        
        # Clean up session data
        session_files.pop(session_id, None)
        session_content.pop(session_id, None)
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return jsonify({'error': 'Cleanup failed'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle secure chat requests"""
    try:
        data = request.get_json()
        if not data or not isinstance(data, dict):
            return jsonify({'error': 'Invalid request'}), 400
        
        query = data.get('query', '').strip()
        session_id = data.get('sessionId', '').strip()
        
        # Log question securely
        logger.info(f"QUESTION: {escape(query)}")
        
        if not query:
            return jsonify({'error': 'Query required'}), 400
        
        if not session_id or session_id not in session_content:
            return jsonify({'error': 'No document available'}), 400
        
        context = session_content.get(session_id, '')
        if not context.strip():
            return jsonify({'error': 'Document content is empty'}), 400
        
        # Generate answer securely
        answer = qa_system.generate_answer(query, context)
        
        # Log answer securely
        logger.info(f"ANSWER: {escape(answer)}")
        
        return jsonify({'answer': answer})
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': 'Processing failed'}), 500

if __name__ == '__main__':
    # Perform startup cleanup
    secure_cleanup_files()
    
    # Run in production mode
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    if debug_mode:
        logger.warning("Running in debug mode - not recommended for production")
    
    app.run(
        debug=debug_mode,
        host=os.getenv('FLASK_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_PORT', '5000'))
    )