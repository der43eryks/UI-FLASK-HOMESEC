import os
from flask import Flask, request, jsonify, redirect, send_from_directory, render_template, Response
import requests
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_url_path='/static')
CORS(app, supports_credentials=True)

LOCAL_API = os.getenv('LOCAL_API_URL')
ONLINE_API = os.getenv('ONLINE_API_URL')
API_TIMEOUT = int(os.getenv('API_TIMEOUT', 2))


def get_api_response(endpoint, method='GET', data=None, timeout=API_TIMEOUT):
    """
    Try local server first, then fallback to online server
    Returns (response, server_used) tuple
    """
    servers = [
        (LOCAL_API, 'local'),
        (ONLINE_API, 'online')
    ]
    for server_url, server_name in servers:
        try:
            url = f'{server_url}{endpoint}'
            if method == 'GET':
                response = requests.get(url, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, timeout=timeout)
            if response is not None:
                print(f"✅ Using {server_name} server for {endpoint}")
                return response, server_name
        except Exception as e:
            print(f"❌ {server_name} server failed for {endpoint}: {str(e)}")
            continue
    return None, None

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

# === Health Check ===
@app.route('/api/health', methods=['GET'])
def health_check():
    response, server = get_api_response('/api/health', 'GET')
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'message': 'Both servers unavailable'}), 500

# === Authentication ===
@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    data = request.json
    if data['email'] == 'admin@test.com' and data['password'] == 'admin123':
        return jsonify({
            "message": "Login successful",
            "user": {
                "email": data['email'],
                "name": "Admin Tester"
            }
        }), 200
    response, server = get_api_response('/api/auth/login', 'POST', data)
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'message': 'Both servers unavailable'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    response, server = get_api_response('/api/auth/logout', 'POST')
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'message': 'Both servers unavailable'}), 500

# === User Management ===
@app.route('/api/users/me', methods=['GET'])
def users_me():
    response, server = get_api_response('/api/users/me', 'GET')
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'message': 'Both servers unavailable'}), 500

@app.route('/api/users/email', methods=['PUT'])
def update_email():
    response, server = get_api_response('/api/users/email', 'PUT', request.json)
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'message': 'Both servers unavailable'}), 500

@app.route('/api/users/phone', methods=['PUT'])
def update_phone():
    response, server = get_api_response('/api/users/phone', 'PUT', request.json)
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'message': 'Both servers unavailable'}), 500

@app.route('/api/users/password', methods=['PUT'])
def update_password():
    response, server = get_api_response('/api/users/password', 'PUT', request.json)
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'message': 'Both servers unavailable'}), 500

# === Device Management ===
@app.route('/api/devices/me', methods=['GET'])
def devices_me():
    response, server = get_api_response('/api/devices/me', 'GET')
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'message': 'Both servers unavailable'}), 500

@app.route('/api/devices/status', methods=['GET'])
def devices_status():
    response, server = get_api_response('/api/devices/status', 'GET')
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'message': 'Both servers unavailable'}), 500

# === Alerts ===
@app.route('/api/alerts', methods=['GET'])
def alerts():
    response, server = get_api_response('/api/alerts', 'GET')
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'message': 'Both servers unavailable'}), 500

@app.route('/api/sse/alerts', methods=['GET'])
def sse_alerts():
    def generate():
        servers = [
            (LOCAL_API, 'local'),
            (ONLINE_API, 'online')
        ]
        
        for server_url, server_name in servers:
            if not server_url:
                continue
            try:
                response = requests.get(f'{server_url}/api/sse/alerts', stream=True, timeout=API_TIMEOUT)
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        yield f"data: {chunk.decode('utf-8')}\n\n"
                break  # If successful, don't try the next server
            except Exception as e:
                print(f"❌ {server_name} SSE server failed: {str(e)}")
                continue
        
        # If all servers fail, send error
        yield f"data: {{\"error\": \"All servers unavailable\"}}\n\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true'
        }
    )

# === Password Resets ===
@app.route('/api/password-resets/request', methods=['POST'])
def password_reset_request():
    response, server = get_api_response('/api/password-resets/request', 'POST', request.json)
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'message': 'Both servers unavailable'}), 500

@app.route('/api/password-resets/reset', methods=['POST'])
def password_reset_reset():
    response, server = get_api_response('/api/password-resets/reset', 'POST', request.json)
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'message': 'Both servers unavailable'}), 500

# === Run the Server ===
if __name__ == '__main__':
    app.run(debug=True, port=int(os.getenv('FLASK_PORT', 5000)))
