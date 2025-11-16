# Password Reset Implementation - Quick Start Guide

## ✅ Implementation Complete!

All password reset functionality has been implemented. Here's what to do next:

---

## Step 1: Run Migrations

```bash
python manage.py makemigrations accounts
python manage.py migrate
```

---

## Step 2: Configure Email (Choose One)

### Option A: Development (Console - No Real Emails)
Your `.env` file (already set as default):
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
FRONTEND_URL=http://localhost:3000
```

Emails will print in the Django console/terminal.

### Option B: Production (Gmail)
Update your `.env` file:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=BikeShop <noreply@bikeshop.com>
FRONTEND_URL=http://localhost:3000
```

---

## Step 3: API Endpoints Ready to Use

### 1️⃣ Forgot Password
**POST** `http://localhost:8000/api/auth/forgot-password/`

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "status": true,
  "status_code": 200,
  "message": "If an account exists with this email, you will receive a password reset link shortly.",
  "data": {}
}
```

---

### 2️⃣ Verify Reset Token
**POST** `http://localhost:8000/api/auth/verify-reset-token/`

**Request:**
```json
{
  "token": "abc123xyz..."
}
```

**Response (Success):**
```json
{
  "status": true,
  "status_code": 200,
  "message": "Token is valid",
  "data": {
    "valid": true,
    "email": "user@example.com"
  }
}
```

**Response (Error):**
```json
{
  "status": false,
  "status_code": 400,
  "message": "Invalid or expired token",
  "data": {
    "errors": {
      "token": ["Token has expired or already been used"]
    }
  }
}
```

---

### 3️⃣ Reset Password
**POST** `http://localhost:8000/api/auth/reset-password/`

**Request:**
```json
{
  "token": "abc123xyz...",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

**Response (Success):**
```json
{
  "status": true,
  "status_code": 200,
  "message": "Password reset successfully. You can now login with your new password.",
  "data": {
    "email": "user@example.com"
  }
}
```

**Response (Passwords Don't Match):**
```json
{
  "status": false,
  "status_code": 400,
  "message": "Password reset failed",
  "data": {
    "errors": {
      "confirm_password": ["Passwords do not match"]
    }
  }
}
```

---

## Frontend Integration Flow

### 1. Forgot Password Page (`/forgot-password`)
```javascript
// User enters email
const response = await axios.post('http://localhost:8000/api/auth/forgot-password/', {
  email: userEmail
});

// Always shows success (security feature)
// User receives email if account exists
```

### 2. Email Sent
User receives beautifully formatted email with:
- Reset link: `http://localhost:3000/reset-password?token=abc123xyz...`
- Expires in 1 hour
- One-time use only

### 3. Reset Password Page (`/reset-password?token=...`)
```javascript
// Step 1: Verify token when page loads
const verifyResponse = await axios.post('http://localhost:8000/api/auth/verify-reset-token/', {
  token: tokenFromURL
});

// Show form if valid, show error if invalid/expired

// Step 2: User submits new password
const resetResponse = await axios.post('http://localhost:8000/api/auth/reset-password/', {
  token: tokenFromURL,
  new_password: password,
  confirm_password: confirmPassword
});

// Redirect to login on success
```

---

## Testing Right Now

### Test 1: Request Password Reset
```bash
curl -X POST http://localhost:8000/api/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com"}'
```

### Test 2: Check Console
Look at your Django console - you'll see the email with the reset token!

### Test 3: Copy Token and Verify
```bash
curl -X POST http://localhost:8000/api/auth/verify-reset-token/ \
  -H "Content-Type: application/json" \
  -d '{"token": "PASTE_TOKEN_HERE"}'
```

### Test 4: Reset Password
```bash
curl -X POST http://localhost:8000/api/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "PASTE_TOKEN_HERE",
    "new_password": "newpass123",
    "confirm_password": "newpass123"
  }'
```

---

## Files Created/Modified

✅ `.env.example` - Email configuration template
✅ `apps/accounts/models.py` - Added PasswordResetToken model
✅ `apps/api/serializers/auth.py` - Added 3 new serializers
✅ `apps/api/views/auth.py` - Added 3 new views
✅ `apps/api/urls.py` - Added 3 new routes
✅ `bike_shop/settings.py` - Added email configuration
✅ `PASSWORD_RESET_API_DOCUMENTATION.md` - Complete documentation with frontend examples

---

## What Your Frontend Needs

### Route 1: Forgot Password
- **URL**: `/forgot-password`
- **Shows**: Email input form
- **API Call**: POST `/api/auth/forgot-password/`
- **Success**: Show confirmation message

### Route 2: Reset Password  
- **URL**: `/reset-password?token=...`
- **On Load**: Verify token with API
- **Shows**: New password form (if valid) or error (if invalid)
- **API Calls**: 
  1. POST `/api/auth/verify-reset-token/` (on page load)
  2. POST `/api/auth/reset-password/` (on form submit)
- **Success**: Redirect to login

---

## Password Requirements

Your frontend should show these rules:
- ✅ Minimum 8 characters
- ✅ Cannot be too common
- ✅ Cannot be entirely numeric
- ✅ Must match confirmation

The Django backend validates all these automatically!

---

## Security Features Included

✅ Tokens expire after 1 hour
✅ One-time use tokens
✅ Email enumeration protection
✅ Secure token generation
✅ Password strength validation
✅ All old tokens invalidated on new request

---

## Need Help?

Check `PASSWORD_RESET_API_DOCUMENTATION.md` for:
- Complete API documentation
- Full React component examples
- Error handling patterns
- Production deployment checklist
- Troubleshooting guide

---

**Status**: ✅ Ready to use!
**Next Step**: Run migrations and start testing!
