import os
import time
from flask import Flask, request, jsonify, redirect, send_from_directory, render_template, Response, session
import requests
from flask_cors import CORS, cross_origin
from dotenv  import load_dotenv
import redis
import logging
from typing import Optional

# Load environment variables
load_dotenv()

# Configure Redis connection
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Configure logging
logging.basicConfig(level=logging.INFO, filename='login_attempts.log')

RATE_LIMIT = int(os.getenv('LOGIN_RATE_LIMIT', 5))
RATE_WINDOW = int(os.getenv('LOGIN_RATE_WINDOW', 900))  # 15 minutes in seconds

def get_rate_limit_key(email: str, ip: str) -> str:
    return f"rate_limit:{email}:{ip}"

def is_rate_limited(email: str, ip: str) -> tuple[bool, int]:
    key = get_rate_limit_key(email, ip)
    attempts_str = r.get(key)
    ttl = r.ttl(key) or RATE_WINDOW

    try:
        attempts = int(attempts_str) if attempts_str is not None else 0
    except ValueError:
        attempts = 0

    if attempts >= RATE_LIMIT:
        return True, ttl
    return False, ttl

def increment_attempt(email: str, ip: str) -> None:
    key = get_rate_limit_key(email, ip)
    if r.exists(key):
        r.incr(key)
    else:
        r.set(key, 1, ex=RATE_WINDOW)

def reset_attempts(email: str, ip: str) -> None:
    key = get_rate_limit_key(email, ip)
    r.delete(key)

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

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# === Health Check ===
# Removed: /api/health

# === Authentication ===
@app.route('/api/auth/login', methods=['POST'])
def proxy_login():
    data = request.json or {}
    email = data.get('email', '').strip()
    ip = request.remote_addr

    # Rate limiting check
    limited, retry_after = is_rate_limited(email, ip)
    if limited:
        logging.warning(f"Rate limit hit for {email} from {ip}")
        resp = jsonify({'error': 'Login attempts reached, please try again later.'})
        resp.status_code = 429
        resp.headers['Retry-After'] = str(retry_after if retry_after > 0 else RATE_WINDOW)
        return resp

    try:
        resp = requests.post(
            f"{LOCAL_API}/api/auth/login", 
            json=data,
            headers={"Content-Type": "application/json"},
            cookies=request.cookies
        )
        if resp.status_code == 200:
            reset_attempts(email, ip)
            # Store user session data securely
            session['logged_in'] = True
            session['user_email'] = data.get('email', '')
            session['device_id'] = data.get('device_id', '')
            session['login_time'] = int(time.time())
            return jsonify({"success": True, "message": "Login successful"}), 200
        else:
            increment_attempt(email, ip)
            logging.info(f"Failed login for {email} from {ip}")
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
# Removed: /api/auth/session

# === User Management ===
@app.route('/api/users/me', methods=['GET'])
def users_me():
    response, server = get_api_response('/api/users/me', 'GET')
    if response:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({'error': 'Failed to get user'}), 500

@app.route('/api/users/profile', methods=['GET'])
# Removed: /api/users/profile

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

# === Registration ===
@app.route('/api/auth/register', methods=['POST'])
@cross_origin()
def register():
    response, server = get_api_response('/api/auth/register', 'POST', request.json)
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
