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

    async function isEmailRegistered(email) {
        // Try to check if email is registered (assumes backend endpoint exists)
        try {
            const res = await fetch(`http://localhost:4000/api/users/check-email?email=${encodeURIComponent(email)}`);
            if (res.ok) {
                const data = await res.json();
                return data.exists === true;
            }
        } catch (e) {}
        return false; // If check fails, allow registration to proceed
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
        const password = passwordInput.value; // always '12345678'
        const model = modelInput.value.trim();
        const device_id = deviceIdInput.value.trim();
        const phone = phoneInput.value.trim();

        let valid = true;

        // Validate email
        if (!email) {
            emailError.textContent = 'Email is required.';
            valid = false;
        } else if (!validateEmail(email)) {
            emailError.textContent = 'Invalid email format.';
            valid = false;
        } else if (await isEmailRegistered(email)) {
            emailError.textContent = 'Email is already registered.';
            valid = false;
        }

        // Validate model
        if (!model) {
            modelError.textContent = 'Model is required.';
            valid = false;
        }

        // Validate device_id
        if (!device_id) {
            deviceIdError.textContent = 'Device ID is required.';
            valid = false;
        }

        // Optionally validate phone (e.g., length or format)
        if (phone && !/^\+?\d{7,15}$/.test(phone)) {
            phoneError.textContent = 'Invalid phone number.';
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