import config from './config.js';
const backendURL = config.backendURL;


// --- Helper function to logout ---
function logoutUser() {
    localStorage.removeItem('loggedIn');
    localStorage.removeItem('token');
    localStorage.removeItem('chatHistory');
    localStorage.removeItem('currentUrl');
    window.location.href = "login.html";
}

// --- Force check login on page load ---
if (localStorage.getItem('loggedIn') !== 'true') {
    logoutUser();
}

// --- Automatic logout after inactivity ---
let logoutTimer;

// 30 minutes (in milliseconds)
const AUTO_LOGOUT_TIME = 30 * 60 * 1000;

// Reset the timer every user activity
function resetLogoutTimer() {
    clearTimeout(logoutTimer);
    logoutTimer = setTimeout(() => {
        alert("You have been logged out due to inactivity.");
        logoutUser();
    }, AUTO_LOGOUT_TIME);
}

// Listen for any user activity
window.onload = resetLogoutTimer;
document.onmousemove = resetLogoutTimer;
document.onkeydown = resetLogoutTimer;
document.onclick = resetLogoutTimer;
document.onscroll = resetLogoutTimer;


// Force check login status on page load
if (localStorage.getItem('loggedIn') !== 'true') {
    logoutUser();
}

// Validate if string is a valid URL
function isValidURL(string) {
    try {
        // Add a default scheme if missing
        const url = new URL(string.includes('://') ? string : `http://${string}`);
        return true;
    } catch (_) {
        return false;
    }
}

// Initialize chat history from localStorage or empty array
let chatHistory = JSON.parse(localStorage.getItem('chatHistory') || '[]');
let currentUrl = localStorage.getItem('currentUrl') || '';

// Function to save chat state
function saveChatState() {
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    localStorage.setItem('currentUrl', currentUrl);
}

// Function to restore chat UI from history
function restoreChatUI() {
    const chatArea = document.getElementById('chatArea');
    chatArea.innerHTML = ''; // Clear existing messages
    
    // Restore URL if exists
    if (currentUrl) {
        document.getElementById('urlInput').value = currentUrl;
    }
    
    // Restore all messages
    chatHistory.forEach(msg => {
        addMessage(msg.content, msg.role === 'user', false); // false means don't save to history
    });
}

// Modified addMessage function
function addMessage(content, isUser = false, shouldSave = true) {
    const message = document.createElement('div');
    message.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
    
    // Replace newlines with <br> tags for proper display
    message.innerHTML = content.replace(/\n/g, '<br>');
    
    const chatArea = document.getElementById('chatArea');
    chatArea.appendChild(message);
    chatArea.scrollTop = chatArea.scrollHeight;
    
    // Add to chat history only if it's a new message
    if (shouldSave) {
        chatHistory.push({
            role: isUser ? 'user' : 'assistant',
            content: content
        });
        saveChatState();
    }
}

// Update the summarize button handler
if (document.getElementById('summarizeButton')) {
    document.getElementById('summarizeButton').addEventListener('click', async function () {
        const url = document.getElementById('urlInput').value;
        currentUrl = url;  // Store current URL
        
        if (!isValidURL(url)) {
            addMessage('Please enter a valid URL.', false);
            return;
        }

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${backendURL}/summarize-url`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ url: url })
            });

            if (response.status === 401) {
                alert("Session expired. Please login again.");
                logoutUser();
                return;
            }

            const data = await response.json();
            
            // Clear chat history when new URL is summarized
            chatHistory = [];
            addMessage(`Summary: ${data.summary}`, false);
            saveChatState();
            
        } catch (error) {
            console.error("Error:", error);
            addMessage('Failed to summarize the URL.', false);
        }
    });
}

// Add this function to auto-resize textarea
function autoResizeTextarea(textarea) {
    // Reset height to auto to get the correct scrollHeight
    textarea.style.height = 'auto';
    
    // Set new height based on scrollHeight
    const newHeight = Math.min(textarea.scrollHeight, 150); // Max height of 150px
    textarea.style.height = `${newHeight}px`;
}

// Update the event listeners for the chat input
if (document.getElementById('submitButton')) {
    const questionInput = document.getElementById('questionInput');
    
    // Auto-resize on input
    questionInput.addEventListener('input', function() {
        autoResizeTextarea(this);
    });

    // Handle key events
    questionInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            if (e.shiftKey) {
                // Shift+Enter: add new line
                return; // Let the default behavior happen
            } else {
                // Enter only: send message
                e.preventDefault(); // Prevent new line
                if (this.value.trim()) {
                    document.getElementById('submitButton').click();
                }
            }
        }
    });

    // Update the submit button handler
    document.getElementById('submitButton').addEventListener('click', async function () {
        const question = questionInput.value.trim();
        
        if (!question) return;
        
        addMessage(question, true);
        questionInput.value = '';
        // Reset textarea height
        questionInput.style.height = 'auto';
        
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${backendURL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    url: currentUrl,
                    question: question,
                    chat_history: chatHistory
                })
            });

            if (response.status === 401) {
                alert("Session expired. Please login again.");
                logoutUser();
                return;
            }

            const data = await response.json();
            if (data.error) {
                addMessage(data.error.message, false);
            } else {
                addMessage(data.response, false);
            }
            
        } catch (error) {
            console.error("Error:", error);
            addMessage('Failed to get response. Please try again.', false);
        }
    });
}

// Handle Logout Button
if (document.getElementById('logoutButton')) {
    document.getElementById('logoutButton').addEventListener('click', function () {
        logoutUser();
    });
}

// Add clear chat button
const clearButton = document.createElement('button');
clearButton.textContent = 'Clear Chat';
clearButton.style.marginLeft = '10px';
document.querySelector('.url-section').appendChild(clearButton);

clearButton.addEventListener('click', () => {
    if (confirm('Are you sure you want to clear the chat history?')) {
        chatHistory = [];
        currentUrl = '';
        document.getElementById('urlInput').value = '';
        document.getElementById('chatArea').innerHTML = '';
        saveChatState();
    }
});

// Restore chat on page load
window.addEventListener('load', restoreChatUI);
