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

function showValidation(input, message) {
  let msgElem = input.nextElementSibling;
  if (!msgElem || !msgElem.classList.contains('validation-msg')) {
    msgElem = document.createElement('div');
    msgElem.className = 'validation-msg';
    input.parentNode.insertBefore(msgElem, input.nextSibling);
  }
  msgElem.textContent = message;
  msgElem.style.color = message ? '#e74c3c' : '#27ae60';
  input.classList.toggle('input-error', !!message);
  input.classList.toggle('input-success', !message);
}

function showSuccess(input) {
  showValidation(input, '');
  input.classList.add('input-success');
  input.classList.remove('input-error');
}

const MAX_LENGTHS = {
  email: 50,
  password: 16,
  deviceId: 12
};

function enforceMaxLength(input, maxLength, errorMsg) {
  input.addEventListener('input', function (e) {
    if (input.value.length > maxLength) {
      input.value = input.value.slice(0, maxLength);
      showValidation(input, errorMsg);
    }
  });
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const deviceIdInput = document.getElementById('deviceId');
    const loginError = document.getElementById('loginError');
    const loadingText = document.getElementById('loadingText');

    // Enforce max length and show error
    enforceMaxLength(emailInput, MAX_LENGTHS.email, 'Maximum number of characters reached, Max. 20');
    enforceMaxLength(passwordInput, MAX_LENGTHS.password, 'Password cannot exceed 16 digits.');
    enforceMaxLength(deviceIdInput, MAX_LENGTHS.deviceId, 'Device ID cannot exceed 12 digits.');

    // Debounced validation handlers with per-field feedback
    function attachValidation(input, validateFn) {
      const debounced = debounce(() => {
        const error = validateFn(input.value.trim());
        if (error) showValidation(input, error);
        else showSuccess(input);
      }, 300);
      input.addEventListener('input', debounced);
      input.addEventListener('blur', () => {
        const error = validateFn(input.value.trim());
        if (error) showValidation(input, error);
        else showSuccess(input);
      });
    }

    attachValidation(emailInput, validateLoginEmail);
    attachValidation(passwordInput, validateLoginPassword);
    attachValidation(deviceIdInput, validateLoginDeviceId);

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

        // Always trim input values
        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();
        const device_id = deviceIdInput.value.trim();

        let valid = true;

        const emailValidation = validateLoginEmail(email);
        if (emailValidation) {
            showValidation(emailInput, emailValidation);
            valid = false;
        }
        const passwordValidation = validateLoginPassword(password);
        if (passwordValidation) {
            showValidation(passwordInput, passwordValidation);
            valid = false;
        }
        const deviceIdValidation = validateLoginDeviceId(device_id);
        if (deviceIdValidation) {
            showValidation(deviceIdInput, deviceIdValidation);
            valid = false;
        }
        if (!valid) return;

        loadingText.style.display = 'block';

        try {
            // Use credentials: 'include' for cookies/session support
            const BACKEND_URL = window.BACKEND_URL; // <-- Set your actual backend URL here
            const res = await fetch(`${BACKEND_URL}api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, device_id }),
                credentials: 'include'
            });
            const data = await res.json();
            loadingText.style.display = 'none';
            if (res.ok && data.success) {
                sessionStorage.setItem('userEmail', email);
                sessionStorage.setItem('deviceId', device_id);
                showPopup('Login successful', () => {
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

 