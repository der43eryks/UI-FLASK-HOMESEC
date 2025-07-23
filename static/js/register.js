import {
  validateRegisterEmail,
  validateRegisterPassword,
  validateRegisterPhone,
  validateRegisterDeviceId,
  validateRegisterModel,
  validateRegisterName
} from './validation/registerValidations.js';

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
  deviceId: 12,
  model: 30,
  phone: 10,
  name: 20
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
    const form = document.getElementById('registerForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const modelInput = document.getElementById('model');
    const deviceIdInput = document.getElementById('device_id');
    const phoneInput = document.getElementById('phone');
    const nameInput = document.getElementById('name');

    const emailError = document.getElementById('emailError');
    const passwordError = document.getElementById('passwordError');
    const modelError = document.getElementById('modelError');
    const deviceIdError = document.getElementById('deviceIdError');
    const phoneError = document.getElementById('phoneError');
    const nameError = document.getElementById('nameError');
    const formError = document.getElementById('formError');
    const formSuccess = document.getElementById('formSuccess');

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

    attachValidation(emailInput, validateRegisterEmail);
    attachValidation(passwordInput, validateRegisterPassword);
    attachValidation(modelInput, validateRegisterModel);
    attachValidation(deviceIdInput, validateRegisterDeviceId);
    attachValidation(phoneInput, validateRegisterPhone);
    attachValidation(nameInput, validateRegisterName);

    // Enforce max length and show error
    enforceMaxLength(emailInput, MAX_LENGTHS.email, 'Email cannot exceed 50 characters.');
    enforceMaxLength(passwordInput, MAX_LENGTHS.password, 'Password cannot exceed 16 digits.');
    enforceMaxLength(modelInput, MAX_LENGTHS.model, 'Model cannot exceed 30 characters.');
    enforceMaxLength(deviceIdInput, MAX_LENGTHS.deviceId, 'Device ID cannot exceed 12 digits.');
    enforceMaxLength(phoneInput, MAX_LENGTHS.phone, 'Phone cannot exceed 10 digits.');
    enforceMaxLength(nameInput, MAX_LENGTHS.name, 'Device name cannot exceed 20 characters.');

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
        nameError.textContent = '';
        formError.textContent = '';
        formSuccess.textContent = '';

        const email = emailInput.value.trim();
        const password = passwordInput.value;
        const model = modelInput.value.trim();
        const device_id = deviceIdInput.value.trim();
        const phone = phoneInput.value.trim();
        const name = nameInput.value.trim();

        let valid = true;

        const emailValidation = validateRegisterEmail(email);
        if (emailValidation) {
            showValidation(emailInput, emailValidation);
            valid = false;
        }
        const passwordValidation = validateRegisterPassword(password);
        if (passwordValidation) {
            showValidation(passwordInput, passwordValidation);
            valid = false;
        }
        const modelValidation = validateRegisterModel(model);
        if (modelValidation) {
            showValidation(modelInput, modelValidation);
            valid = false;
        }
        const deviceIdValidation = validateRegisterDeviceId(device_id);
        if (deviceIdValidation) {
            showValidation(deviceIdInput, deviceIdValidation);
            valid = false;
        }
        const phoneValidation = validateRegisterPhone(phone);
        if (phoneValidation) {
            showValidation(phoneInput, phoneValidation);
            valid = false;
        }
        const nameValidation = validateRegisterName(name);
        if (nameValidation) {
            showValidation(nameInput, nameValidation);
            valid = false;
        }
        if (!valid) return;

        const payload = {
            email,
            password,
            model,
            device_id,
            name,
        };
        if (phone) payload.phone = phone;

        try {
            const BACKEND_URL = window.BACKEND_URL;
            const res = await fetch(`${BACKEND_URL}/api/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                credentials: 'include'
            });
            const data = await res.json();
            //this is the main issue
            if (res.ok && data.message === 'Registration successful') {
                form.reset();
                showPopup('You have been registered successfully!', () => {
                    window.location.href = '/login';
                });
            } else {
                formError.textContent = data.error || (data.errors ? data.errors.join(', ') : 'Registration failed please try again.');
            }
        } catch (err) {
            formError.textContent = 'Could not connect to server. Please try again later.';
        }
    });
}); 