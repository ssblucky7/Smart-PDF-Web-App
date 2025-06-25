# SmartPDF Web App

A web application that allows users to upload PDF files, extract text content, interact with the content through a chatbot interface, and have the text read aloud.

## Features

- **PDF Upload**: Upload PDF documents to extract text content
- **PDF Preview**: View the original PDF document directly in the browser
- **Text Extraction**: Extract text from PDFs using PyPDF2 with OCR fallback using pytesseract
- **Read Aloud**: Listen to the extracted text using browser's speech synthesis
- **Chat Interface**: Ask questions about the PDF content and get AI-powered responses
- **Responsive Design**: User-friendly interface that works on various devices

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **PDF Processing**: PyPDF2, pdf2image, pytesseract
- **AI Integration**: Google Gemini API (Gemini 2.0 Flash) with local fallback processing

## Requirements

- Python 3.8+
- Tesseract OCR (for OCR functionality)
- Poppler (for pdf2image functionality)

## Python Dependencies

The following Python packages are required and will be installed via `requirements.txt`:

- **Flask==3.1.1**: Web framework for creating the web application server and handling HTTP requests/responses
- **Werkzeug==3.1.3**: WSGI utility library that Flask depends on, provides secure filename handling and request processing
- **python-dotenv==1.1.0**: Loads environment variables from `.env` file to manage API keys and configuration securely
- **PyPDF2==3.0.1**: Primary PDF processing library for extracting text directly from PDF documents
- **pytesseract==0.3.13**: Python wrapper for Tesseract OCR engine, used for extracting text from images and scanned PDFs
- **pdf2image==1.17.0**: Converts PDF pages to images, enabling OCR processing when direct text extraction fails
- **requests==2.32.3**: HTTP library for making API calls to external services (AI chat functionality)

- **Pillow==11.2.1**: Python Imaging Library for image processing and manipulation, required by pytesseract and pdf2image

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd Smart-PDF-Web-App
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install Tesseract OCR:
   - **Windows**: Download and install from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt install tesseract-ocr`

4. Install Poppler:
   - **Windows**: Download from [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/) and add to PATH
   - **macOS**: `brew install poppler`
   - **Linux**: `sudo apt install poppler-utils`

5. Create a `.env` file in the project root with your API key:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

1. Start the Flask server:
   ```
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

3. Upload a PDF file, view the PDF preview, see the extracted text, and interact with the chatbot.

## How It Works

1. **PDF Upload**: User uploads a PDF file which is processed on the server
2. **PDF Preview**: The original PDF is displayed in an embedded viewer
3. **Text Extraction**: The app attempts to extract text directly using PyPDF2, with OCR fallback using pytesseract
4. **Chat Functionality**: User questions are processed against the extracted text using the Gemini 2.0 Flash model
5. **Read Aloud**: The browser's built-in speech synthesis API reads the extracted text

## Limitations

- Large PDF files may take longer to process
- OCR accuracy depends on the quality of the PDF
- API-based chat responses require an internet connection

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.