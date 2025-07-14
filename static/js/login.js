import {
  validateLoginEmail,
  validateLoginPassword,
  validateLoginDeviceId
} from './validation/LoginValidations.js';

function debounce(fn, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const deviceIdInput = document.getElementById('deviceId');
    const loginError = document.getElementById('loginError');
    const loadingText = document.getElementById('loadingText');

    // Debounced validation handlers
    emailInput.addEventListener('input', debounce(function () {
        loginError.textContent = '';
        const msg = validateLoginEmail(emailInput.value.trim());
        if (msg) loginError.textContent = msg;
    }, 300));
    emailInput.addEventListener('blur', function () {
        const msg = validateLoginEmail(emailInput.value.trim());
        loginError.textContent = msg;
    });

    passwordInput.addEventListener('input', debounce(function () {
        loginError.textContent = '';
        const msg = validateLoginPassword(passwordInput.value);
        if (msg) loginError.textContent = msg;
    }, 300));
    passwordInput.addEventListener('blur', function () {
        const msg = validateLoginPassword(passwordInput.value);
        loginError.textContent = msg;
    });

    deviceIdInput.addEventListener('input', debounce(function () {
        loginError.textContent = '';
        const msg = validateLoginDeviceId(deviceIdInput.value.trim());
        if (msg) loginError.textContent = msg;
    }, 300));
    deviceIdInput.addEventListener('blur', function () {
        const msg = validateLoginDeviceId(deviceIdInput.value.trim());
        loginError.textContent = msg;
    });

    // Popup for success
    function showPopup(message, callback) {
        let popup = document.createElement('div');
        popup.className = 'popup-success';
        popup.innerHTML = `<div class="popup-content">
            <h3>Login successful</h3>
            <p>${message}</p>
            <a href="/dashboard" class="popup-link" style="display:none;opacity:0;transition:opacity 0.4s;">Go to Dashboard</a>
        </div>`;
        document.body.appendChild(popup);
        setTimeout(() => {
            popup.classList.add('show');
            setTimeout(() => {
                const btn = popup.querySelector('.popup-link');
                btn.style.display = 'inline-block';
                setTimeout(() => { btn.style.opacity = 1; }, 10);
            }, 1200);
        }, 10);
        popup.querySelector('.popup-link').onclick = function(e) {
            e.preventDefault();
            popup.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(popup);
                if (callback) callback();
            }, 300);
            window.location.href = '/dashboard';
        };
    }

    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        loginError.textContent = '';
        loadingText.style.display = 'none';

        const email = emailInput.value.trim();
        const password = passwordInput.value;
        const device_id = deviceIdInput.value.trim();

        let valid = true;

        const emailValidation = validateLoginEmail(email);
        if (emailValidation) {
            loginError.textContent = emailValidation;
            valid = false;
        }
        const passwordValidation = validateLoginPassword(password);
        if (passwordValidation) {
            loginError.textContent = passwordValidation;
            valid = false;
        }
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
                showPopup('You have logged in successfully!', () => {
                    window.location.href = '/dashboard';
                });
            } else {
                loginError.textContent = data.error || 'Login failed. Please check your credentials.';
            }
        } catch (err) {
            loadingText.style.display = 'none';
            loginError.textContent = 'Could not connect to server. Please try again later.';
        }
    });
}); 

 