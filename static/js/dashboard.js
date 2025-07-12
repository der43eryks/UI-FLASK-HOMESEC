async function fetchDeviceStatuses() {
    try {
        const res = await fetch('/api/devices/status');
        const data = await res.json();

        // Motion Sensor
        const motion = document.getElementById('motionSensor');
        const motionText = motion.querySelector('.status-text');
        if (data.motionSensor === 'active') {
            motion.classList.add('active'); motion.classList.remove('inactive');
            motionText.textContent = "Motion Detected!";
        } else {
            motion.classList.add('inactive'); motion.classList.remove('active');
            motionText.textContent = "No Motion";
        }

        // Distance Sensor
        const distance = document.getElementById('distanceSensor');
        distance.querySelector('.status-text').textContent = data.distanceSensor + " meters";

        // RFID
        const rfid = document.getElementById('rfidReader');
        const rfidText = rfid.querySelector('.status-text');
        if (data.rfidReader) {
            rfidText.textContent = data.rfidReader;
            rfid.classList.add('active'); rfid.classList.remove('inactive');
        } else {
            rfidText.textContent = "None";
            rfid.classList.remove('active'); rfid.classList.add('inactive');
        }

        // Doors & Window
        ['frontDoor', 'backDoor', 'window1'].forEach(id => {
            const el = document.getElementById(id);
            const status = data[id];
            const span = el.querySelector('.status-text');
            if (status === 'locked') {
                el.classList.add('locked'); el.classList.remove('unlocked');
                span.textContent = "Locked";
            } else {
                el.classList.add('unlocked'); el.classList.remove('locked');
                span.textContent = "Unlocked";
            }
        });

        // LED
        const led = document.getElementById('ledLight');
        const ledText = led.querySelector('.status-text');
        if (data.ledLight === 'on') {
            led.classList.add('led-on'); led.classList.remove('led-off');
            ledText.textContent = "On";
        } else {
            led.classList.add('led-off'); led.classList.remove('led-on');
            ledText.textContent = "Off";
        }

    } catch (err) {
        console.error("Error fetching status:", err);
    }
}

// Device control functions removed - not in official endpoint list
// function toggleLock(deviceId) { ... }
// function toggleLed() { ... }

function addAlert(message) {
    const alertsList = document.getElementById('alertsList');
    const newAlert = document.createElement('li');
    newAlert.textContent = new Date().toLocaleTimeString() + " - " + message;
    alertsList.prepend(newAlert);
    if (alertsList.children.length > 1 && alertsList.lastChild.textContent === "No alerts at the moment")
        alertsList.removeChild(alertsList.lastChild);
}

function openProfileModal() {
    document.getElementById('profileModal').style.display = 'flex';
    document.getElementById('passwordChangeSection').style.display = 'none';
}

function closeProfileModal() {
    document.getElementById('profileModal').style.display = 'none';
}

function togglePasswordChangeSection() {
    const section = document.getElementById('passwordChangeSection');
    section.style.display = section.style.display === 'none' ? 'block' : 'none';
}

async function saveProfile() {
    const phone = document.getElementById('phoneNumber').value;
    const email = document.getElementById('email').value;
    await fetch('/api/users/phone', {
        method: 'PUT', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone })
    });
    await fetch('/api/users/email', {
        method: 'PUT', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
    });
    alert("Profile saved");
}

async function changePassword() {
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirm = document.getElementById('confirmNewPassword').value;
    if (newPassword !== confirm) return alert("Passwords don't match.");
    const res = await fetch('/api/users/password', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ currentPassword, newPassword })
    });
    const data = await res.json();
    if (!res.ok) return alert("Error: " + data.message);
    alert("Password changed");
    closeProfileModal();
}

async function resetPassword() {
    const email = document.getElementById('email').value;
    const res = await fetch('/api/password-resets/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
    });
    const data = await res.json();
    if (!res.ok) return alert("Error: " + data.message);
    alert("Reset link sent");
}

function signOut() {
    sessionStorage.clear();
    window.location.href = "/login";
}

document.addEventListener('DOMContentLoaded', () => {
    fetchDeviceStatuses();
    setInterval(fetchDeviceStatuses, 3000);
}); 