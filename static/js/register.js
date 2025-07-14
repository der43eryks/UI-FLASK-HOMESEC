import {
  validateRegisterEmail,
  validateRegisterPassword,
  validateRegisterPhone,
  validateRegisterDeviceId,
  validateRegisterModel
} from './validation/registerValidations.js';

function debounce(fn, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('registerForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const modelInput = document.getElementById('model');
    const deviceIdInput = document.getElementById('device_id');
    const phoneInput = document.getElementById('phone');

    const emailError = document.getElementById('emailError');
    const passwordError = document.getElementById('passwordError');
    const modelError = document.getElementById('modelError');
    const deviceIdError = document.getElementById('deviceIdError');
    const phoneError = document.getElementById('phoneError');
    const formError = document.getElementById('formError');
    const formSuccess = document.getElementById('formSuccess');

    // Debounced validation handlers
    emailInput.addEventListener('input', debounce(function () {
        emailError.textContent = '';
        const msg = validateRegisterEmail(emailInput.value.trim());
        if (msg) emailError.textContent = msg;
    }, 300));
    emailInput.addEventListener('blur', function () {
        const msg = validateRegisterEmail(emailInput.value.trim());
        emailError.textContent = msg;
    });

    passwordInput.addEventListener('input', debounce(function () {
        passwordError.textContent = '';
        const msg = validateRegisterPassword(passwordInput.value);
        if (msg) passwordError.textContent = msg;
    }, 300));
    passwordInput.addEventListener('blur', function () {
        const msg = validateRegisterPassword(passwordInput.value);
        passwordError.textContent = msg;
    });

    modelInput.addEventListener('input', debounce(function () {
        modelError.textContent = '';
        const msg = validateRegisterModel(modelInput.value.trim());
        if (msg) modelError.textContent = msg;
    }, 300));
    modelInput.addEventListener('blur', function () {
        const msg = validateRegisterModel(modelInput.value.trim());
        modelError.textContent = msg;
    });

    deviceIdInput.addEventListener('input', debounce(function () {
        deviceIdError.textContent = '';
        const msg = validateRegisterDeviceId(deviceIdInput.value.trim());
        if (msg) deviceIdError.textContent = msg;
    }, 300));
    deviceIdInput.addEventListener('blur', function () {
        const msg = validateRegisterDeviceId(deviceIdInput.value.trim());
        deviceIdError.textContent = msg;
    });

    phoneInput.addEventListener('input', debounce(function () {
        phoneError.textContent = '';
        const msg = validateRegisterPhone(phoneInput.value.trim());
        if (msg) phoneError.textContent = msg;
    }, 300));
    phoneInput.addEventListener('blur', function () {
        const msg = validateRegisterPhone(phoneInput.value.trim());
        phoneError.textContent = msg;
    });

    // Popup for success
    function showPopup(message, callback) {
        let popup = document.createElement('div');
        popup.className = 'popup-success';
        popup.innerHTML = `<div class="popup-content">
            <h3>Registration successful</h3>
            <p>${message}</p>
            <a href="/login" class="popup-link" style="display:none;opacity:0;transition:opacity 0.4s;">Back to Login</a>
        </div>`;
        document.body.appendChild(popup);
        setTimeout(() => {
            popup.classList.add('show');
            // Show the button after 1.2s
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
            window.location.href = '/login';
        };
    }

    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        emailError.textContent = '';
        passwordError.textContent = '';
        modelError.textContent = '';
        deviceIdError.textContent = '';
        phoneError.textContent = '';
        formError.textContent = '';
        formSuccess.textContent = '';

        const email = emailInput.value.trim();
        const password = passwordInput.value;
        const model = modelInput.value.trim();
        const device_id = deviceIdInput.value.trim();
        const phone = phoneInput.value.trim();

        let valid = true;

        const emailValidation = validateRegisterEmail(email);
        if (emailValidation) {
            emailError.textContent = emailValidation;
            valid = false;
        }
        const passwordValidation = validateRegisterPassword(password);
        if (passwordValidation) {
            passwordError.textContent = passwordValidation;
            valid = false;
        }
        const modelValidation = validateRegisterModel(model);
        if (modelValidation) {
            modelError.textContent = modelValidation;
            valid = false;
        }
        const deviceIdValidation = validateRegisterDeviceId(device_id);
        if (deviceIdValidation) {
            deviceIdError.textContent = deviceIdValidation;
            valid = false;
        }
        const phoneValidation = validateRegisterPhone(phone);
        if (phoneValidation) {
            phoneError.textContent = phoneValidation;
            valid = false;
        }
        if (!valid) return;

        const payload = {
            email,
            password,
            model,
            device_id,
        };
        if (phone) payload.phone = phone;

        try {
            const res = await fetch('http://localhost:4000/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (res.ok && data.message === 'Registration successful') {
                form.reset();
                showPopup('You have been registered successfully!', () => {
                    window.location.href = '/login';
                });
            } else {
                formError.textContent = data.error || (data.errors ? data.errors.join(', ') : 'Registration failed.');
            }
        } catch (err) {
            formError.textContent = 'Could not connect to server. Please try again later.';
        }
    });
}); 