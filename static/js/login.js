// Redirect if already logged in
if (sessionStorage.getItem("userEmail")) {
    window.location.href = "/dashboard";
}

// Add error message div if not present
let errorDiv = document.getElementById('loginError');
if (!errorDiv) {
    errorDiv = document.createElement('div');
    errorDiv.id = 'loginError';
    errorDiv.style.color = 'red';
    errorDiv.style.marginBottom = '10px';
    errorDiv.style.textAlign = 'center';
    const form = document.getElementById('loginForm');
    form.insertBefore(errorDiv, document.getElementById('loginButton'));
}
errorDiv.textContent = '';

document.getElementById('loginForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const deviceId = document.getElementById('deviceId').value;
    const loginButton = document.getElementById('loginButton');
    const loadingText = document.getElementById('loadingText');
    const errorDiv = document.getElementById('loginError');

    loginButton.disabled = true;
    loadingText.style.display = 'block';
    errorDiv.textContent = '';

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, device_id: deviceId })
        });
    

        const data = await response.json();

        if (response.ok) {
            sessionStorage.setItem("userEmail", email);
            //sessionStorage.setItem("deviceId", deviceId); // store email and device_id
            window.location.href = "/dashboard";
        } else {
            if (data.error) {               
                errorDiv.textContent = data.error;
            } else if (data.errors && Array.isArray(data.errors)) {
                errorDiv.textContent = data.errors.map(e => e.msg || e.error || JSON.stringify(e)).join(', ');
            } else if (data.message) {
                errorDiv.textContent = data.message;
            } else {
                errorDiv.textContent = "Login failed. Please try again.";
            }
        }
    } catch (error) {
        errorDiv.textContent = "Server error. Please try again later.";
        console.error(error);
    } finally {
        loginButton.disabled = false;
        loadingText.style.display = 'none';
    }
}); 

 