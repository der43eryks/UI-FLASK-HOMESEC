# Home Security Web App

## Overview
This project is a Flask-based frontend for a home security system, acting as a proxy and UI for a backend API. It provides user authentication, device management, alert monitoring, and password reset features.

---

## API Endpoints Used

| Endpoint                        | Method | Description                                 |
|----------------------------------|--------|---------------------------------------------|
| /api/auth/register               | POST   | Register user and device                    |
| /api/auth/login                  | POST   | Login                                       |
| /api/auth/logout                 | POST   | Logout                                      |
| /api/users/me                    | GET    | Get user profile and device info            |
| /api/users/email                 | PUT    | Update user email                           |
| /api/users/phone                 | PUT    | Update user phone number                    |
| /api/users/password              | PUT    | Change user password                        |
| /api/devices/me                  | GET    | Get current device info                     |
| /api/devices/status              | GET    | Get current device status                   |
| /api/alerts                      | GET    | Get recent alerts for user/device           |
| /api/sse/alerts                  | GET    | Real-time alerts via SSE                    |
| /api/password-resets/request     | POST   | Request password reset                      |
| /api/password-resets/reset       | POST   | Reset password with token                   |

---

## Registration Flow
- User visits `/register` and fills out the form (email, password, model, device_id, phone [optional]).
- Frontend validates input (email format, required fields, phone format).
- On submit, frontend sends a POST request to `/api/auth/register` with the form data.
- On success, user is redirected to the login page.
- No backend email check is performed on the frontend; duplicate email errors are handled by the backend response.

## Login Flow
- User visits `/login` and enters email, password, and device ID.
- Frontend sends a POST request to `/api/auth/login`.
- On success, user is redirected to the dashboard.

## Other Features
- Device and alert information is available via the dashboard after login.
- Password reset is available via the appropriate endpoints.

## Notes
- All endpoints except registration, login, logout, and password reset require authentication (cookie/session).
- CORS is enabled for the registration endpoint.
- The frontend does not attempt to check if an email is registered before submitting the registration form.

---

## Project Structure
- `app.py` — Flask app and proxy routes
- `templates/` — HTML templates (login, register, dashboard)
- `static/js/` — Frontend JavaScript (login, register, dashboard)
- `static/css/` — Stylesheets

---

## Setup
1. Install dependencies from `requirements.txt`.
2. Set up your `.env` file with the correct backend API URL and secret key.
3. Run the Flask app: `python app.py`
4. Access the app at `http://localhost:10000` (or your configured port).

---

## License
MIT
