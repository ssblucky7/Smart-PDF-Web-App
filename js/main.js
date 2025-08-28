document.addEventListener('DOMContentLoaded', () => {
    const pdfInput = document.getElementById('pdfInput');
    const textOutput = document.getElementById('textOutput');
    const readAloudBtn = document.getElementById('readAloud');
    const stopReadBtn = document.getElementById('stopRead');
    const chatInput = document.getElementById('chatInput');
    const sendChatBtn = document.getElementById('sendChat');
    const chatOutput = document.getElementById('chatOutput');
    const pdfViewer = document.getElementById('pdfViewer');
    const imageViewer = document.getElementById('imageViewer');
    const pdfPreviewContainer = document.querySelector('.pdf-preview-container');
    
    // Validate DOM elements
    if (!pdfInput || !textOutput || !readAloudBtn || !stopReadBtn || !chatInput || !sendChatBtn || !chatOutput) {
        console.error('Required DOM elements not found');
        return;
    }
    
    let extractedText = '';
    let speech = null;
    let currentFilename = '';
    let isImage = false;
    
    // Generate a unique session ID
    const sessionId = Date.now().toString() + Math.random().toString(36).substring(2, 15);

    // HTML escape function
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // File Upload
    pdfInput.addEventListener('change', async () => {
        const file = pdfInput.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('sessionId', sessionId);
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            
            if (result.error) {
                showError(result.error);
                return;
            }
            
            extractedText = result.text;
            currentFilename = result.filename;
            textOutput.textContent = extractedText;
            readAloudBtn.disabled = false;
            
            isImage = result.isImage;
            
            if (isImage) {
                imageViewer.src = `/uploads/${currentFilename}`;
                imageViewer.classList.remove('hidden');
                pdfViewer.classList.add('hidden');
            } else {
                pdfViewer.src = `/uploads/${currentFilename}`;
                pdfViewer.classList.remove('hidden');
                imageViewer.classList.add('hidden');
            }
            
            if (pdfPreviewContainer) {
                pdfPreviewContainer.classList.remove('hidden');
            }
        } catch (error) {
            showError('Error uploading file: ' + error.message);
        }
    });

    // Read Aloud
    readAloudBtn.addEventListener('click', () => {
        if (extractedText) {
            speech = new SpeechSynthesisUtterance(extractedText);
            speech.lang = 'en-US';
            speech.rate = 1;
            speech.onend = () => {
                stopReadBtn.classList.add('hidden');
                readAloudBtn.classList.remove('hidden');
            };
            window.speechSynthesis.speak(speech);
            readAloudBtn.classList.add('hidden');
            stopReadBtn.classList.remove('hidden');
        }
    });

    stopReadBtn.addEventListener('click', () => {
        if (speech) {
            window.speechSynthesis.cancel();
            stopReadBtn.classList.add('hidden');
            readAloudBtn.classList.remove('hidden');
        }
    });

    // Q&A System
    sendChatBtn.addEventListener('click', async () => {
        const query = chatInput.value.trim();
        if (!query || !extractedText) return;
        
        try {
            // Sanitize and display user input
            const escapedQuery = escapeHtml(query);
            addChatMessage('You', escapedQuery);
            addChatMessage('AI', '<em>Processing...</em>');
            
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, sessionId: sessionId })
            });
            const result = await response.json();
            
            // Remove processing message
            removeLastMessage();
            
            if (result.error) {
                addChatMessage('AI', `<span class="text-red-500">Error: ${escapeHtml(result.error)}</span>`);
                return;
            }
            
            // Add answer with speak button
            const answerHtml = `${result.answer} <button onclick="speakText('${result.answer.replace(/'/g, "\\'")}')" class="speak-btn">🔊</button>`;
            addChatMessage('AI', answerHtml);
            chatInput.value = '';
            
        } catch (error) {
            removeLastMessage();
            addChatMessage('AI', `<span class="text-red-500">Error: ${escapeHtml(error.message)}</span>`);
        }
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatBtn.click();
    });
    
    // Helper functions
    function addChatMessage(sender, message) {
        const messageElement = document.createElement('p');
        messageElement.innerHTML = `<strong>${escapeHtml(sender)}:</strong> ${message}`;
        chatOutput.appendChild(messageElement);
        chatOutput.scrollTop = chatOutput.scrollHeight;
    }
    
    function removeLastMessage() {
        const lastMessage = chatOutput.lastElementChild;
        if (lastMessage) {
            chatOutput.removeChild(lastMessage);
        }
    }
    
    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        errorDiv.style.cssText = 'background: #fee; color: #c33; padding: 10px; margin: 10px 0; border-radius: 4px;';
        document.body.insertBefore(errorDiv, document.body.firstChild);
        setTimeout(() => errorDiv.remove(), 5000);
    }
    
    // Global function for speaking chat responses
    window.speakText = function(text) {
        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
        }
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 1;
        window.speechSynthesis.speak(utterance);
    };
    
    // Clean up files when page is unloaded
    window.addEventListener('beforeunload', async () => {
        if (currentFilename) {
            try {
                await fetch('/cleanup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sessionId: sessionId }),
                    keepalive: true
                });
            } catch (error) {
                console.error('Error during cleanup:', error);
            }
        }
    });
});