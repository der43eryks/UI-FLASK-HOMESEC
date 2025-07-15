import os
import time
from flask import Flask, request, jsonify, redirect, send_from_directory, render_template, Response, session
import requests
from flask_cors import CORS, cross_origin
from dotenv  import load_dotenv
import logging
from typing import Optional

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, filename='login_attempts.log')

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
# Load both backend URLs
LOCAL_API = os.getenv('BACKEND_URL')
FALLBACK_API = os.getenv('FALLBACK_BACKEND_URL')

# Optional: allow forcing fallback only
USE_FALLBACK_ONLY = os.getenv('USE_FALLBACK_ONLY', 'false').lower() == 'true'


API_TIMEOUT = int(os.getenv('API_TIMEOUT', 2))


def get_api_response(endpoint, method='GET', data=None, timeout=API_TIMEOUT):
    # Try main backend first, then fallback if needed
    urls = [FALLBACK_API] if USE_FALLBACK_ONLY else [LOCAL_API, FALLBACK_API]
    for base_url in urls:
        if not base_url:
            continue
        url = f'{base_url}{endpoint}'
        print(f"🔍 API Request - Method: {method}, URL: {url}")
        print(f"🔍 API Request - Data: {data}")
        try:
            headers = {"Content-Type": "application/json"}
            req_args = {
                'url': url,
                'headers': headers,
                'cookies': request.cookies,
                'timeout': timeout
            }
            if method == 'GET':
                response = requests.get(**req_args)
            elif method == 'POST':
                req_args['json'] = data
                response = requests.post(**req_args)
            elif method == 'PUT':
                req_args['json'] = data
                response = requests.put(**req_args)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            print(f"✅ Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            return response, base_url
        except Exception as e:
            print(f"❌ Request error for {base_url}: {str(e)}")
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
    print(f"🔍 Login attempt - Data: {data}")
    print(f"🔍 Backend URL: {LOCAL_API}/api/auth/login")
    
    try:
        resp = requests.post(
            f"{LOCAL_API}/api/auth/login", 
            json=data,
            headers={"Content-Type": "application/json"},
            cookies=request.cookies
        )
        print(f"🔍 Express response status: {resp.status_code}")
        print(f"🔍 Express response body: {resp.text}")
        
        if resp.status_code == 200:
            # ✅ Forward Set-Cookie header to browser
            flask_response = jsonify({"success": True, "message": "Login successful"})
            if 'set-cookie' in resp.headers:
                flask_response.headers['Set-Cookie'] = resp.headers['set-cookie']
            
            # Set Flask session (optional)
            session['logged_in'] = True
            session['user_email'] = data.get('email', '').strip()
            session['device_id'] = data.get('device_id', '').strip()
            session['login_time'] = int(time.time())
            print(f"✅ Login successful for {data.get('email', '')}")
            
            return flask_response, 200
        else:
            logging.info(f"Failed login for {data.get('email', '')} from {request.remote_addr}")
            print(f"❌ Login failed - Status: {resp.status_code}, Response: {resp.text}")
            return jsonify({"success": False, "error": resp.json().get("error", "Login failed")}), resp.status_code
    except Exception as e:
        print(f"❌ Error during login: {str(e)}")
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

@app.route('/debug-cookies')
def debug_cookies():
    return jsonify(dict(request.cookies))
