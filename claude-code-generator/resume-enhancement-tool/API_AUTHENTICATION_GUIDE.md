# API Authentication Guide

## Quick Reference for Developers

### How to Call Protected API Endpoints

All API endpoints (except `/api/health` and `/api/auth/*`) now require authentication.

#### 1. **Obtain JWT Token**

**Register a new user:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

#### 2. **Use Token in API Requests**

**Include token in Authorization header:**
```bash
curl -X GET http://localhost:8000/api/resumes \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

#### 3. **Frontend Implementation**

**JavaScript/TypeScript Example:**
```typescript
// Store token after login
const loginResponse = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});

const { access_token } = await loginResponse.json();
localStorage.setItem('token', access_token);

// Use token in API calls
const token = localStorage.getItem('token');

const response = await fetch('/api/resumes', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

**React Hook Example:**
```typescript
import { useState, useEffect } from 'react';

function useAuth() {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('token')
  );

  const login = async (email: string, password: string) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();
    setToken(data.access_token);
    localStorage.setItem('token', data.access_token);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem('token');
  };

  const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`
      }
    });
  };

  return { token, login, logout, fetchWithAuth };
}
```

### Error Handling

#### 401 Unauthorized
Token is missing, invalid, or expired.

**Response:**
```json
{
  "detail": "Invalid authentication credentials"
}
```

**Action:** Redirect user to login page.

#### 403 Forbidden
User is authenticated but doesn't own the requested resource.

**Response:**
```json
{
  "detail": "Not authorized to access this resume"
}
```

**Action:** Show error message, prevent action.

### API Endpoints by Category

#### 🔓 Public Endpoints (No Auth Required)
```
POST   /api/auth/register     # Create account
POST   /api/auth/login        # Get token
GET    /api/health            # Health check
```

#### 🔒 Protected Endpoints (Auth Required)

**Resumes:**
```
POST   /api/resumes/upload                      # Upload resume
GET    /api/resumes                             # List user's resumes
GET    /api/resumes/{resume_id}                 # Get resume details
DELETE /api/resumes/{resume_id}                 # Delete resume
DELETE /api/resumes                             # Delete all user's resumes
PATCH  /api/resumes/{resume_id}/update-style    # Update style
POST   /api/resumes/{resume_id}/select-style    # Select writing style
```

**Jobs:**
```
POST   /api/jobs              # Create job description
GET    /api/jobs              # List user's jobs
GET    /api/jobs/{job_id}     # Get job details
```

**Enhancements:**
```
POST   /api/enhancements/tailor                           # Create tailoring
POST   /api/enhancements/revamp                           # Create revamp
GET    /api/enhancements                                  # List user's enhancements
GET    /api/enhancements/{enhancement_id}                 # Get enhancement
POST   /api/enhancements/{enhancement_id}/finalize        # Finalize (generate PDF)
GET    /api/enhancements/{enhancement_id}/download        # Download (PDF/MD)
GET    /api/enhancements/{enhancement_id}/download/docx   # Download DOCX
GET    /api/enhancements/{enhancement_id}/download/cover-letter  # Download cover letter
DELETE /api/enhancements/{enhancement_id}                 # Delete enhancement
DELETE /api/enhancements                                  # Delete all user's enhancements
```

**Analysis:**
```
GET    /api/enhancements/{enhancement_id}/analysis        # Get ATS analysis
GET    /api/enhancements/{enhancement_id}/achievements    # Get achievement suggestions
```

**Comparison:**
```
GET    /api/enhancements/{enhancement_id}/comparison      # Get before/after comparison
```

### Testing with cURL

**Upload Resume (Authenticated):**
```bash
TOKEN="your_token_here"

curl -X POST http://localhost:8000/api/resumes/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@resume.pdf"
```

**List Resumes (Authenticated):**
```bash
curl -X GET http://localhost:8000/api/resumes \
  -H "Authorization: Bearer $TOKEN"
```

**Create Job (Authenticated):**
```bash
curl -X POST http://localhost:8000/api/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Software Engineer",
    "company": "Tech Corp",
    "description_text": "We are seeking a talented senior software engineer..."
  }'
```

**Create Enhancement (Authenticated):**
```bash
curl -X POST http://localhost:8000/api/enhancements/tailor \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_id": "resume-uuid",
    "job_id": "job-uuid",
    "run_analysis": true
  }'
```

### Testing with Postman

1. **Setup Environment Variables:**
   - `base_url`: `http://localhost:8000`
   - `token`: (will be set after login)

2. **Login Request:**
   - Method: `POST`
   - URL: `{{base_url}}/api/auth/login`
   - Body (JSON):
     ```json
     {
       "email": "user@example.com",
       "password": "password"
     }
     ```
   - Tests (to save token):
     ```javascript
     pm.test("Status code is 200", function () {
         pm.response.to.have.status(200);
     });

     const jsonData = pm.response.json();
     pm.environment.set("token", jsonData.access_token);
     ```

3. **Authenticated Request:**
   - Method: `GET`
   - URL: `{{base_url}}/api/resumes`
   - Headers:
     ```
     Authorization: Bearer {{token}}
     ```

### Token Expiration

JWT tokens expire after **24 hours** (configurable in `backend/app/core/config.py`).

When a token expires:
1. API returns `401 Unauthorized`
2. Frontend should redirect to login
3. User must re-authenticate

**Future Enhancement:** Implement refresh tokens for seamless re-authentication.

### Security Best Practices

#### Frontend:
- ✅ Store token in `localStorage` or `sessionStorage`
- ✅ Clear token on logout
- ✅ Include token in all API requests
- ✅ Handle 401 errors by redirecting to login
- ✅ Don't store passwords
- ⚠️ Consider using `httpOnly` cookies for production (more secure)

#### Backend (Already Implemented):
- ✅ JWT tokens are signed with secret key
- ✅ Passwords are hashed with bcrypt
- ✅ All endpoints verify token
- ✅ User data is isolated by `user_id`
- ✅ Ownership checks on all resources

### Common Issues & Solutions

#### Issue: "Invalid authentication credentials"
**Cause:** Token is missing, expired, or invalid
**Solution:**
1. Check if token exists: `localStorage.getItem('token')`
2. Verify token format: `Bearer <token>`
3. Re-login if expired

#### Issue: "Not authorized to access this resource"
**Cause:** User doesn't own the resource
**Solution:**
1. Verify user is accessing their own data
2. Check if resource belongs to current user
3. Don't allow sharing resource IDs between users

#### Issue: CORS errors in frontend
**Cause:** CORS middleware not configured
**Solution:** Already configured in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend Update Checklist

To integrate authentication into your frontend:

- [ ] Add login page
- [ ] Add registration page
- [ ] Store JWT token after login
- [ ] Add `Authorization` header to all API calls
- [ ] Handle 401 errors (redirect to login)
- [ ] Handle 403 errors (show error message)
- [ ] Add logout functionality
- [ ] Clear token on logout
- [ ] Add protected route wrapper
- [ ] Show user email/name in header
- [ ] Add token expiration handling

### Example: Protected Route in React

```typescript
import { Navigate } from 'react-router-dom';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token');

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// Usage in App.tsx
<Routes>
  <Route path="/login" element={<LoginPage />} />
  <Route path="/register" element={<RegisterPage />} />
  <Route
    path="/dashboard"
    element={
      <ProtectedRoute>
        <Dashboard />
      </ProtectedRoute>
    }
  />
</Routes>
```

---

## Summary

All API endpoints are now protected with JWT authentication. To use them:

1. **Register** or **Login** to get a token
2. **Include token** in `Authorization: Bearer <token>` header
3. **Handle errors**: 401 = login again, 403 = unauthorized access
4. **Token expires** after 24 hours

For questions or issues, refer to the main authentication documentation or contact the backend team.
