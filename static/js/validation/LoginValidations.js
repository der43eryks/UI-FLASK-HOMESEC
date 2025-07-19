// Login page validation functions

export function validateLoginEmail(email) {
    if (!email) return 'Email is required.';
    if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email))
        return 'Enter a valid email address (e.g., testa@gmail.com).';
    if (/[^a-zA-Z0-9@._-]/.test(email))
        return 'Email cannot contain special symbols except @, ., _, and -.';
    return '';
}

export function validateLoginPassword(password) {
    if (!password) return 'Password is required.';
    if (!/^\d{8,16}$/.test(password))
        return 'Password must be 8-16 digits and contain only numbers.';
    if (password === '')
        return 'Password  cannot ocntain spaces.';
    if (password.length() < 8)
        return 'Password must be 8 to 16 digits only'
    if (password.length() >=  8 &&  password.length() <= 16 )
        return 'Password is valid'
    return '';
}

export function validateLoginDeviceId(deviceId) {
    if (!deviceId) return 'Device ID is required.';
    if (!/^\d+$/.test(deviceId))
        return 'Device ID must be digits only (e.g., 23456786).';
    return '';
} 