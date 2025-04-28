// --- Backend URL ---
const backendURL = 'https://anchor-chat-production.up.railway.app';


// --- Login protection ---
if (localStorage.getItem('loggedIn') !== 'true') {
    window.location.href = "login.html"; // 🚨 Block access if not logged in
}


// --- URL Validation ---
function isValidURL(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}


// --- Handle Summarize Button ---
if (document.getElementById('summarizeButton')) {
    document.getElementById('summarizeButton').addEventListener('click', async function () {
        const chatArea = document.getElementById('chatArea');
        chatArea.innerHTML = ""; // 🧹 Clear previous content FIRST

        const url = document.getElementById('urlInput').value;

        if (!isValidURL(url)) {
            chatArea.innerHTML = `
                <div style="color: red;"><strong>Error:</strong> Please enter a valid URL.</div>
            `;
            return;
        }

        try {
            const response = await fetch(`${backendURL}/summarize-url`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            chatArea.innerHTML = `
                <div><strong>Summary:</strong></div>
                <pre>${data.summary || "Error or no summary returned."}</pre>
            `;
        } catch (error) {
            console.error("Error:", error);
            chatArea.innerHTML = `
                <div style="color: red;"><strong>Error:</strong> Failed to summarize the URL.</div>
            `;
        }
    });
}


// --- Handle Send Question Button (future feature) ---
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

// --- Handle Logout Button ---
if (document.getElementById('logoutButton')) {
    document.getElementById('logoutButton').addEventListener('click', function () {
        localStorage.removeItem('loggedIn'); // 🧹 Clear login status
        window.location.href = "login.html"; // 🚪 Redirect to login
    });
}
