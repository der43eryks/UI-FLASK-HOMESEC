// Register page validation functions

export function validateRegisterEmail(email) {
    if (!email) return 'Email is required.';
    if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email))
        return 'Enter a valid email address (e.g., testa@gmail.com).';
    if (/[^a-zA-Z0-9@._-]/.test(email))
        return 'Email cannot contain special symbols except @, ., _, and -.';
    return '';
}

export function validateRegisterPassword(password) {
    if (!password) return 'Password is required.';
    if (!/^\d{8,16}$/.test(password))
        return 'Password must be 8-16 digits and contain only numbers.';
    if (password !== '12345678')
        return 'Password must be exactly 12345678.';
    return '';
}

export function validateRegisterPhone(phone) {
    if (!phone) return '';
    if (!/^(01|07)\d{8}$/.test(phone))
        return 'Phone number must start with 01 or 07 and be 10 digits (e.g., 0756000000).';
    return '';
}

export function validateRegisterDeviceId(deviceId) {
    if (!deviceId) return 'Device ID is required.';
    if (!/^\d+$/.test(deviceId))
        return 'Device ID must be numeric (e.g., 23456786).';
    return '';
}

export function validateRegisterModel(model) {
    if (!model) return 'Model is required.';
    return '';
} 