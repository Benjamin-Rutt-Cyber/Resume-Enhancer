---
name: node-express
description: Expert knowledge in Node.js Express framework including middleware, routing, error handling, TypeScript integration, authentication, and production best practices.
allowed-tools: [Read, Write, Edit, Bash]
---

# Node.js Express Skill

Comprehensive guide for building robust web applications and APIs with Express.js.

## Quick Start

### Basic Express Server

```bash
# Create new project
mkdir my-express-app
cd my-express-app
npm init -y

# Install dependencies
npm install express
npm install --save-dev @types/express typescript ts-node nodemon

# TypeScript config
npx tsc --init
```

```typescript
// src/index.ts
import express, { Request, Response, NextFunction } from 'express';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.get('/', (req: Request, res: Response) => {
  res.json({ message: 'Hello World!' });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
```

```json
// package.json scripts
{
  "scripts": {
    "dev": "nodemon src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  }
}
```

---

## Middleware

### Built-in Middleware

```typescript
import express from 'express';

const app = express();

// Parse JSON bodies
app.use(express.json());

// Parse URL-encoded bodies
app.use(express.urlencoded({ extended: true }));

// Serve static files
app.use(express.static('public'));

// Parse cookies (requires cookie-parser)
import cookieParser from 'cookie-parser';
app.use(cookieParser());
```

### Third-Party Middleware

```typescript
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import compression from 'compression';

// CORS
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
  credentials: true
}));

// Security headers
app.use(helmet());

// HTTP request logger
app.use(morgan('combined'));

// Gzip compression
app.use(compression());
```

### Custom Middleware

```typescript
// Logging middleware
const logger = (req: Request, res: Response, next: NextFunction) => {
  console.log(`${req.method} ${req.path} - ${new Date().toISOString()}`);
  next();
};

// Authentication middleware
const authenticate = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');

    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }

    const decoded = verifyToken(token);
    req.user = decoded;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

// Rate limiting
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP'
});

app.use('/api/', limiter);
```

### Middleware Order Matters

```typescript
// ✅ CORRECT ORDER
app.use(helmet());              // 1. Security first
app.use(cors());                // 2. CORS
app.use(morgan('combined'));    // 3. Logging
app.use(express.json());        // 4. Body parsing
app.use(authenticate);          // 5. Authentication
app.use('/api', routes);        // 6. Routes
app.use(errorHandler);          // 7. Error handling (LAST)

// ❌ WRONG - Error handler should be last
app.use(errorHandler);
app.use('/api', routes);
```

---

## Routing

### Basic Routes

```typescript
import { Router } from 'express';

const router = Router();

// GET request
router.get('/users', (req, res) => {
  res.json({ users: [] });
});

// POST request
router.post('/users', (req, res) => {
  const user = req.body;
  res.status(201).json({ user });
});

// PUT request
router.put('/users/:id', (req, res) => {
  const { id } = req.params;
  const updates = req.body;
  res.json({ id, updates });
});

// DELETE request
router.delete('/users/:id', (req, res) => {
  const { id } = req.params;
  res.status(204).send();
});

export default router;
```

### Route Parameters

```typescript
// URL parameters
router.get('/users/:userId/posts/:postId', (req, res) => {
  const { userId, postId } = req.params;
  res.json({ userId, postId });
});

// Optional parameters
router.get('/products/:category/:subcategory?', (req, res) => {
  const { category, subcategory } = req.params;
  res.json({ category, subcategory });
});

// Query parameters
router.get('/search', (req, res) => {
  const { q, page, limit } = req.query;
  res.json({ query: q, page: Number(page), limit: Number(limit) });
});
```

### Router Grouping

```typescript
// routes/users.ts
import { Router } from 'express';

const router = Router();

router.get('/', getAllUsers);
router.get('/:id', getUserById);
router.post('/', createUser);
router.put('/:id', updateUser);
router.delete('/:id', deleteUser);

export default router;

// routes/index.ts
import { Router } from 'express';
import userRoutes from './users';
import postRoutes from './posts';
import authRoutes from './auth';

const router = Router();

router.use('/users', userRoutes);
router.use('/posts', postRoutes);
router.use('/auth', authRoutes);

export default router;

// app.ts
import routes from './routes';
app.use('/api/v1', routes);
```

### Route Handlers

```typescript
// Single handler
app.get('/users', getUsers);

// Multiple handlers
app.get('/users/:id',
  authenticate,
  authorize(['admin', 'user']),
  getUser
);

// Array of handlers
const handlers = [authenticate, authorize(['admin']), deleteUser];
app.delete('/users/:id', handlers);

// Async handlers
const asyncHandler = (fn: Function) => (req: Request, res: Response, next: NextFunction) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

router.get('/users', asyncHandler(async (req, res) => {
  const users = await User.findAll();
  res.json(users);
}));
```

---

## TypeScript Integration

### Type-Safe Request/Response

```typescript
import { Request, Response, NextFunction } from 'express';

// Extend Request type
interface AuthRequest extends Request {
  user?: {
    id: number;
    email: string;
    role: string;
  };
}

// Type-safe route handlers
const getUser = async (req: Request<{ id: string }>, res: Response) => {
  const userId = parseInt(req.params.id);
  const user = await User.findById(userId);
  res.json(user);
};

// Type-safe body
interface CreateUserBody {
  name: string;
  email: string;
  password: string;
}

const createUser = async (
  req: Request<{}, {}, CreateUserBody>,
  res: Response
) => {
  const { name, email, password } = req.body;
  const user = await User.create({ name, email, password });
  res.status(201).json(user);
};

// Type-safe query
interface SearchQuery {
  q?: string;
  page?: string;
  limit?: string;
}

const search = async (
  req: Request<{}, {}, {}, SearchQuery>,
  res: Response
) => {
  const { q, page = '1', limit = '10' } = req.query;
  const results = await search(q, parseInt(page), parseInt(limit));
  res.json(results);
};
```

### Custom Types

```typescript
// types/express.d.ts
import { User } from '../models/User';

declare global {
  namespace Express {
    interface Request {
      user?: User;
      requestId?: string;
    }
  }
}

// Now req.user is available everywhere
const middleware = (req: Request, res: Response, next: NextFunction) => {
  console.log(req.user?.email); // TypeScript knows about user
  next();
};
```

---

## Error Handling

### Synchronous Errors

```typescript
app.get('/users/:id', (req, res, next) => {
  const user = findUser(req.params.id);

  if (!user) {
    const error = new Error('User not found');
    error.status = 404;
    return next(error); // Pass to error handler
  }

  res.json(user);
});
```

### Asynchronous Errors

```typescript
// Using async/await with try-catch
app.get('/users', async (req, res, next) => {
  try {
    const users = await User.findAll();
    res.json(users);
  } catch (error) {
    next(error);
  }
});

// Using asyncHandler wrapper
const asyncHandler = (fn: Function) =>
  (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };

app.get('/users', asyncHandler(async (req, res) => {
  const users = await User.findAll();
  res.json(users);
}));
```

### Global Error Handler

```typescript
// Custom error class
class AppError extends Error {
  statusCode: number;
  isOperational: boolean;

  constructor(message: string, statusCode: number) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

// Error handler middleware (must be last)
const errorHandler = (
  err: AppError,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  err.statusCode = err.statusCode || 500;

  if (process.env.NODE_ENV === 'development') {
    res.status(err.statusCode).json({
      status: 'error',
      error: err,
      message: err.message,
      stack: err.stack
    });
  } else {
    // Production
    if (err.isOperational) {
      res.status(err.statusCode).json({
        status: 'error',
        message: err.message
      });
    } else {
      // Programming or unknown error
      console.error('ERROR:', err);
      res.status(500).json({
        status: 'error',
        message: 'Something went wrong'
      });
    }
  }
};

app.use(errorHandler);

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});
```

---

## Database Integration

### PostgreSQL with Prisma

```typescript
// prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String
  posts     Post[]
  createdAt DateTime @default(now())
}

model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String
  userId    Int
  user      User     @relation(fields: [userId], references: [id])
}
```

```typescript
// db/prisma.ts
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient({
  log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error']
});

export default prisma;

// routes/users.ts
import prisma from '../db/prisma';

router.get('/users', async (req, res) => {
  const users = await prisma.user.findMany({
    include: { posts: true }
  });
  res.json(users);
});

router.post('/users', async (req, res) => {
  const user = await prisma.user.create({
    data: req.body
  });
  res.status(201).json(user);
});
```

### MongoDB with Mongoose

```typescript
import mongoose from 'mongoose';

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI!)
  .then(() => console.log('MongoDB connected'))
  .catch(err => console.error('MongoDB connection error:', err));

// Define schema
const userSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  name: { type: String, required: true },
  password: { type: String, required: true },
  role: { type: String, enum: ['user', 'admin'], default: 'user' },
  createdAt: { type: Date, default: Date.now }
});

const User = mongoose.model('User', userSchema);

// Routes
router.get('/users', async (req, res) => {
  const users = await User.find().select('-password');
  res.json(users);
});

router.post('/users', async (req, res) => {
  const user = new User(req.body);
  await user.save();
  res.status(201).json(user);
});
```

---

## Authentication

### JWT Authentication

```typescript
import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';

const JWT_SECRET = process.env.JWT_SECRET!;
const JWT_EXPIRES_IN = '7d';

// Generate token
const generateToken = (userId: number): string => {
  return jwt.sign({ userId }, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
};

// Verify token
const verifyToken = (token: string): any => {
  return jwt.verify(token, JWT_SECRET);
};

// Register
router.post('/auth/register', async (req, res) => {
  const { email, password, name } = req.body;

  // Hash password
  const hashedPassword = await bcrypt.hash(password, 10);

  // Create user
  const user = await User.create({
    email,
    password: hashedPassword,
    name
  });

  // Generate token
  const token = generateToken(user.id);

  res.status(201).json({ user, token });
});

// Login
router.post('/auth/login', async (req, res) => {
  const { email, password } = req.body;

  // Find user
  const user = await User.findOne({ where: { email } });
  if (!user) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  // Verify password
  const isValid = await bcrypt.compare(password, user.password);
  if (!isValid) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  // Generate token
  const token = generateToken(user.id);

  res.json({ user, token });
});

// Auth middleware
const authenticate = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');

    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }

    const decoded = verifyToken(token);
    const user = await User.findById(decoded.userId);

    if (!user) {
      return res.status(401).json({ error: 'User not found' });
    }

    req.user = user;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

// Protected route
router.get('/profile', authenticate, (req, res) => {
  res.json(req.user);
});
```

### Session-based Authentication

```typescript
import session from 'express-session';
import RedisStore from 'connect-redis';
import { createClient } from 'redis';

// Redis client
const redisClient = createClient({ url: process.env.REDIS_URL });
redisClient.connect();

// Session middleware
app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET!,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    maxAge: 1000 * 60 * 60 * 24 * 7 // 7 days
  }
}));

// Login
router.post('/login', async (req, res) => {
  const { email, password } = req.body;

  const user = await User.findOne({ where: { email } });
  if (!user || !(await bcrypt.compare(password, user.password))) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  req.session.userId = user.id;
  res.json({ user });
});

// Logout
router.post('/logout', (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      return res.status(500).json({ error: 'Logout failed' });
    }
    res.json({ message: 'Logged out successfully' });
  });
});

// Auth middleware
const requireAuth = (req: Request, res: Response, next: NextFunction) => {
  if (!req.session.userId) {
    return res.status(401).json({ error: 'Not authenticated' });
  }
  next();
};
```

---

## Request Validation

### Zod Validation

```typescript
import { z } from 'zod';

const createUserSchema = z.object({
  name: z.string().min(2).max(50),
  email: z.string().email(),
  password: z.string().min(8).regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/),
  age: z.number().int().min(18).optional()
});

const validate = (schema: z.ZodSchema) => {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      schema.parse(req.body);
      next();
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({
          error: 'Validation failed',
          details: error.errors
        });
      }
      next(error);
    }
  };
};

router.post('/users', validate(createUserSchema), async (req, res) => {
  const user = await User.create(req.body);
  res.status(201).json(user);
});
```

### Express Validator

```typescript
import { body, validationResult } from 'express-validator';

router.post('/users',
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 8 }),
  body('name').trim().notEmpty(),
  async (req, res) => {
    const errors = validationResult(req);

    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const user = await User.create(req.body);
    res.status(201).json(user);
  }
);
```

---

## File Uploads

### Multer

```typescript
import multer from 'multer';
import path from 'path';

// Disk storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|gif/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);

    if (extname && mimetype) {
      return cb(null, true);
    }
    cb(new Error('Only image files are allowed'));
  }
});

// Single file
router.post('/upload', upload.single('avatar'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  res.json({
    filename: req.file.filename,
    path: req.file.path,
    size: req.file.size
  });
});

// Multiple files
router.post('/upload-multiple', upload.array('photos', 10), (req, res) => {
  const files = req.files as Express.Multer.File[];

  res.json({
    count: files.length,
    files: files.map(f => ({
      filename: f.filename,
      path: f.path,
      size: f.size
    }))
  });
});
```

---

## Testing

### Supertest + Jest

```typescript
// __tests__/users.test.ts
import request from 'supertest';
import app from '../app';
import prisma from '../db/prisma';

describe('User API', () => {
  beforeAll(async () => {
    // Setup test database
    await prisma.$connect();
  });

  afterAll(async () => {
    await prisma.$disconnect();
  });

  beforeEach(async () => {
    // Clean database before each test
    await prisma.user.deleteMany();
  });

  describe('GET /api/users', () => {
    it('should return empty array when no users', async () => {
      const res = await request(app).get('/api/users');

      expect(res.status).toBe(200);
      expect(res.body).toEqual([]);
    });

    it('should return all users', async () => {
      await prisma.user.createMany({
        data: [
          { email: 'user1@example.com', name: 'User 1' },
          { email: 'user2@example.com', name: 'User 2' }
        ]
      });

      const res = await request(app).get('/api/users');

      expect(res.status).toBe(200);
      expect(res.body).toHaveLength(2);
    });
  });

  describe('POST /api/users', () => {
    it('should create a new user', async () => {
      const userData = {
        email: 'test@example.com',
        name: 'Test User',
        password: 'password123'
      };

      const res = await request(app)
        .post('/api/users')
        .send(userData);

      expect(res.status).toBe(201);
      expect(res.body).toHaveProperty('id');
      expect(res.body.email).toBe(userData.email);
      expect(res.body).not.toHaveProperty('password');
    });

    it('should return 400 for invalid email', async () => {
      const res = await request(app)
        .post('/api/users')
        .send({
          email: 'invalid-email',
          name: 'Test',
          password: 'password123'
        });

      expect(res.status).toBe(400);
      expect(res.body).toHaveProperty('error');
    });
  });

  describe('Authentication', () => {
    it('should login with valid credentials', async () => {
      const user = await prisma.user.create({
        data: {
          email: 'test@example.com',
          name: 'Test User',
          password: await bcrypt.hash('password123', 10)
        }
      });

      const res = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'test@example.com',
          password: 'password123'
        });

      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('token');
    });

    it('should reject invalid credentials', async () => {
      const res = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'wrong@example.com',
          password: 'wrongpassword'
        });

      expect(res.status).toBe(401);
    });

    it('should access protected route with valid token', async () => {
      const token = generateToken(1);

      const res = await request(app)
        .get('/api/profile')
        .set('Authorization', `Bearer ${token}`);

      expect(res.status).toBe(200);
    });
  });
});
```

---

## Production Best Practices

### Environment Variables

```typescript
// config/env.ts
import dotenv from 'dotenv';
import { z } from 'zod';

dotenv.config();

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.string().default('3000'),
  DATABASE_URL: z.string(),
  JWT_SECRET: z.string(),
  REDIS_URL: z.string().optional(),
  ALLOWED_ORIGINS: z.string().default('*')
});

export const env = envSchema.parse(process.env);
```

### Logging

```typescript
import winston from 'winston';

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

export default logger;

// Usage
logger.info('User created', { userId: 123 });
logger.error('Database error', { error: err.message, stack: err.stack });
```

### Graceful Shutdown

```typescript
const server = app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server');

  server.close(() => {
    console.log('HTTP server closed');

    // Close database connections
    prisma.$disconnect()
      .then(() => {
        console.log('Database connection closed');
        process.exit(0);
      })
      .catch((err) => {
        console.error('Error during shutdown', err);
        process.exit(1);
      });
  });
});
```

### Health Check Endpoint

```typescript
router.get('/health', async (req, res) => {
  try {
    // Check database
    await prisma.$queryRaw`SELECT 1`;

    // Check Redis (if used)
    if (redisClient) {
      await redisClient.ping();
    }

    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      error: error.message
    });
  }
});
```

---

## Common Patterns

### Repository Pattern

```typescript
// repositories/UserRepository.ts
class UserRepository {
  async findAll() {
    return await prisma.user.findMany();
  }

  async findById(id: number) {
    return await prisma.user.findUnique({ where: { id } });
  }

  async create(data: CreateUserInput) {
    return await prisma.user.create({ data });
  }

  async update(id: number, data: UpdateUserInput) {
    return await prisma.user.update({ where: { id }, data });
  }

  async delete(id: number) {
    return await prisma.user.delete({ where: { id } });
  }
}

export const userRepository = new UserRepository();

// routes/users.ts
router.get('/users/:id', async (req, res) => {
  const user = await userRepository.findById(parseInt(req.params.id));
  res.json(user);
});
```

### Service Layer

```typescript
// services/UserService.ts
class UserService {
  async createUser(data: CreateUserInput) {
    const hashedPassword = await bcrypt.hash(data.password, 10);

    const user = await userRepository.create({
      ...data,
      password: hashedPassword
    });

    await emailService.sendWelcomeEmail(user.email);

    return user;
  }

  async updateUser(id: number, data: UpdateUserInput) {
    const user = await userRepository.findById(id);

    if (!user) {
      throw new AppError('User not found', 404);
    }

    return await userRepository.update(id, data);
  }
}

export const userService = new UserService();
```

---

## Resources

- Express Documentation: https://expressjs.com/
- TypeScript Express Guide: https://github.com/microsoft/TypeScript-Node-Starter
- Express Best Practices: https://expressjs.com/en/advanced/best-practice-performance.html
- Helmet Security: https://helmetjs.github.io/
- Express Rate Limit: https://github.com/express-rate-limit/express-rate-limit
