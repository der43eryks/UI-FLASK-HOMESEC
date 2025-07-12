from flask import Flask, request, jsonify, redirect, send_from_directory, render_template
import requests
from flask_cors import CORS

app = Flask(__name__, static_url_path='/static')
CORS(app, supports_credentials=True)

API_BASE = 'https://homesecurity-cw0e.onrender.com'

# === Frontend Pages ===
@app.route('/')
def home():
    return redirect('/login')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# === Authentication ===
@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    data = request.json

    # ✅ Development-only test user
    if data['email'] == 'admin@test.com' and data['password'] == 'admin123':
        return jsonify({
            "message": "Login successful",
            "user": {
                "email": data['email'],
                "name": "Admin Tester"
            }
        }), 200

    # 🔄 Otherwise, try real API
    try:
        response = requests.post(f'{API_BASE}/api/auth/login', json=data)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    try:
        response = requests.post(f'{API_BASE}/api/auth/logout')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# === User Management ===
@app.route('/api/users/me', methods=['GET'])
def users_me():
    try:
        response = requests.get(f'{API_BASE}/api/users/me')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/users/email', methods=['PUT'])
def update_email():
    try:
        response = requests.put(f'{API_BASE}/api/users/email', json=request.json)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/users/phone', methods=['PUT'])
def update_phone():
    try:
        response = requests.put(f'{API_BASE}/api/users/phone', json=request.json)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/users/password', methods=['PUT'])
def update_password():
    try:
        response = requests.put(f'{API_BASE}/api/users/password', json=request.json)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# === Device Info ===
@app.route('/api/devices/me', methods=['GET'])
def devices_me():
    try:
        response = requests.get(f'{API_BASE}/api/devices/me')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/devices/status', methods=['GET'])
def devices_status():
    try:
        response = requests.get(f'{API_BASE}/api/devices/status')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# === Alerts ===
@app.route('/api/alerts', methods=['GET'])
def alerts():
    try:
        response = requests.get(f'{API_BASE}/api/alerts')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/sse/alerts', methods=['GET'])
def sse_alerts():
    try:
        response = requests.get(f'{API_BASE}/api/sse/alerts', stream=True)
        return response.raw.read(), response.status_code, response.headers.items()
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# === Password Resets ===
@app.route('/api/password-resets/request', methods=['POST'])
def password_reset_request():
    try:
        response = requests.post(f'{API_BASE}/api/password-resets/request', json=request.json)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/password-resets/reset', methods=['POST'])
def password_reset_reset():
    try:
        response = requests.post(f'{API_BASE}/api/password-resets/reset', json=request.json)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# === Run the Server ===
if __name__ == '__main__':
    app.run(debug=True)
