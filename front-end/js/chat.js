const backendURL = 'https://anchor-chat-production.up.railway.app';
// const backendURL = 'http://127.0.0.1:8000';


// --- Helper function to logout ---
function logoutUser() {
    localStorage.removeItem('loggedIn');
    localStorage.removeItem('token');
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

// Handle Summarize Button
if (document.getElementById('summarizeButton')) {
    document.getElementById('summarizeButton').addEventListener('click', async function () {
        const chatArea = document.getElementById('chatArea');
        chatArea.innerHTML = ""; // clear old content
        const url = document.getElementById('urlInput').value;

        if (!isValidURL(url)) {
            chatArea.innerHTML = `<div style="color: red;"><strong>Error:</strong> Please enter a valid URL.</div>`;
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
                // Unauthorized, force logout
                alert("Session expired. Please login again.");
                logoutUser();
                return;
            }

            const data = await response.json();

            chatArea.innerHTML = `
                <div><strong>Summary:</strong></div>
                <div class="summary-box">${data.summary || "Error or no summary returned."}</div>
            `;
        } catch (error) {
            console.error("Error:", error);
            chatArea.innerHTML = `<div style="color: red;"><strong>Error:</strong> Failed to summarize the URL.</div>`;
        }
    });
}

// Handle Send Question Button (future feature)
if (document.getElementById('submitButton')) {
    document.getElementById('submitButton').addEventListener('click', function () {
        const question = document.getElementById('questionInput').value;
        const chatArea = document.getElementById('chatArea');

        chatArea.innerHTML += `
            <div><strong>You:</strong> ${question}</div>
            <div><em>(Question feature coming soon...)</em></div>
        `;
    });
}

// Handle Logout Button
if (document.getElementById('logoutButton')) {
    document.getElementById('logoutButton').addEventListener('click', function () {
        logoutUser();
    });
}
