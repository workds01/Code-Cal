# Ava's Day Care Roster

A web application to manage and view Ava's day care schedule.

## Features

- Public view of care schedule with password protection
- Administrative access to modify schedules
- Calendar view of care assignments
- Secure authentication system

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access the website at `http://localhost:5000`

## Default Login Credentials

- Admin User:
  - Username: admin
  - Password: admin123

*Note: Please change these credentials in production!*

## Security Note

For production deployment:
1. Change the SECRET_KEY in app.py
2. Change the admin password
3. Use environment variables for sensitive data
4. Enable HTTPS
