# Smart Security Dashboard

A modern web application for managing home security systems with real-time monitoring and control capabilities.

## 🏗️ Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── render.yaml            # Render deployment config
├── README.md              # Project documentation
├── templates/             # HTML templates
│   ├── login.html         # Login page template
│   └── dashboard.html     # Dashboard template
└── static/                # Static assets
    ├── css/               # Stylesheets
    │   ├── login.css      # Login page styles
    │   └── dashboard.css  # Dashboard styles
    ├── js/                # JavaScript files
    │   ├── login.js       # Login functionality
    │   └── dashboard.js   # Dashboard functionality
    └── images/            # Images and icons
        └── favicon.ico    # Site favicon
```

## 📦 Version Control & .gitignore

- The following are **always ignored** by git (see `.gitignore`):
  - `venv/` (Python virtual environment)
  - `__pycache__/` (Python bytecode cache)
  - All test scripts (e.g., `test_*.py`, `*test*.py`)
- **Only these files/folders are tracked in version control:**
  - `requirements.txt`
  - `app.py`
  - `README.md`
  - `render.yaml`
  - `templates/`
  - `static/`
- **Never commit or push your `venv` folder or test scripts.**
- If you accidentally committed `venv`, remove it with:
  ```bash
  git rm -r --cached venv
  git commit -m "Remove venv from version control"
  git push
  ```
- When adding files, use:
  ```bash
  git add requirements.txt app.py README.md render.yaml templates static
  ```
  (Do **not** use `git add .`)

## 🚀 Features

- **User Authentication**: Secure login system with session management
- **Real-time Monitoring**: Live status updates for security devices
- **Device Control**: Remote control of locks, lights, and sensors
- **Alert System**: Real-time notifications for security events
- **User Profile**: Manage account settings and password changes
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the development server**:
   ```bash
   python app.py
   ```

3. **Access the application**:
   - Open http://localhost:10000
   - Use test credentials: `admin@test.com` / `admin123`

## 🌐 Deployment

### Render Deployment

1. **Deploy to Render**:
   - Connect your GitHub repository to Render
   - Render will automatically detect the Python project
   - Use the `render.yaml` configuration file for deployment settings

2. **Manual Deployment**:
   ```bash
   git add requirements.txt app.py README.md render.yaml templates static
   git commit -m "Deploy to Render"
   git push origin main
   ```

3. **Environment Variables** (if needed):
   - Go to Render dashboard
   - Add any required environment variables in the service settings

4. **Production WSGI Server**:
   - The app uses `gunicorn` for production deployment (see `render.yaml`)

## 🔧 API Endpoints

### Health Check
- `GET /api/health` - Check server and database status

### Authentication
- `POST /api/auth/login` - User login with email, password, and device_id
- `POST /api/auth/logout` - User logout (clears authentication cookie)
- `GET /api/auth/session` - Check current session status and user info

### User Management
- `GET /api/users/me` - Get current user profile and device information
- `PUT /api/users/email` - Update user email address
- `PUT /api/users/phone` - Update user phone number
- `PUT /api/users/password` - Change user password (requires old password)

### Device Management
- `GET /api/devices/me` - Get current device information
- `GET /api/devices/status` - Get current device status (online/offline)

### Alerts
- `GET /api/alerts` - Get user's alert history
- `GET /api/sse/alerts` - Server-Sent Events stream for real-time alerts

### Password Reset
- `POST /api/password-resets/request` - Request password reset (requires email and device_id)
- `POST /api/password-resets/reset` - Reset password with token

## 🎨 Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Custom CSS with responsive design
- **Deployment**: Render (with gunicorn)
- **API**: RESTful API with JSON responses

## 📱 Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## 🔒 Security Features

- **Secure Session Management**: Flask sessions with encrypted cookies
- **CSRF Protection**: SameSite cookie policy and CSRF tokens
- **Secure Password Handling**: Password validation and secure storage
- **Input Validation**: Server-side validation for all user inputs
- **XSS Prevention**: Content Security Policy and input sanitization
- **HTTPS Enforcement**: Secure cookies only sent over HTTPS
- **Session Expiration**: Automatic session timeout (1 hour)
- **Secret Key Management**: Environment-based secret key configuration

## 📄 License

This project is licensed under the MIT License.

## ⚡ Improved Error Handling

- The Flask backend now treats any HTTP response (not just 200 OK) from the backend API as a valid response.
- This means users will see accurate backend error messages (e.g., invalid credentials, validation errors) instead of always seeing 'Both servers unavailable' for non-200 responses.
- Debug logging for backend status code and response body is enabled in `get_api_response` for easier troubleshooting.

## 🚨 Production Error Handling

In production, user-facing error messages are designed to be friendly, secure, and non-technical. Examples include:
- "An unexpected error occurred. Please try again later."
- "Unable to log in at this time. Please try again later."
- "You do not have permission to perform this action."
- "The requested resource was not found."
- "Service is temporarily unavailable. Please try again soon."

**Best Practices:**
- Never expose technical details, stack traces, or internal server errors to users.
- Log detailed errors on the server for developers/ops.
- Show generic, actionable messages to users.
- Provide a support contact or help link for persistent issues.

All API endpoints in this project follow these guidelines for error handling.
