import {
  validateLoginEmail,
  validateLoginPassword,
  validateLoginDeviceId
} from './validation/LoginValidations.js';

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const deviceIdInput = document.getElementById('deviceId');
    const loginError = document.getElementById('loginError');
    const loadingText = document.getElementById('loadingText');

    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        loginError.textContent = '';
        loadingText.style.display = 'none';

        const email = emailInput.value.trim();
        const password = passwordInput.value;
        const device_id = deviceIdInput.value.trim();

        let valid = true;

        // Validate email
        const emailValidation = validateLoginEmail(email);
        if (emailValidation) {
            loginError.textContent = emailValidation;
            valid = false;
        }

        // Validate password
        const passwordValidation = validateLoginPassword(password);
        if (passwordValidation) {
            loginError.textContent = passwordValidation;
            valid = false;
        }

        // Validate device_id
        const deviceIdValidation = validateLoginDeviceId(device_id);
        if (deviceIdValidation) {
            loginError.textContent = deviceIdValidation;
            valid = false;
        }

        if (!valid) return;

        loadingText.style.display = 'block';

        try {
            const res = await fetch('http://localhost:4000/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, device_id })
            });
            const data = await res.json();
            loadingText.style.display = 'none';
            if (res.ok && data.success) {
                sessionStorage.setItem('userEmail', email);
                sessionStorage.setItem('deviceId', device_id);
                window.location.href = '/dashboard';
            } else {
                loginError.textContent = data.error || 'Login failed. Please check your credentials.';
            }
        } catch (err) {
            loadingText.style.display = 'none';
            loginError.textContent = 'Could not connect to server. Please try again later.';
        }
    });
}); 

 