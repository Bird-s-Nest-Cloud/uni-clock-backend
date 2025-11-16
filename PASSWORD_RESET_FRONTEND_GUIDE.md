# Password Reset API - Frontend Integration Guide

## API Base URL
```
http://localhost:8000/api
```

---

## 1. Forgot Password API

### Endpoint
```
POST /api/auth/forgot-password/
```

### Request Headers
```
Content-Type: application/json
```

### Request Body
```json
{
  "email": "user@example.com"
}
```

### Success Response (200 OK)
```json
{
  "status": true,
  "status_code": 200,
  "message": "You will receive a password reset link shortly.",
  "data": {}
}
```

### Error Response - Invalid Email (400 Bad Request)
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


---

## 2. Verify Reset Token API

### Endpoint
```
POST /api/auth/verify-reset-token/
```

### Request Headers
```
Content-Type: application/json
```

### Request Body
```json
{
  "token": "KZJxvZ8h9QzE9RqN0LHm8FYwGN-7Tqk9xN8yLQp-F3M"
}
```

### Success Response (200 OK)
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

### Error Response - Invalid Token (400 Bad Request)
```json
{
  "status": false,
  "status_code": 400,
  "message": "Invalid or expired token",
  "data": {
    "errors": {
      "token": ["Invalid token"]
    }
  }
}
```

### Error Response - Expired Token (400 Bad Request)
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

```javascript
const verifyToken = async (token) => {
  try {
    const response = await fetch('http://localhost:8000/api/auth/verify-reset-token/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token })
    });
    
    const data = await response.json();
    
    if (data.status) {
      // Token is valid
      return {
        valid: true,
        email: data.data.email
      };
    } else {
      // Token is invalid or expired
      return {
        valid: false,
        error: data.data.errors.token?.[0] || 'Invalid token'
      };
    }
  } catch (error) {
    console.error('Error:', error);
    return {
      valid: false,
      error: 'Failed to verify token'
    };
  }
};
```

---

## 3. Reset Password API

### Endpoint
```
POST /api/auth/reset-password/
```

### Request Headers
```
Content-Type: application/json
```

### Request Body
```json
{
  "token": "KZJxvZ8h9QzE9RqN0LHm8FYwGN-7Tqk9xN8yLQp-F3M",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

### Success Response (200 OK)
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

### Error Response - Passwords Don't Match (400 Bad Request)
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

### Error Response - Invalid Token (400 Bad Request)
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

### Error Response - Weak Password (400 Bad Request)
```json
{
  "status": false,
  "status_code": 400,
  "message": "Password reset failed",
  "data": {
    "errors": {
      "new_password": [
        "This password is too short. It must contain at least 8 characters."
      ]
    }
  }
}
```

```javascript
const resetPassword = async (token, newPassword, confirmPassword) => {
  try {
    const response = await fetch('http://localhost:8000/api/auth/reset-password/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token,
        new_password: newPassword,
        confirm_password: confirmPassword
      })
    });
    
    const data = await response.json();
    
    if (data.status) {
      // Password reset successful
      alert(data.message);
      // Redirect to login
      window.location.href = '/login';
    } else {
      // Show errors
      const errors = data.data.errors;
      if (errors.token) {
        alert(errors.token[0]);
      } else if (errors.new_password) {
        alert(errors.new_password[0]);
      } else if (errors.confirm_password) {
        alert(errors.confirm_password[0]);
      } else {
        alert(data.message);
      }
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to reset password');
  }
};
```

---

## Complete React Example

```javascript
// src/pages/ForgotPassword.jsx
import { useState } from 'react';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/forgot-password/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      const data = await response.json();
      setMessage(data.message);
      if (data.status) setEmail('');
    } catch (error) {
      setMessage('Failed to send reset email. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h2>Forgot Password</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
          required
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Send Reset Link'}
        </button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}
```

```javascript
// src/pages/ResetPassword.jsx
import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [tokenValid, setTokenValid] = useState(false);
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState({});

  // Verify token on mount
  useEffect(() => {
    const verifyToken = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/auth/verify-reset-token/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token })
        });

        const data = await response.json();
        
        if (data.status) {
          setTokenValid(true);
          setEmail(data.data.email);
        } else {
          setMessage(data.data.errors.token?.[0] || 'Invalid reset link');
        }
      } catch (error) {
        setMessage('Invalid reset link');
      }
    };

    if (token) verifyToken();
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setErrors({});

    try {
      const response = await fetch('http://localhost:8000/api/auth/reset-password/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token,
          new_password: password,
          confirm_password: confirmPassword
        })
      });

      const data = await response.json();

      if (data.status) {
        setMessage(data.message);
        setTimeout(() => navigate('/login'), 3000);
      } else {
        setErrors(data.data.errors);
        setMessage(data.message);
      }
    } catch (error) {
      setMessage('Password reset failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!tokenValid && !message) {
    return <div>Verifying reset link...</div>;
  }

  if (!tokenValid) {
    return (
      <div className="alert alert-error">
        <h3>Invalid Reset Link</h3>
        <p>{message}</p>
      </div>
    );
  }

  return (
    <div className="container">
      <h2>Reset Password</h2>
      <p>Resetting password for: <strong>{email}</strong></p>

      <form onSubmit={handleSubmit}>
        <div>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="New Password"
            minLength={8}
            required
            disabled={loading}
          />
          {errors.new_password && <span className="error">{errors.new_password[0]}</span>}
        </div>

        <div>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm Password"
            minLength={8}
            required
            disabled={loading}
          />
          {errors.confirm_password && <span className="error">{errors.confirm_password[0]}</span>}
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Resetting...' : 'Reset Password'}
        </button>
      </form>

      {message && <p className={errors.token ? 'error' : 'success'}>{message}</p>}
    </div>
  );
}
```

---

## Error Handling Reference

### All Possible Errors

| Field | Error Message | Meaning |
|-------|--------------|---------|
| `email` | "Enter a valid email address." | Invalid email format |
| `token` | "Invalid token" | Token doesn't exist in database |
| `token` | "Token has expired or already been used" | Token is expired or was already used |
| `new_password` | "This password is too short. It must contain at least 8 characters." | Password < 8 chars |
| `new_password` | "This password is too common." | Password in common password list |
| `new_password` | "This password is entirely numeric." | Password only contains numbers |
| `confirm_password` | "Passwords do not match" | new_password ≠ confirm_password |

---

## Response Structure (Always)

Every response follows this structure:

```json
{
  "status": true,              // boolean: true = success, false = error
  "status_code": 200,           // number: HTTP status code
  "message": "...",             // string: Human-readable message
  "data": {}                    // object: Response data or errors
}
```

For errors, `data` contains:
```json
{
  "data": {
    "errors": {
      "field_name": ["Error message"]
    }
  }
}
```

---

## Email Template

When user requests password reset, they receive an HTML email with:

- **Subject**: "Password Reset Request - BikeShop"
- **Content**: 
  - Greeting with user's name
  - Reset link button (clickable)
  - Plain text link (for copy/paste)
  - Expiry warning (1 hour)
  - Security notice
  - BikeShop branding

**Reset Link Format**:
```
http://localhost:3000/reset-password?token=KZJxvZ8h9QzE9RqN0LHm8FYwGN-7Tqk9xN8yLQp-F3M
```

---

## Testing Commands

```bash
# 1. Request password reset
curl -X POST http://localhost:8000/api/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# 2. Verify token
curl -X POST http://localhost:8000/api/auth/verify-reset-token/ \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_TOKEN"}'

# 3. Reset password
curl -X POST http://localhost:8000/api/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_TOKEN", "new_password": "newpass123", "confirm_password": "newpass123"}'
```

---

## Next Steps for Frontend

1. ✅ Create `/forgot-password` route
2. ✅ Create `/reset-password` route  
3. ✅ Implement form validation
4. ✅ Handle all error states
5. ✅ Add loading states
6. ✅ Test with console email backend first
7. ✅ Test with real email in staging

---

**Backend Status**: ✅ Complete and Ready
**API Documentation**: ✅ Complete
**Frontend Examples**: ✅ Provided
