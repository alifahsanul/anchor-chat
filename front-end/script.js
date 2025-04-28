let authToken = '';

document.getElementById('loginButton').addEventListener('click', async function() {
    const password = document.getElementById('passwordInput').value;

    try {
        const response = await fetch('https://anchor-chat-production.up.railway.app/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: password })
        });

        if (response.ok) {
            const data = await response.json();
            authToken = data.token;
            document.getElementById('loginSection').style.display = 'none';
            document.getElementById('chatSection').style.display = 'block';
        } else {
            document.getElementById('loginError').innerText = 'Incorrect password!';
        }
    } catch (error) {
        console.error('Login error:', error);
        document.getElementById('loginError').innerText = 'Server error!';
    }
});

document.getElementById('submitButton').addEventListener('click', async function() {
    const url = document.getElementById('urlInput').value;
    const question = document.getElementById('questionInput').value;

    if (!url || !question) {
        alert('Please enter both URL and question.');
        return;
    }

    const chatArea = document.getElementById('chatArea');
    const userMessage = `<div><strong>You:</strong> ${question}</div>`;
    chatArea.innerHTML += userMessage;

    try {
        const response = await fetch('https://anchor-chat-production.up.railway.app/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ url: url, question: question })
        });

        const data = await response.json();
        const botMessage = `<div><strong>Bot:</strong> ${data.answer}</div>`;
        chatArea.innerHTML += botMessage;
        chatArea.scrollTop = chatArea.scrollHeight;
    } catch (error) {
        console.error('Chat error:', error);
        alert('Error sending message.');
    }
});
