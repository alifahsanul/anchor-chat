const backendURL = 'https://anchor-chat-production.up.railway.app';

document.getElementById('loginButton').addEventListener('click', async function () {
    const password = document.getElementById('passwordInput').value;

    try {
        const response = await fetch(`${backendURL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password: password })
        });

        if (response.ok) {
            localStorage.setItem('loggedIn', 'true');
            window.location.href = "chat.html";
        } else {
            const data = await response.json();
            document.getElementById('loginError').innerText = data.detail || 'Login failed.';
        }
    } catch (error) {
        console.error("Login error:", error);
        document.getElementById('loginError').innerText = 'Network error. Please try again.';
    }
});
