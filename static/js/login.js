// Redirect if already logged in
if (sessionStorage.getItem("userEmail")) {
    window.location.href = "/dashboard";
}

document.getElementById('loginForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const loginButton = document.getElementById('loginButton');
    const loadingText = document.getElementById('loadingText');

    loginButton.disabled = true;
    loadingText.style.display = 'block';

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            sessionStorage.setItem("userEmail", email);
            alert("Logged in successfully!");
            window.location.href = "/dashboard";
        } else {
            alert(data.message || "Login failed. Please try again.");
        }
    } catch (error) {
        alert("Server error. Please try again later.");
        console.error(error);
    } finally {
        loginButton.disabled = false;
        loadingText.style.display = 'none';
    }
}); 