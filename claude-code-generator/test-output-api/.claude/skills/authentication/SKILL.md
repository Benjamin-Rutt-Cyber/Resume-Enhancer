---
name: authentication
description: Expert knowledge in authentication and authorization including JWT tokens, OAuth2, password hashing, session management, and multi-factor authentication.
allowed-tools: [Read, Write, Edit, Bash]
---

# Authentication Skill

Comprehensive knowledge for implementing secure authentication and authorization.

## Quick Start

### JWT Authentication (Node.js)

```bash
# Install dependencies
npm install jsonwebtoken bcryptjs
npm install @types/jsonwebtoken @types/bcryptjs --save-dev
```

```typescript
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';

const SECRET_KEY = process.env.JWT_SECRET || 'your-secret-key';

// Hash password
async function hashPassword(password: string): Promise<string> {
    const salt = await bcrypt.genSalt(10);
    return bcrypt.hash(password, salt);
}

// Verify password
async function verifyPassword(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
}

// Generate JWT token
function generateToken(userId: number): string {
    return jwt.sign(
        { userId, type: 'access' },
        SECRET_KEY,
        { expiresIn: '15m' }
    );
}

// Verify JWT token
function verifyToken(token: string): { userId: number } {
    return jwt.verify(token, SECRET_KEY) as { userId: number };
}

// Login endpoint example
app.post('/login', async (req, res) => {
    const { email, password } = req.body;

    const user = await db.getUserByEmail(email);
    if (!user) {
        return res.status(401).json({ error: 'Invalid credentials' });
    }

    const isValid = await verifyPassword(password, user.passwordHash);
    if (!isValid) {
        return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = generateToken(user.id);
    res.json({ token, user: { id: user.id, email: user.email } });
});
```

### JWT Authentication (Python/FastAPI)

```bash
# Install dependencies
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Create access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verify token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

---

## Core Concepts

### 1. Password Hashing

```python
# Python with bcrypt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password (automatic salt generation)
hashed = pwd_context.hash("mypassword")

# Verify password
is_valid = pwd_context.verify("mypassword", hashed)

# Argon2 (more secure, recommended for new apps)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
hashed = pwd_context.hash("mypassword")
```

```javascript
// Node.js with bcrypt
const bcrypt = require('bcryptjs');

// Hash password
const salt = await bcrypt.genSalt(10);  // Cost factor 10
const hashed = await bcrypt.hash('mypassword', salt);

// Verify password
const isValid = await bcrypt.compare('mypassword', hashed);

// Argon2 (more secure)
const argon2 = require('argon2');

const hashed = await argon2.hash('mypassword');
const isValid = await argon2.verify(hashed, 'mypassword');
```

**Best Practices:**
- Use bcrypt with cost factor 10-12 (10 is default)
- Use argon2 for new applications (more secure)
- Never store plain-text passwords
- Use salt (bcrypt/argon2 handle this automatically)
- Rehash on login if algorithm needs updating

### 2. JWT Tokens

**Structure:** `header.payload.signature`

```javascript
// JWT Header
{
  "alg": "HS256",
  "typ": "JWT"
}

// JWT Payload (claims)
{
  "sub": "user123",      // Subject (user ID)
  "email": "user@example.com",
  "iat": 1234567890,     // Issued at
  "exp": 1234571490,     // Expiration
  "type": "access"       // Custom claim
}

// Generate token
const jwt = require('jsonwebtoken');

const payload = {
    userId: user.id,
    email: user.email,
    role: user.role
};

const accessToken = jwt.sign(
    payload,
    process.env.JWT_SECRET,
    { expiresIn: '15m' }
);

const refreshToken = jwt.sign(
    { userId: user.id, type: 'refresh' },
    process.env.JWT_REFRESH_SECRET,
    { expiresIn: '7d' }
);

// Verify token
try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    console.log('User ID:', decoded.userId);
} catch (error) {
    if (error.name === 'TokenExpiredError') {
        // Token expired, need refresh
    } else if (error.name === 'JsonWebTokenError') {
        // Invalid token
    }
}
```

### 3. Refresh Tokens

```typescript
interface TokenPair {
    accessToken: string;
    refreshToken: string;
}

function generateTokenPair(userId: number): TokenPair {
    const accessToken = jwt.sign(
        { userId, type: 'access' },
        ACCESS_SECRET,
        { expiresIn: '15m' }
    );

    const refreshToken = jwt.sign(
        { userId, type: 'refresh' },
        REFRESH_SECRET,
        { expiresIn: '7d' }
    );

    return { accessToken, refreshToken };
}

// Refresh endpoint
app.post('/refresh', async (req, res) => {
    const { refreshToken } = req.body;

    try {
        const payload = jwt.verify(refreshToken, REFRESH_SECRET);

        // Check if refresh token is blacklisted
        const isBlacklisted = await db.isTokenBlacklisted(refreshToken);
        if (isBlacklisted) {
            return res.status(401).json({ error: 'Token revoked' });
        }

        // Generate new token pair
        const tokens = generateTokenPair(payload.userId);

        // Optionally blacklist old refresh token
        await db.blacklistToken(refreshToken);

        res.json(tokens);
    } catch (error) {
        res.status(401).json({ error: 'Invalid refresh token' });
    }
});
```

### 4. OAuth2 Authorization Code Flow

```typescript
// Step 1: Redirect to OAuth provider
app.get('/auth/google', (req, res) => {
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
        `client_id=${CLIENT_ID}` +
        `&redirect_uri=${REDIRECT_URI}` +
        `&response_type=code` +
        `&scope=openid email profile`;

    res.redirect(authUrl);
});

// Step 2: Handle callback
app.get('/auth/google/callback', async (req, res) => {
    const { code } = req.query;

    // Exchange code for tokens
    const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            code,
            client_id: CLIENT_ID,
            client_secret: CLIENT_SECRET,
            redirect_uri: REDIRECT_URI,
            grant_type: 'authorization_code'
        })
    });

    const { access_token, id_token } = await tokenResponse.json();

    // Get user info
    const userResponse = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
        headers: { Authorization: `Bearer ${access_token}` }
    });

    const googleUser = await userResponse.json();

    // Create or update user in database
    let user = await db.getUserByEmail(googleUser.email);
    if (!user) {
        user = await db.createUser({
            email: googleUser.email,
            name: googleUser.name,
            googleId: googleUser.id
        });
    }

    // Generate your own JWT
    const token = generateToken(user.id);

    res.json({ token, user });
});
```

### 5. Multi-Factor Authentication (TOTP)

```typescript
import speakeasy from 'speakeasy';
import QRCode from 'qrcode';

// Generate secret for user
app.post('/mfa/setup', async (req, res) => {
    const user = await getCurrentUser(req);

    const secret = speakeasy.generateSecret({
        name: `MyApp (${user.email})`
    });

    // Save secret to user
    await db.updateUser(user.id, { mfaSecret: secret.base32 });

    // Generate QR code
    const qrCodeUrl = await QRCode.toDataURL(secret.otpauth_url);

    res.json({
        secret: secret.base32,
        qrCode: qrCodeUrl
    });
});

// Verify TOTP code
app.post('/mfa/verify', async (req, res) => {
    const user = await getCurrentUser(req);
    const { token } = req.body;

    const verified = speakeasy.totp.verify({
        secret: user.mfaSecret,
        encoding: 'base32',
        token,
        window: 2  // Allow 2 time steps before/after
    });

    if (verified) {
        await db.updateUser(user.id, { mfaEnabled: true });
        res.json({ success: true });
    } else {
        res.status(401).json({ error: 'Invalid code' });
    }
});

// Login with MFA
app.post('/login', async (req, res) => {
    const { email, password, mfaToken } = req.body;

    const user = await db.getUserByEmail(email);
    if (!user || !await verifyPassword(password, user.passwordHash)) {
        return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Check if MFA is enabled
    if (user.mfaEnabled) {
        if (!mfaToken) {
            return res.status(200).json({ mfaRequired: true });
        }

        const verified = speakeasy.totp.verify({
            secret: user.mfaSecret,
            encoding: 'base32',
            token: mfaToken,
            window: 2
        });

        if (!verified) {
            return res.status(401).json({ error: 'Invalid MFA code' });
        }
    }

    const token = generateToken(user.id);
    res.json({ token, user });
});
```

---

## Session Management

### Cookie-based Sessions

```typescript
import session from 'express-session';
import RedisStore from 'connect-redis';
import { createClient } from 'redis';

// Redis client
const redisClient = createClient({ url: 'redis://localhost:6379' });
await redisClient.connect();

// Session middleware
app.use(session({
    store: new RedisStore({ client: redisClient }),
    secret: process.env.SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: process.env.NODE_ENV === 'production',  // HTTPS only
        httpOnly: true,                                  // No client JS access
        maxAge: 1000 * 60 * 60 * 24,                    // 24 hours
        sameSite: 'lax'                                  // CSRF protection
    }
}));

// Login
app.post('/login', async (req, res) => {
    const { email, password } = req.body;
    const user = await authenticateUser(email, password);

    if (user) {
        req.session.userId = user.id;
        req.session.role = user.role;
        res.json({ success: true });
    } else {
        res.status(401).json({ error: 'Invalid credentials' });
    }
});

// Logout
app.post('/logout', (req, res) => {
    req.session.destroy((err) => {
        if (err) {
            return res.status(500).json({ error: 'Logout failed' });
        }
        res.clearCookie('connect.sid');
        res.json({ success: true });
    });
});

// Protected route
app.get('/profile', requireAuth, async (req, res) => {
    const user = await db.getUser(req.session.userId);
    res.json({ user });
});

// Auth middleware
function requireAuth(req, res, next) {
    if (!req.session.userId) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    next();
}
```

---

## Authorization (RBAC)

```typescript
// Define roles and permissions
const ROLES = {
    ADMIN: 'admin',
    USER: 'user',
    MODERATOR: 'moderator'
};

const PERMISSIONS = {
    'admin': ['read', 'write', 'delete', 'manage_users'],
    'moderator': ['read', 'write', 'delete'],
    'user': ['read', 'write']
};

// Middleware to check permissions
function requirePermission(permission: string) {
    return (req, res, next) => {
        const user = req.user;  // From auth middleware

        const userPermissions = PERMISSIONS[user.role] || [];
        if (userPermissions.includes(permission)) {
            next();
        } else {
            res.status(403).json({ error: 'Forbidden' });
        }
    };
}

// Usage
app.delete('/posts/:id', requireAuth, requirePermission('delete'), async (req, res) => {
    // Delete post
});

// Alternative: Check role directly
function requireRole(...roles: string[]) {
    return (req, res, next) => {
        if (roles.includes(req.user.role)) {
            next();
        } else {
            res.status(403).json({ error: 'Forbidden' });
        }
    };
}

app.get('/admin/users', requireAuth, requireRole('admin'), async (req, res) => {
    // Admin only
});
```

---

## Security Best Practices

### 1. Token Storage

```typescript
// ✅ GOOD: Store in httpOnly cookie
res.cookie('token', jwtToken, {
    httpOnly: true,      // Not accessible via JavaScript
    secure: true,        // HTTPS only
    sameSite: 'strict',  // CSRF protection
    maxAge: 900000       // 15 minutes
});

// ❌ BAD: Store in localStorage (vulnerable to XSS)
// localStorage.setItem('token', jwtToken);

// For mobile apps: Secure storage
// iOS: Keychain
// Android: Keystore
```

### 2. CSRF Protection

```typescript
import csrf from 'csurf';

// CSRF middleware
const csrfProtection = csrf({ cookie: true });

app.use(csrfProtection);

// Send CSRF token to client
app.get('/csrf-token', (req, res) => {
    res.json({ csrfToken: req.csrfToken() });
});

// Client must include CSRF token
// In form: <input type="hidden" name="_csrf" value="${csrfToken}">
// In AJAX: headers: { 'CSRF-Token': csrfToken }
```

### 3. Rate Limiting

```typescript
import rateLimit from 'express-rate-limit';

// Login rate limiter
const loginLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,  // 15 minutes
    max: 5,                      // 5 requests per window
    message: 'Too many login attempts, please try again later',
    standardHeaders: true,
    legacyHeaders: false,
});

app.post('/login', loginLimiter, async (req, res) => {
    // Login logic
});
```

### 4. Password Requirements

```typescript
function validatePassword(password: string): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (password.length < 8) {
        errors.push('Password must be at least 8 characters');
    }
    if (!/[A-Z]/.test(password)) {
        errors.push('Password must contain uppercase letter');
    }
    if (!/[a-z]/.test(password)) {
        errors.push('Password must contain lowercase letter');
    }
    if (!/[0-9]/.test(password)) {
        errors.push('Password must contain number');
    }
    if (!/[^A-Za-z0-9]/.test(password)) {
        errors.push('Password must contain special character');
    }

    return {
        valid: errors.length === 0,
        errors
    };
}
```

---

## Common Patterns

### Password Reset Flow

```typescript
import crypto from 'crypto';

// Request password reset
app.post('/forgot-password', async (req, res) => {
    const { email } = req.body;
    const user = await db.getUserByEmail(email);

    if (!user) {
        // Don't reveal if email exists
        return res.json({ message: 'If email exists, reset link sent' });
    }

    // Generate reset token
    const resetToken = crypto.randomBytes(32).toString('hex');
    const resetTokenHash = crypto
        .createHash('sha256')
        .update(resetToken)
        .digest('hex');

    // Save hashed token and expiry
    await db.updateUser(user.id, {
        resetToken: resetTokenHash,
        resetTokenExpiry: Date.now() + 3600000  // 1 hour
    });

    // Send email with reset link
    const resetUrl = `https://myapp.com/reset-password?token=${resetToken}`;
    await sendEmail(user.email, 'Password Reset', resetUrl);

    res.json({ message: 'If email exists, reset link sent' });
});

// Reset password
app.post('/reset-password', async (req, res) => {
    const { token, newPassword } = req.body;

    const resetTokenHash = crypto
        .createHash('sha256')
        .update(token)
        .digest('hex');

    const user = await db.getUserByResetToken(resetTokenHash);

    if (!user || user.resetTokenExpiry < Date.now()) {
        return res.status(400).json({ error: 'Invalid or expired token' });
    }

    // Update password
    const passwordHash = await hashPassword(newPassword);
    await db.updateUser(user.id, {
        passwordHash,
        resetToken: null,
        resetTokenExpiry: null
    });

    res.json({ message: 'Password reset successful' });
});
```

### Email Verification

```typescript
// After registration
app.post('/register', async (req, res) => {
    const { email, password } = req.body;

    // Create user
    const user = await db.createUser({
        email,
        passwordHash: await hashPassword(password),
        emailVerified: false
    });

    // Generate verification token
    const verificationToken = crypto.randomBytes(32).toString('hex');
    await db.saveVerificationToken(user.id, verificationToken);

    // Send verification email
    const verifyUrl = `https://myapp.com/verify-email?token=${verificationToken}`;
    await sendEmail(email, 'Verify Email', verifyUrl);

    res.json({ message: 'Please check your email to verify account' });
});

// Verify email
app.get('/verify-email', async (req, res) => {
    const { token } = req.query;

    const userId = await db.getUserIdByVerificationToken(token);
    if (!userId) {
        return res.status(400).json({ error: 'Invalid token' });
    }

    await db.updateUser(userId, { emailVerified: true });
    await db.deleteVerificationToken(token);

    res.json({ message: 'Email verified successfully' });
});
```

---

## Troubleshooting

**JWT token not being sent:**
- Check CORS settings (credentials: 'include')
- Ensure cookie settings (httpOnly, secure, sameSite)
- Verify domain matches

**bcrypt hash compare always fails:**
- Check password encoding
- Verify hash is stored correctly
- Ensure same bcrypt version

**OAuth redirect issues:**
- Verify redirect URI matches exactly
- Check OAuth app settings in provider console
- Ensure HTTPS in production

---

## Resources

- JWT.io: https://jwt.io/
- OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- OAuth 2.0: https://oauth.net/2/
- Passport.js (Node.js): http://www.passportjs.org/
- Auth0 Docs: https://auth0.com/docs
