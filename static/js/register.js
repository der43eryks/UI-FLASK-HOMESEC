import {
  validateRegisterEmail,
  validateRegisterPassword,
  validateRegisterPhone,
  validateRegisterDeviceId,
  validateRegisterModel
} from './validation/registerValidations.js';

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

    function validateEmail(email) {
        // Simple email regex
        return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
    }

    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        // Clear errors
        emailError.textContent = '';
        passwordError.textContent = '';
        modelError.textContent = '';
        deviceIdError.textContent = '';
        phoneError.textContent = '';
        formError.textContent = '';
        formSuccess.textContent = '';

        // Get values
        const email = emailInput.value.trim();
        const password = passwordInput.value;
        const model = modelInput.value.trim();
        const device_id = deviceIdInput.value.trim();
        const phone = phoneInput.value.trim();

        let valid = true;

        // Validate email
        const emailValidation = validateRegisterEmail(email);
        if (emailValidation) {
            emailError.textContent = emailValidation;
            valid = false;
        }

        // Validate password
        const passwordValidation = validateRegisterPassword(password);
        if (passwordValidation) {
            passwordError.textContent = passwordValidation;
            valid = false;
        }

        // Validate model
        const modelValidation = validateRegisterModel(model);
        if (modelValidation) {
            modelError.textContent = modelValidation;
            valid = false;
        }

        // Validate device_id
        const deviceIdValidation = validateRegisterDeviceId(device_id);
        if (deviceIdValidation) {
            deviceIdError.textContent = deviceIdValidation;
            valid = false;
        }

        // Validate phone
        const phoneValidation = validateRegisterPhone(phone);
        if (phoneValidation) {
            phoneError.textContent = phoneValidation;
            valid = false;
        }

        if (!valid) return;

        // Prepare data
        const payload = {
            email,
            password,
            model,
            device_id,
        };
        if (phone) payload.phone = phone;

        // Send registration request
        try {
            const res = await fetch('http://localhost:4000/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (res.ok && data.message === 'Registration successful') {
                formSuccess.textContent = 'Registration successful! Redirecting to login...';
                form.reset();
                passwordInput.value = '12345678';
                setTimeout(() => {
                    window.location.href = '/login';
                }, 1500);
            } else {
                formError.textContent = data.error || (data.errors ? data.errors.join(', ') : 'Registration failed.');
            }
        } catch (err) {
            formError.textContent = 'Could not connect to server. Please try again later.';
        }
    });
}); 