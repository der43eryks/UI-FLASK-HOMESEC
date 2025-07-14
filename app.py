import os
import time
from flask import Flask, request, jsonify, redirect, send_from_directory, render_template, Response, session
import requests
from flask_cors import CORS
from dotenv  import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_url_path='/static')
CORS(app, supports_credentials=True)

# Flask Configuration with Secure Session Management
app.config.update(
    SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'fallback-secret-key-change-in-production'),
    SESSION_COOKIE_SECURE=True,      # Only send cookie over HTTPS
    SESSION_COOKIE_HTTPONLY=True,    # Prevent JavaScript access to cookie
    SESSION_COOKIE_SAMESITE='Lax',   # Mitigate CSRF attacks
    SESSION_COOKIE_MAX_AGE=3600,     # Session expires in 1 hour
    PERMANENT_SESSION_LIFETIME=3600  # Session lifetime in seconds
)


#BACKEND/API URL (for all proxied API calls)
#ONLINE_API = os.getenv('ONLINE_API_URL','LOCAL_API = os.getenv('LOCAL_API_URL', ONLINE_API)
LOCAL_API = os.getenv('BACKEND_URL')
API_TIMEOUT = int(os.getenv('API_TIMEOUT', 2))


def get_api_response(endpoint, method='GET', data=None, timeout=API_TIMEOUT):
    """
    Send a request to the local backend API and return the response.
    """
    url = f'{LOCAL_API}{endpoint}'
    try:
        if method == 'GET':
            response = requests.get(url, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=timeout)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        if response is not None:
            print(f"✅ Using local server for {endpoint} (status: {response.status_code})")
            print(f"Response body: {response.text}")
            return response, 'local'  # Return any HTTP response, not just 200
    except Exception as e:
        print(f"❌ Local server failed for {endpoint}: {str(e)}")
    return None, None

# === Session Management Helper ===
def is_user_logged_in():
    """Check if user is logged in and session is valid"""
    if not session.get('logged_in'):
        return False
    
    # Check if session has expired (1 hour)
    login_time = session.get('login_time', 0)
    if time.time() - login_time > 3600:
        session.clear()
        return False
    
    return True

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
        return jsonify({'error': 'Backend unavailable or error occurred'}), 500

# === Authentication ===
@app.route('/api/auth/login', methods=['POST'])
def proxy_login():
    data = request.json or {}
    try:
        resp = requests.post(
            f"{LOCAL_API}/api/auth/login", 
            json=data,
            headers={"Content-Type": "application/json"},
            cookies=request.cookies
        )
        if resp.status_code == 200:
            # Store user session data securely
            session['logged_in'] = True
            session['user_email'] = data.get('email', '') # data.get('email', '')
            session['device_id'] = data.get('device_id', '') #try fill the whole cookie with the expected json data
            session['login_time'] = int(time.time())
            
            return jsonify({"success": True, "message": "Login successful"}), 200
        else:
            return jsonify({"success": False, "error": resp.json().get("error", "Login failed")}), resp.status_code
    except Exception as e:
        return jsonify({"success": False, "error": "An error occurred while logging in."}), 500

@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    # Clear Flask session
    session.clear()
    
    # Forward logout request to backend
    response, server = get_api_response('/api/auth/logout', 'POST')
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'error': 'Backend unavailable or error occurred'}), 500

# === Session Check ===
@app.route('/api/auth/session', methods=['GET'])
def check_session():
    """Check if user session is valid"""
    if is_user_logged_in():
        return jsonify({
            "logged_in": True,
            "user_email": session.get('user_email', ''),
            "device_id" : session.get('device_id', ''),
            "login_time": session.get('login_time', 0)
        }), 200
    else:
        #print('401 error alwasys ')
        return jsonify({"logged_in": False}), 401

# === User Management ===
@app.route('/api/users/me', methods=['GET'])
def users_me():
    response, server = get_api_response('/api/users/me', 'GET')
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'error': 'Failed to get user'}), 500

@app.route('/api/users/profile', methods=['GET'])
def proxy_user_profile():
    try:
        resp = requests.get(
            f"{LOCAL_API}/api/users/profile",
            cookies=request.cookies
        )
        if resp.status_code == 200:
            return jsonify(resp.json()), 200
        else:
            return jsonify({"error": resp.json().get("error", "Failed to retrieve user profile")}), resp.status_code
    except Exception as e:
        return jsonify({"error": "An error occurred while retrieving user profile."}), 500

@app.route('/api/users/email', methods=['PUT'])
def update_email():
    response, server = get_api_response('/api/users/email', 'PUT', request.json)
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'error': 'Backend unavailable or error occurred'}), 500

@app.route('/api/users/phone', methods=['PUT'])
def update_phone():
    response, server = get_api_response('/api/users/phone', 'PUT', request.json)
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'error': 'Backend unavailable or error occurred'}), 500

@app.route('/api/users/password', methods=['PUT'])
def update_password():
    response, server = get_api_response('/api/users/password', 'PUT', request.json)
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'error': 'Backend unavailable or error occurred'}), 500

# === Device Management ===
@app.route('/api/devices/me', methods=['GET'])
def devices_me():
    response, server = get_api_response('/api/devices/me', 'GET')
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'error': 'Backend unavailable or error occurred'}), 500

@app.route('/api/devices/status', methods=['GET'])
def devices_status():
    response, server = get_api_response('/api/devices/status', 'GET')
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'error': 'Backend unavailable or error occurred'}), 500

# === Alerts ===
@app.route('/api/alerts', methods=['GET'])
def alerts():
    response, server = get_api_response('/api/alerts', 'GET')
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'error': 'Failure to get alerts'}), 500

@app.route('/api/sse/alerts', methods=['GET'])
def proxy_sse_alerts():
    def generate():
        backend_url = f"{LOCAL_API}/api/sse/alerts"
        headers = {"Accept": "text/event-stream"}
        while True:
            try:
                with requests.get(backend_url, stream=True, headers=headers, timeout=60) as resp:
                    for line in resp.iter_lines():
                        if line:
                            data = line.decode('utf-8')
                            if data.startswith('data: '):
                                yield f"data: {data[6:]}\n\n"
            except Exception as e:
                print(f"SSE proxy error: {e}")
                yield f"data: {{\"error\": \"SSE connection error, retrying...\"}}\n\n"
                import time
                time.sleep(5)  # Wait before reconnecting
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
        return jsonify({'error': 'error occurred while logging in'}), 500

@app.route('/api/password-resets/reset', methods=['POST'])
def password_reset_reset():
    response, server = get_api_response('/api/password-resets/reset', 'POST', request.json)
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'error': 'Backend unavailable or error occurred'}), 500

# # Make ONLINE_CLIENT_RENDER available in all templates
# @app.context_processor
# def inject_online_client_render():
#     return dict(ONLINE_CLIENT_RENDER=ONLINE_CLIENT_RENDER)

# === Run the Server ===
if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(debug=False, host='0.0.0.0', port=port)
