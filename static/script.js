// Speech recognition setup
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = 'fr-FR';
recognition.interimResults = false;
recognition.maxAlternatives = 1;

let isListening = false;

recognition.onresult = (event) => {
    const speechResult = event.results[0][0].transcript;
    document.getElementById('user-input').value = speechResult;
    sendMessage();
};

recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
    isListening = false;
    updateVoiceButton();
};

recognition.onend = () => {
    isListening = false;
    updateVoiceButton();
};

function toggleVoiceInput() {
    if (!isListening) {
        recognition.start();
        isListening = true;
    } else {
        recognition.stop();
        isListening = false;
    }
    updateVoiceButton();
}

function updateVoiceButton() {
    const voiceButton = document.getElementById('voice-btn');
    voiceButton.classList.toggle('listening', isListening);
    voiceButton.querySelector('i').className = isListening ? 'fas fa-stop' : 'fas fa-microphone';
}

function sendMessage() {
    var userInput = document.getElementById('user-input');
    var userMessage = userInput.value.trim();
    if (userMessage === '') {
        return;
    }
    appendMessage('user', userMessage);
    userInput.value = '';

    // Create a placeholder for the bot's response
    var botMessageElement = appendMessage('bot', '');
    botMessageElement.classList.add('typing');

    fetch('/send_message', {
        method: 'POST',
        body: new URLSearchParams({ 'user_message': userMessage }),
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let botResponse = '';

        function readStream() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    botMessageElement.classList.remove('typing');
                    botMessageElement.innerText = botResponse;
                    return;
                }
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            botResponse += data.response;
                            botMessageElement.innerText = botResponse;
                        } catch (e) {
                            console.error('Error parsing JSON:', e);
                        }
                    }
                });
                readStream();
            });
        }

        readStream();
    })
    .catch(error => {
        console.error('Error:', error);
        botMessageElement.classList.remove('typing');
        botMessageElement.innerText = 'Une erreur s\'est produite lors de la communication avec le serveur.';
    });
}

function appendMessage(sender, message) {
    var chatBox = document.getElementById('chat-box');
    var messageElement = document.createElement('div');
    messageElement.className = sender + '-message message';
    messageElement.innerText = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
    return messageElement;
}

// Add event listener for 'Enter' key press
document.getElementById('user-input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

// Initialize voice button state
document.addEventListener('DOMContentLoaded', () => {
    updateVoiceButton();
});