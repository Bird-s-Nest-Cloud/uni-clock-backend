# Password Reset API Documentation

Complete documentation for the password reset functionality in BikeShop API.

---

## Table of Contents
1. [Setup Instructions](#setup-instructions)
2. [API Endpoints](#api-endpoints)
3. [Frontend Integration Examples](#frontend-integration-examples)
4. [Testing Guide](#testing-guide)

---

## Setup Instructions

### 1. Run Migrations

```bash
python manage.py makemigrations accounts
python manage.py migrate accounts
```

### 2. Configure Environment Variables

Create a `.env` file in the project root (or update existing one):

```env
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=BikeShop <noreply@bikeshop.com>

# Frontend URL (for password reset links)
FRONTEND_URL=http://localhost:3000

# Password Reset Token Expiry (in seconds)
PASSWORD_RESET_TIMEOUT=3600
```

### 3. Gmail Setup (if using Gmail)

1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Generate an "App Password" for Django
4. Use that app password in `EMAIL_HOST_PASSWORD`

### 4. Development Setup (Console Email)

For development/testing without sending real emails, use:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Emails will be printed to the console instead of being sent.

---

## API Endpoints

### 1. Forgot Password

**POST** `/api/auth/forgot-password/`

Request a password reset email.

#### Headers
```
Content-Type: application/json
```

#### Request Body
```json
{
  "email": "user@example.com"
}
```

#### Success Response (200 OK)
```json
{
  "status": true,
  "status_code": 200,
  "message": "If an account exists with this email, you will receive a password reset link shortly.",
  "data": {}
}
```

#### Error Response (400 Bad Request)
```json
{
  "status": false,
  "status_code": 400,
  "message": "Invalid email address",
  "data": {
    "errors": {
      "email": ["Enter a valid email address."]
    }
  }
}
```

#### Notes
- **Security Feature**: The API always returns success even if the email doesn't exist to prevent email enumeration attacks.
- The user will receive an email if their account exists.
- Email contains a secure token that expires in 1 hour.

---

### 2. Verify Reset Token

**POST** `/api/auth/verify-reset-token/`

Verify if a password reset token is valid before showing the reset password form.

#### Headers
```
Content-Type: application/json
```

#### Request Body
```json
{
  "token": "abc123xyz..."
}
```

#### Success Response (200 OK)
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

#### Error Response (400 Bad Request)
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

#### Use Cases
- Verify token when user lands on reset password page
- Show user's email for confirmation
- Display appropriate error if token is invalid/expired

---

### 3. Reset Password

**POST** `/api/auth/reset-password/`

Reset user's password using a valid token.

#### Headers
```
Content-Type: application/json
```

#### Request Body
```json
{
  "token": "abc123xyz...",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

#### Success Response (200 OK)
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

#### Error Responses

**Passwords Don't Match (400)**
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

**Invalid Token (400)**
```json
{
  "status": false,
  "status_code": 400,
  "message": "Password reset failed",
  "data": {
    "errors": {
      "token": ["Invalid token"]
    }
  }
}
```

**Expired Token (400)**
```json
{
  "status": false,
  "status_code": 400,
  "message": "Password reset failed",
  "data": {
    "errors": {
      "token": ["Token has expired or already been used"]
    }
  }
}
```

**Weak Password (400)**
```json
{
  "status": false,
  "status_code": 400,
  "message": "Password reset failed",
  "data": {
    "errors": {
      "new_password": [
        "This password is too short. It must contain at least 8 characters.",
        "This password is too common."
      ]
    }
  }
}
```

#### Password Requirements
- Minimum 8 characters
- Cannot be too common
- Cannot be entirely numeric
- Cannot be too similar to user information
- Must match confirmation password

---

## Frontend Integration Examples

### 1. Forgot Password Page

```javascript
// ForgotPassword.jsx
import { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/forgot-password/`, {
        email: email
      });
      
      setMessage(response.data.message);
      setEmail(''); // Clear the form
    } catch (err) {
      if (err.response?.data?.data?.errors) {
        setError(err.response.data.data.errors.email?.[0] || 'Invalid email address');
      } else {
        setError('Failed to send reset email. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forgot-password-container">
      <h2>Forgot Password</h2>
      <p>Enter your email address and we'll send you a link to reset your password.</p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email Address</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            required
            disabled={loading}
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Send Reset Link'}
        </button>
      </form>
      
      {message && (
        <div className="alert alert-success">
          {message}
        </div>
      )}
      
      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}
    </div>
  );
}

export default ForgotPassword;
```

---

### 2. Reset Password Page

```javascript
// ResetPassword.jsx
import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');
  
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState({});

  // Verify token on component mount
  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setMessage('Invalid reset link');
        setVerifying(false);
        return;
      }

      try {
        const response = await axios.post(`${API_BASE_URL}/auth/verify-reset-token/`, {
          token: token
        });
        
        setTokenValid(true);
        setEmail(response.data.data.email);
      } catch (error) {
        setTokenValid(false);
        if (error.response?.data?.data?.errors) {
          setMessage(error.response.data.data.errors.token?.[0] || 'Invalid or expired reset link');
        } else {
          setMessage('Invalid or expired reset link');
        }
      } finally {
        setVerifying(false);
      }
    };

    verifyToken();
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setErrors({});
    
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/reset-password/`, {
        token: token,
        new_password: password,
        confirm_password: confirmPassword
      });
      
      setMessage(response.data.message);
      
      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login');
      }, 3000);
      
    } catch (error) {
      if (error.response?.data?.data?.errors) {
        setErrors(error.response.data.data.errors);
        setMessage(error.response.data.message);
      } else {
        setMessage('Password reset failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Loading state
  if (verifying) {
    return (
      <div className="reset-password-container">
        <div className="loading">Verifying reset link...</div>
      </div>
    );
  }

  // Invalid token state
  if (!tokenValid) {
    return (
      <div className="reset-password-container">
        <div className="alert alert-error">
          <h3>Invalid Reset Link</h3>
          <p>{message}</p>
          <button onClick={() => navigate('/forgot-password')}>
            Request New Reset Link
          </button>
        </div>
      </div>
    );
  }

  // Success state (after password reset)
  if (message && !errors.token && !errors.new_password && !errors.confirm_password) {
    return (
      <div className="reset-password-container">
        <div className="alert alert-success">
          <h3>✓ Password Reset Successful</h3>
          <p>{message}</p>
          <p>Redirecting to login page...</p>
        </div>
      </div>
    );
  }

  // Reset password form
  return (
    <div className="reset-password-container">
      <h2>Reset Password</h2>
      <p>Resetting password for: <strong>{email}</strong></p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="password">New Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter new password"
            minLength={8}
            required
            disabled={loading}
          />
          {errors.new_password && (
            <span className="error-text">{errors.new_password[0]}</span>
          )}
        </div>
        
        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm new password"
            minLength={8}
            required
            disabled={loading}
          />
          {errors.confirm_password && (
            <span className="error-text">{errors.confirm_password[0]}</span>
          )}
        </div>
        
        <div className="password-requirements">
          <p>Password must:</p>
          <ul>
            <li>Be at least 8 characters long</li>
            <li>Not be too common</li>
            <li>Not be entirely numeric</li>
          </ul>
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Resetting...' : 'Reset Password'}
        </button>
      </form>
      
      {message && errors.token && (
        <div className="alert alert-error">
          {message}
        </div>
      )}
    </div>
  );
}

export default ResetPassword;
```

---

### 3. API Service Helper

```javascript
// services/authService.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const authService = {
  // Request password reset
  forgotPassword: async (email) => {
    const response = await axios.post(`${API_BASE_URL}/auth/forgot-password/`, {
      email
    });
    return response.data;
  },

  // Verify reset token
  verifyResetToken: async (token) => {
    const response = await axios.post(`${API_BASE_URL}/auth/verify-reset-token/`, {
      token
    });
    return response.data;
  },

  // Reset password
  resetPassword: async (token, newPassword, confirmPassword) => {
    const response = await axios.post(`${API_BASE_URL}/auth/reset-password/`, {
      token,
      new_password: newPassword,
      confirm_password: confirmPassword
    });
    return response.data;
  }
};
```

---

## Testing Guide

### 1. Test Forgot Password (Console Backend)

```bash
# Make sure EMAIL_BACKEND is set to console in .env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Start Django server
python manage.py runserver

# In another terminal, test the API
curl -X POST http://localhost:8000/api/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# Check the Django console/terminal for the email output with the reset link
```

### 2. Test Token Verification

```bash
# Copy the token from the email in console
# Replace YOUR_TOKEN_HERE with actual token

curl -X POST http://localhost:8000/api/auth/verify-reset-token/ \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_TOKEN_HERE"}'
```

### 3. Test Password Reset

```bash
# Use the token from the email

curl -X POST http://localhost:8000/api/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN_HERE",
    "new_password": "newpassword123",
    "confirm_password": "newpassword123"
  }'
```

### 4. Test with Real Email (Gmail)

Update your `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=BikeShop <noreply@bikeshop.com>
```

Then test the forgot password API - you should receive a real email!

---

## Security Features

✅ **Token Expiry** - Tokens expire after 1 hour (configurable)
✅ **One-time Use** - Tokens can only be used once
✅ **Token Invalidation** - All previous tokens invalidated when new one generated
✅ **Email Enumeration Protection** - Same response whether email exists or not
✅ **Secure Token Generation** - Uses `secrets.token_urlsafe()` for cryptographic security
✅ **Password Validation** - Django's built-in password validators
✅ **HTTPS Ready** - Works securely over HTTPS in production

---

## Common Issues & Solutions

### Issue: Email not sending
**Solution**: 
- Check EMAIL_BACKEND is correct
- Verify Gmail app password is correct
- Check internet connection
- Look for errors in Django console

### Issue: Token expired error
**Solution**: 
- Token expires in 1 hour by default
- Request a new password reset link
- Increase PASSWORD_RESET_TIMEOUT in .env if needed

### Issue: CORS error in frontend
**Solution**: 
- Ensure CORS is configured in Django settings
- Frontend URL must match FRONTEND_URL in .env
- Check browser console for exact error

---

## Email Template Preview

The password reset email includes:
- Professional HTML template with styling
- Clear call-to-action button
- Plain text fallback
- Expiry warning
- Security notice
- BikeShop branding

---

## Production Checklist

- [ ] Use real SMTP server (not console backend)
- [ ] Set up proper email credentials
- [ ] Use HTTPS for frontend URL
- [ ] Set SESSION_COOKIE_SECURE = True
- [ ] Set CSRF_COOKIE_SECURE = True
- [ ] Configure proper CORS origins
- [ ] Set appropriate token expiry time
- [ ] Add rate limiting to prevent abuse
- [ ] Set up email delivery monitoring
- [ ] Test email delivery thoroughly
- [ ] Add logging for failed email attempts
- [ ] Set DEBUG = False

---

## API Quick Reference

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/api/auth/forgot-password/` | POST | No | Request password reset |
| `/api/auth/verify-reset-token/` | POST | No | Verify token validity |
| `/api/auth/reset-password/` | POST | No | Reset password with token |

---

**Created**: November 1, 2025
**Version**: 1.0.0
**Status**: ✅ Production Ready
