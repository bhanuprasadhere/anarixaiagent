document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const messagesDiv = document.getElementById('messages');
    const errorMessageDiv = document.getElementById('error-message');

    // Dynamically get the base URL of your Replit app
    const API_BASE_URL = window.location.origin;

    function addMessage(content, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message-' + sender);

        // Check if content is an image tag or other HTML
        if (typeof content === 'string' && content.trim().startsWith('<')) { // Simple check for HTML
            messageElement.innerHTML = content; // Insert as HTML
        } else {
            messageElement.textContent = content; // Insert as plain text
        }

        messagesDiv.appendChild(messageElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight; // Scroll to bottom
        return messageElement; // Return the created element for later use (e.g., typing)
    }

    // Helper function to simulate typing effect
    function typeMessage(element, text, delay = 20) {
        return new Promise(resolve => {
            let i = 0;
            element.textContent = ''; // Clear content before typing
            function typeChar() {
                if (i < text.length) {
                    element.textContent += text.charAt(i);
                    i++;
                    setTimeout(typeChar, delay);
                } else {
                    resolve(); // Typing complete
                }
            }
            typeChar();
        });
    }

    async function sendMessage() {
        const question = userInput.value.trim();
        if (question === '') {
            return;
        }

        addMessage(question, 'user');
        userInput.value = ''; // Clear input
        sendButton.disabled = true; // Disable button to prevent multiple sends
        errorMessageDiv.style.display = 'none'; // Hide previous errors

        // Add a temporary AI message element that will be typed into
        const aiMessageElement = addMessage('', 'ai'); // Create AI message element immediately

        try {
            const response = await fetch(`${API_BASE_URL}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: question }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(errorText || 'Something went wrong on the server.');
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let fullResponseText = '';
            let isHtmlResponse = false; // Flag to check if the response is HTML (like an image)

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                fullResponseText += chunk;

                // Check if the content looks like HTML (specifically for img tags)
                if (fullResponseText.trim().startsWith('<img src="data:image/png;base64,')) {
                    isHtmlResponse = true;
                    // For images, we don't stream character by character.
                    // The entire HTML tag should be received as one "message".
                    aiMessageElement.innerHTML = fullResponseText;
                    break; // Once we know it's an image, stop streaming logic
                } else {
                    // For text responses, update content incrementally
                    aiMessageElement.textContent = fullResponseText;
                }
                messagesDiv.scrollTop = messagesDiv.scrollHeight; // Keep scrolling down
            }

            // If it was a text response (not an image), apply the typing effect
            if (!isHtmlResponse) {
                aiMessageElement.textContent = ''; // Clear current text for typing animation
                await typeMessage(aiMessageElement, fullResponseText);
            }
            // If it was an image, it's already set via innerHTML above.

        } catch (error) {
            console.error('Error fetching AI response:', error);
            const displayMessage = `Sorry, I couldn't process that. Error: ${error.message}. Please try again.`;
            errorMessageDiv.textContent = displayMessage;
            errorMessageDiv.style.display = 'block';

            if (aiMessageElement.textContent === '') {
                aiMessageElement.textContent = "Sorry, I couldn't process that. Please try again or ask a different question.";
            } else {
                aiMessageElement.textContent += "\n(Error: Could not complete response)";
            }
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

        } finally {
            sendButton.disabled = false;
            userInput.focus();
        }
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
});