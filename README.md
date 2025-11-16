# Team Member
**Suresh Mahato**
**Sastika Regmi**
**Nischal Shrestha**


# Smart PDF Q&A System

🚀 **Production-Ready AI-Powered Document Intelligence Platform**

A secure, scalable web application that enables intelligent interaction with PDF documents and images through advanced text extraction and AI-powered question-answering capabilities.

## ✨ Key Features

### 📄 Document Processing
- **Multi-Format Support**: PDF documents and images (JPG, PNG, GIF, BMP, TIFF)
- **Dual Text Extraction**: Direct PDF parsing with intelligent OCR fallback
- **Real-Time Preview**: Embedded document viewer with responsive design
- **Memory Optimization**: Efficient processing of large documents

### 🤖 AI-Powered Q&A
- **Hugging Face Integration**: DistilBERT model for accurate question answering
- **Local Fallback System**: Keyword-based processing when API unavailable
- **Context-Aware Responses**: Question type detection (what, how, why, when, where, who)
- **Enhanced Reasoning**: Intelligent answer generation with explanatory context

### 🔊 Accessibility Features
- **Text-to-Speech**: Browser-based speech synthesis for extracted text
- **Interactive Chat**: Voice playback for individual AI responses
- **Responsive Design**: Mobile-friendly interface with accessibility compliance

### 🔒 Enterprise Security
- **Input Sanitization**: XSS prevention and secure data handling
- **Path Traversal Protection**: Safe file operations with validation
- **Session Management**: Secure file tracking with automatic cleanup
- **Comprehensive Logging**: Production-ready monitoring and error tracking

## 🏗️ Architecture

### Technology Stack
- **Backend**: Flask (Python 3.8+) with production security features
- **Frontend**: HTML5, CSS3, Vanilla JavaScript with XSS protection
- **AI/ML**: Hugging Face Transformers (DistilBERT-base-cased-distilled-squad)
- **Text Processing**: PyPDF2, pytesseract, pdf2image with error handling
- **Security**: Werkzeug security utilities, MarkupSafe sanitization

### System Components
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask Backend  │    │  Hugging Face   │
│   (Browser)     │◄──►│   (Python)       │◄──►│     API         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Static Files  │    │   File Storage   │    │   ML Models     │
│   (CSS/JS)      │    │   (Uploads)      │    │   (DistilBERT)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📦 Dependencies

### Core Dependencies
```
Flask==3.1.1              # Web framework with security features
Werkzeug==3.1.3           # WSGI utilities and security functions
PyPDF2==3.0.1             # PDF text extraction
pytesseract==0.3.13       # OCR processing
pdf2image==1.17.0         # PDF to image conversion
Pillow==11.3.0            # Image processing (security patched)
huggingface-hub==0.20.0   # AI model integration
python-dotenv==1.1.0      # Environment configuration
MarkupSafe==2.1.3         # XSS prevention
```

### System Requirements
- **Python**: 3.8 or higher
- **Tesseract OCR**: Text extraction from images
- **Poppler**: PDF to image conversion
- **Memory**: 2GB+ recommended for large documents
- **Storage**: 100MB+ for temporary file processing

## 🚀 Quick Start

### 1. Installation
```bash
# Clone repository
git clone <repository-url>
cd Smart-PDF-Web-App

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. System Dependencies

**Windows:**
```bash
# Download and install Tesseract from GitHub
# Download Poppler and add to PATH
```

**macOS:**
```bash
brew install tesseract poppler
```

**Linux:**
```bash
sudo apt install tesseract-ocr poppler-utils
```

### 3. Configuration
```bash
# Create environment file
cp .env.example .env

# Edit .env with your configuration
HF_TOKEN=your_hugging_face_api_token
SECRET_KEY=your_secure_secret_key
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=16777216
FLASK_DEBUG=False
```

### 4. Run Application
```bash
python app.py
```

Access the application at: `http://127.0.0.1:5000`

## 🔧 Configuration Options

### Environment Variables
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `HF_TOKEN` | Hugging Face API token | - | ✅ |
| `SECRET_KEY` | Flask secret key | - | ✅ |
| `UPLOAD_FOLDER` | File upload directory | uploads | ❌ |
| `MAX_FILE_SIZE` | Maximum file size (bytes) | 16777216 | ❌ |
| `FLASK_DEBUG` | Debug mode | False | ❌ |
| `FLASK_HOST` | Server host | 127.0.0.1 | ❌ |
| `FLASK_PORT` | Server port | 5000 | ❌ |

### Performance Tuning
- **MAX_CONTEXT_LENGTH**: 2000 characters (API optimization)
- **MAX_PAGES_OCR**: 10 pages (memory optimization)
- **Session Timeout**: 1 hour (automatic cleanup)

## 🛡️ Security Features

### Input Validation
- File type whitelist validation
- Filename sanitization
- Session ID regex validation
- Request size limits

### XSS Prevention
- Input sanitization with MarkupSafe
- Output encoding for user content
- Secure DOM manipulation

### Path Traversal Protection
- Safe file path construction
- Directory traversal prevention
- Secure file serving

### Error Handling
- Comprehensive exception handling
- Secure error messages
- Detailed logging without sensitive data exposure

## 📊 Performance Characteristics

### Processing Times
- **File Upload**: 2-10 seconds (size dependent)
- **PDF Text Extraction**: 1-5 seconds (direct) / 5-30 seconds (OCR)
- **AI Q&A Response**: 1-3 seconds (API) / <1 second (local)
- **Session Cleanup**: <1 second

### Scalability Limits
- **Maximum File Size**: 16MB (configurable)
- **Concurrent Sessions**: Memory dependent
- **OCR Processing**: 10 pages maximum

## 🔍 API Documentation

### File Upload
```http
POST /upload
Content-Type: multipart/form-data

file: <PDF or Image file>
sessionId: <unique session identifier>
```

### Question Answering
```http
POST /chat
Content-Type: application/json

{
  "query": "What is this document about?",
  "sessionId": "unique_session_id"
}
```

### File Cleanup
```http
POST /cleanup
Content-Type: application/json

{
  "sessionId": "unique_session_id"
}
```

## 🚀 Production Deployment

### Security Checklist
- [ ] Set `FLASK_DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure HTTPS
- [ ] Set up reverse proxy (Nginx)
- [ ] Implement rate limiting
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging

### Recommended Setup
```bash
# Production WSGI server
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Nginx configuration
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔧 Troubleshooting

### Common Issues

**Tesseract not found:**
```bash
# Ensure Tesseract is in PATH
tesseract --version
```

**Poppler not found:**
```bash
# Ensure Poppler is installed and in PATH
pdftoppm -h
```

**HF API errors:**
- Check API token validity
- Verify internet connection
- System falls back to local processing

### Logging
Check `app.log` for detailed error information and system events.

## 📈 Monitoring

### Key Metrics
- Request/response times
- File processing success rates
- API success/failure rates
- Memory usage patterns
- Error rates by category

### Log Analysis
```bash
# View recent logs
tail -f app.log

# Search for errors
grep "ERROR" app.log

# Monitor API calls
grep "HF API" app.log
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Follow security best practices
4. Add comprehensive tests
5. Update documentation
6. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run security scan
bandit -r app.py

# Run tests
python -m pytest tests/
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please:
1. Check the troubleshooting section
2. Review the system documentation
3. Open an issue with detailed information
4. Include relevant log entries

---

**S.S.B Lucky 7**
