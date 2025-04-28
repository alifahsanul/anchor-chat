const backendURL = 'https://anchor-chat-production.up.railway.app';
// const backendURL = 'http://127.0.0.1:8000';

document.getElementById('loginButton').addEventListener('click', async function () {
    const password = document.getElementById('passwordInput').value;
    console.log(password); // ✅ JS style logging

    try {
        const response = await fetch(`${backendURL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password: password })
        });
        console.log(response); // ✅ JS style logging

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('loggedIn', 'true');
            localStorage.setItem('token', data.token);
            window.location.href = "chat.html";
        } else {
            const data = await response.json();
            document.getElementById('loginError').innerText = data.error?.message || 'Login failed.';
        }
    } catch (error) {
        console.error("Login error:", error);
        document.getElementById('loginError').innerText = 'Network error. Please try again.';
    }
});
