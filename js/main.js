document.addEventListener('DOMContentLoaded', () => {
    const pdfInput = document.getElementById('pdfInput');
    const textOutput = document.getElementById('textOutput');
    const readAloudBtn = document.getElementById('readAloud');
    const stopReadBtn = document.getElementById('stopRead');
    const chatInput = document.getElementById('chatInput');
    const sendChatBtn = document.getElementById('sendChat');
    const chatOutput = document.getElementById('chatOutput');
    let extractedText = '';
    let speech = null;

    // PDF Upload
    pdfInput.addEventListener('change', async () => {
        const file = pdfInput.files[0];
        if (!file) return;
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            if (result.error) {
                alert(result.error);
                return;
            }
            extractedText = result.text;
            textOutput.textContent = extractedText;
            readAloudBtn.disabled = false;
        } catch (error) {
            alert('Error uploading PDF: ' + error.message);
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

    // Chatbot
    sendChatBtn.addEventListener('click', async () => {
        const query = chatInput.value.trim();
        if (!query || !extractedText) return;
        
        try {
            chatOutput.innerHTML += `<p><strong>You:</strong> ${query}</p>`;
            chatOutput.innerHTML += `<p><strong>AI:</strong> <em>Thinking...</em></p>`;
            chatOutput.scrollTop = chatOutput.scrollHeight;
            
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, context: extractedText })
            });
            const result = await response.json();
            
            // Remove the "thinking" message
            chatOutput.innerHTML = chatOutput.innerHTML.replace('<p><strong>AI:</strong> <em>Thinking...</em></p>', '');
            
            if (result.error) {
                chatOutput.innerHTML += `<p class="text-red-500">Error: ${result.error}</p>`;
                return;
            }
            chatOutput.innerHTML += `<p><strong>AI:</strong> ${result.answer}</p>`;
            chatInput.value = '';
            chatOutput.scrollTop = chatOutput.scrollHeight;
        } catch (error) {
            chatOutput.innerHTML = chatOutput.innerHTML.replace('<p><strong>AI:</strong> <em>Thinking...</em></p>', '');
            chatOutput.innerHTML += `<p class="text-red-500">Error: ${error.message}</p>`;
        }
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatBtn.click();
    });
});