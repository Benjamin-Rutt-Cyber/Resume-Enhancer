---
name: nextjs
description: Expert knowledge in Next.js including App Router, Server Components, Client Components, routing, data fetching, API routes, middleware, and deployment.
allowed-tools: [Read, Write, Edit, Bash]
---

# Next.js Skill

Comprehensive knowledge for building modern full-stack React applications with Next.js 14+.

## Quick Start

### Installation

```bash
# Create new Next.js app (App Router - recommended)
npx create-next-app@latest my-app
cd my-app

# Interactive prompts will ask:
# - TypeScript? Yes
# - ESLint? Yes
# - Tailwind CSS? Yes
# - `src/` directory? Yes
# - App Router? Yes (recommended)
# - Import alias? @/*

# Start development server
npm run dev

# Open http://localhost:3000
```

### Project Structure (App Router)

```
my-app/
├── src/
│   ├── app/                  # App Router (Next.js 13+)
│   │   ├── layout.tsx        # Root layout
│   │   ├── page.tsx          # Home page
│   │   ├── globals.css       # Global styles
│   │   ├── api/              # API routes
│   │   │   └── users/
│   │   │       └── route.ts  # /api/users endpoint
│   │   ├── dashboard/        # /dashboard route
│   │   │   ├── layout.tsx    # Dashboard layout
│   │   │   └── page.tsx      # Dashboard page
│   │   └── [id]/             # Dynamic route
│   │       └── page.tsx      # /[id] page
│   ├── components/           # React components
│   ├── lib/                  # Utilities and helpers
│   └── types/                # TypeScript types
├── public/                   # Static assets
├── next.config.js            # Next.js configuration
├── package.json
└── tsconfig.json
```

### Basic Page Component

```typescript
// src/app/page.tsx
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold">Welcome to Next.js 14</h1>
      <p className="mt-4 text-xl">The React Framework for Production</p>
    </main>
  );
}
```

---

## Core Concepts

### 1. App Router vs Pages Router

**App Router (Recommended - Next.js 13+)**
- Uses `app/` directory
- Server Components by default
- Nested layouts
- Server Actions
- Better performance

**Pages Router (Legacy)**
- Uses `pages/` directory
- Client-side rendering by default
- File-based routing
- API routes in `pages/api/`

**Migration:** You can use both routers simultaneously during migration.

---

### 2. Server Components (Default)

Server Components render on the server and send HTML to the client.

```typescript
// app/users/page.tsx (Server Component by default)
async function getUsers() {
  const res = await fetch('https://api.example.com/users', {
    cache: 'no-store' // Disable caching for dynamic data
  });
  return res.json();
}

export default async function UsersPage() {
  const users = await getUsers();

  return (
    <div>
      <h1>Users</h1>
      <ul>
        {users.map((user: any) => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

**Benefits:**
- Zero JavaScript sent to client
- Direct database access
- Better performance
- Automatic code splitting

**Limitations:**
- No hooks (useState, useEffect)
- No browser APIs
- No event listeners

---

### 3. Client Components

Use `'use client'` directive for interactive components.

```typescript
// components/Counter.tsx
'use client';

import { useState } from 'react';

export default function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
}
```

**When to use Client Components:**
- Need React hooks (useState, useEffect, etc.)
- Need browser APIs (localStorage, window, etc.)
- Need event listeners (onClick, onChange, etc.)
- Need third-party libraries that use hooks

**Best Practice:** Keep Client Components small and nested within Server Components.

---

### 4. Layouts

Layouts wrap multiple pages and persist across navigation.

```typescript
// app/layout.tsx (Root Layout - Required)
import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'My App',
  description: 'My Next.js application',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
```

**Nested Layouts:**

```typescript
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="dashboard">
      <nav>Dashboard Navigation</nav>
      <main>{children}</main>
    </div>
  );
}
```

---

### 5. Routing

#### Basic Routes

File system-based routing in `app/` directory:

```
app/
├── page.tsx              → /
├── about/
│   └── page.tsx          → /about
├── blog/
│   ├── page.tsx          → /blog
│   └── [slug]/
│       └── page.tsx      → /blog/:slug
└── dashboard/
    ├── page.tsx          → /dashboard
    └── settings/
        └── page.tsx      → /dashboard/settings
```

#### Dynamic Routes

```typescript
// app/blog/[slug]/page.tsx
interface PageProps {
  params: { slug: string };
  searchParams: { [key: string]: string | string[] | undefined };
}

export default async function BlogPost({ params }: PageProps) {
  const { slug } = params;
  const post = await getPost(slug);

  return (
    <article>
      <h1>{post.title}</h1>
      <div>{post.content}</div>
    </article>
  );
}
```

#### Catch-All Routes

```typescript
// app/shop/[...slug]/page.tsx
// Matches /shop/a, /shop/a/b, /shop/a/b/c

interface PageProps {
  params: { slug: string[] };
}

export default function ShopPage({ params }: PageProps) {
  const path = params.slug.join('/');
  return <div>Path: {path}</div>;
}
```

#### Optional Catch-All Routes

```typescript
// app/docs/[[...slug]]/page.tsx
// Matches /docs, /docs/a, /docs/a/b
```

---

### 6. Navigation

#### Link Component

```typescript
import Link from 'next/link';

export default function Nav() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about">About</Link>
      <Link href="/blog/first-post">First Post</Link>

      {/* Prefetching (automatic for visible links) */}
      <Link href="/dashboard" prefetch={false}>
        Dashboard (no prefetch)
      </Link>
    </nav>
  );
}
```

#### Programmatic Navigation (Client Component)

```typescript
'use client';

import { useRouter } from 'next/navigation';

export default function LoginForm() {
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Login logic...
    router.push('/dashboard');
    // router.replace('/dashboard'); // No history entry
    // router.back(); // Go back
    // router.forward(); // Go forward
    // router.refresh(); // Refresh current route
  };

  return <form onSubmit={handleSubmit}>...</form>;
}
```

---

### 7. Data Fetching

#### Server Components (Async/Await)

```typescript
// app/posts/page.tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    // Caching options:
    cache: 'force-cache',    // Default - cache indefinitely
    // cache: 'no-store',    // No caching - always fresh
    // next: { revalidate: 60 } // Revalidate every 60 seconds
  });

  if (!res.ok) {
    throw new Error('Failed to fetch posts');
  }

  return res.json();
}

export default async function PostsPage() {
  const posts = await getPosts();

  return (
    <div>
      {posts.map((post: any) => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>{post.excerpt}</p>
        </article>
      ))}
    </div>
  );
}
```

#### Static Site Generation (SSG)

```typescript
// Automatic if using cache: 'force-cache' (default)
async function getStaticData() {
  const res = await fetch('https://api.example.com/data', {
    cache: 'force-cache'
  });
  return res.json();
}
```

#### Incremental Static Regeneration (ISR)

```typescript
// Revalidate every 60 seconds
async function getISRData() {
  const res = await fetch('https://api.example.com/data', {
    next: { revalidate: 60 }
  });
  return res.json();
}
```

#### Dynamic Rendering (SSR)

```typescript
// Opt out of caching for always-fresh data
async function getDynamicData() {
  const res = await fetch('https://api.example.com/data', {
    cache: 'no-store'
  });
  return res.json();
}

// Or force dynamic rendering for entire route
export const dynamic = 'force-dynamic';
```

#### Parallel Data Fetching

```typescript
export default async function Page() {
  // Fetch in parallel
  const [users, posts] = await Promise.all([
    getUsers(),
    getPosts()
  ]);

  return (
    <div>
      <UserList users={users} />
      <PostList posts={posts} />
    </div>
  );
}
```

---

### 8. API Routes (Route Handlers)

```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';

// GET /api/users
export async function GET(request: NextRequest) {
  const users = await db.user.findMany();

  return NextResponse.json(users);
}

// POST /api/users
export async function POST(request: NextRequest) {
  const body = await request.json();
  const user = await db.user.create({ data: body });

  return NextResponse.json(user, { status: 201 });
}

// Dynamic route: app/api/users/[id]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = await db.user.findUnique({
    where: { id: params.id }
  });

  if (!user) {
    return NextResponse.json(
      { error: 'User not found' },
      { status: 404 }
    );
  }

  return NextResponse.json(user);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const body = await request.json();
  const user = await db.user.update({
    where: { id: params.id },
    data: body
  });

  return NextResponse.json(user);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  await db.user.delete({ where: { id: params.id } });
  return NextResponse.json({ success: true });
}
```

#### Headers and Cookies

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { cookies, headers } from 'next/headers';

export async function GET(request: NextRequest) {
  // Read headers
  const headersList = headers();
  const authorization = headersList.get('authorization');

  // Read cookies
  const cookieStore = cookies();
  const token = cookieStore.get('token');

  // Set cookies in response
  const response = NextResponse.json({ data: 'success' });
  response.cookies.set('session', 'abc123', {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    maxAge: 60 * 60 * 24 * 7 // 1 week
  });

  return response;
}
```

---

### 9. Server Actions

Server-side mutations without API routes.

```typescript
// app/actions.ts
'use server';

import { revalidatePath } from 'next/cache';

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  const post = await db.post.create({
    data: { title, content }
  });

  // Revalidate the posts page
  revalidatePath('/posts');

  return { success: true, post };
}

export async function deletePost(id: string) {
  await db.post.delete({ where: { id } });
  revalidatePath('/posts');
}
```

#### Using Server Actions in Forms

```typescript
// app/new-post/page.tsx
import { createPost } from '@/app/actions';

export default function NewPostPage() {
  return (
    <form action={createPost}>
      <input type="text" name="title" required />
      <textarea name="content" required />
      <button type="submit">Create Post</button>
    </form>
  );
}
```

#### Using Server Actions with useTransition (Client Component)

```typescript
'use client';

import { useTransition } from 'react';
import { deletePost } from '@/app/actions';

export default function DeleteButton({ id }: { id: string }) {
  const [isPending, startTransition] = useTransition();

  const handleDelete = () => {
    startTransition(async () => {
      await deletePost(id);
    });
  };

  return (
    <button onClick={handleDelete} disabled={isPending}>
      {isPending ? 'Deleting...' : 'Delete'}
    </button>
  );
}
```

---

### 10. Middleware

Runs before requests are completed.

```typescript
// middleware.ts (at project root)
import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  // Authentication example
  const token = request.cookies.get('token');

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Add custom header
  const response = NextResponse.next();
  response.headers.set('x-custom-header', 'value');

  return response;
}

// Specify which routes to run middleware on
export const config = {
  matcher: [
    '/dashboard/:path*',
    '/api/:path*',
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
```

#### Redirect Example

```typescript
export function middleware(request: NextRequest) {
  if (request.nextUrl.pathname === '/old-path') {
    return NextResponse.redirect(new URL('/new-path', request.url));
  }
}
```

#### Rewrite Example

```typescript
export function middleware(request: NextRequest) {
  // Serve /about content for /info route
  if (request.nextUrl.pathname === '/info') {
    return NextResponse.rewrite(new URL('/about', request.url));
  }
}
```

---

### 11. Loading States

```typescript
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="spinner">Loading...</div>
    </div>
  );
}
```

#### Suspense Boundaries

```typescript
// app/dashboard/page.tsx
import { Suspense } from 'react';

async function UserList() {
  const users = await getUsers(); // Slow operation
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<div>Loading users...</div>}>
        <UserList />
      </Suspense>
    </div>
  );
}
```

---

### 12. Error Handling

```typescript
// app/dashboard/error.tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

#### Global Error Handler

```typescript
// app/global-error.tsx
'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body>
        <h2>Application Error</h2>
        <button onClick={reset}>Try again</button>
      </body>
    </html>
  );
}
```

#### Not Found Pages

```typescript
// app/not-found.tsx
import Link from 'next/link';

export default function NotFound() {
  return (
    <div>
      <h2>Not Found</h2>
      <p>Could not find requested resource</p>
      <Link href="/">Return Home</Link>
    </div>
  );
}
```

---

### 13. Metadata & SEO

```typescript
// app/page.tsx
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'My App',
  description: 'My awesome Next.js app',
  keywords: ['next.js', 'react', 'typescript'],
  authors: [{ name: 'Your Name' }],
  openGraph: {
    title: 'My App',
    description: 'My awesome Next.js app',
    images: ['/og-image.jpg'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'My App',
    description: 'My awesome Next.js app',
    images: ['/og-image.jpg'],
  },
};
```

#### Dynamic Metadata

```typescript
// app/blog/[slug]/page.tsx
export async function generateMetadata(
  { params }: { params: { slug: string } }
): Promise<Metadata> {
  const post = await getPost(params.slug);

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [post.coverImage],
    },
  };
}
```

---

### 14. Image Optimization

```typescript
import Image from 'next/image';

export default function Page() {
  return (
    <>
      {/* Local image */}
      <Image
        src="/hero.jpg"
        alt="Hero image"
        width={1200}
        height={600}
        priority // Load immediately
      />

      {/* Remote image */}
      <Image
        src="https://example.com/image.jpg"
        alt="Remote image"
        width={800}
        height={400}
        quality={75}
      />

      {/* Responsive image */}
      <Image
        src="/responsive.jpg"
        alt="Responsive"
        fill // Fill parent container
        style={{ objectFit: 'cover' }}
      />
    </>
  );
}
```

Configure remote image domains:

```javascript
// next.config.js
module.exports = {
  images: {
    domains: ['example.com', 'cdn.example.com'],
  },
};
```

---

### 15. Environment Variables

```bash
# .env.local
DATABASE_URL="postgresql://..."
NEXT_PUBLIC_API_URL="https://api.example.com"
SECRET_KEY="abc123"
```

```typescript
// Server-side only (secure)
const dbUrl = process.env.DATABASE_URL;

// Client-side accessible (prefixed with NEXT_PUBLIC_)
const apiUrl = process.env.NEXT_PUBLIC_API_URL;
```

---

### 16. Styling

#### Tailwind CSS (Recommended)

```typescript
// Already included in create-next-app
export default function Button() {
  return (
    <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
      Click me
    </button>
  );
}
```

#### CSS Modules

```css
/* components/Button.module.css */
.button {
  padding: 10px 20px;
  background: blue;
  color: white;
  border-radius: 4px;
}

.button:hover {
  background: darkblue;
}
```

```typescript
import styles from './Button.module.css';

export default function Button() {
  return <button className={styles.button}>Click me</button>;
}
```

#### Global Styles

```css
/* app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

html,
body {
  padding: 0;
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
```

---

### 17. TypeScript Types

```typescript
// types/index.ts
export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
}

export interface Post {
  id: string;
  title: string;
  content: string;
  authorId: string;
  createdAt: Date;
}

export interface ApiResponse<T> {
  data: T;
  error?: string;
  message?: string;
}
```

Usage:

```typescript
import { User, ApiResponse } from '@/types';

async function getUser(id: string): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  const data: ApiResponse<User> = await res.json();
  return data.data;
}
```

---

### 18. Testing

#### Jest Setup

```bash
npm install -D jest @testing-library/react @testing-library/jest-dom jest-environment-jsdom
```

```javascript
// jest.config.js
const nextJest = require('next/jest');

const createJestConfig = nextJest({
  dir: './',
});

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
};

module.exports = createJestConfig(customJestConfig);
```

```javascript
// jest.setup.js
import '@testing-library/jest-dom';
```

#### Component Test Example

```typescript
// __tests__/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import Button from '@/components/Button';

describe('Button', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

---

### 19. Deployment

#### Vercel (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Production deployment
vercel --prod
```

Or connect your GitHub repo to Vercel for automatic deployments.

#### Docker

```dockerfile
# Dockerfile
FROM node:18-alpine AS base

# Dependencies
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Build
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production
FROM base AS runner
WORKDIR /app
ENV NODE_ENV production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
```

```javascript
// next.config.js
module.exports = {
  output: 'standalone',
};
```

---

### 20. Configuration

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Output directory
  distDir: 'build',

  // Strict mode
  reactStrictMode: true,

  // Image optimization
  images: {
    domains: ['example.com'],
    formats: ['image/avif', 'image/webp'],
  },

  // Environment variables
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },

  // Redirects
  async redirects() {
    return [
      {
        source: '/old-path',
        destination: '/new-path',
        permanent: true,
      },
    ];
  },

  // Rewrites
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://api.example.com/:path*',
      },
    ];
  },

  // Headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
```

---

## Best Practices

### 1. Server Components by Default

Use Server Components for:
- Data fetching
- Backend logic
- SEO-critical content
- Large dependencies (charts, markdown)

Only use Client Components when necessary (interactivity, hooks).

### 2. Data Fetching Patterns

```typescript
// ✅ Good: Fetch in parallel
const [users, posts] = await Promise.all([
  getUsers(),
  getPosts()
]);

// ❌ Bad: Sequential fetching
const users = await getUsers();
const posts = await getPosts(); // Waits for users
```

### 3. Minimize Client-Side JavaScript

```typescript
// ✅ Good: Server Component with nested Client Component
export default async function Page() {
  const data = await getData();

  return (
    <div>
      <StaticContent data={data} />
      <InteractiveButton /> {/* Only this is client-side */}
    </div>
  );
}

// ❌ Bad: Entire page as Client Component
'use client';
export default function Page() {
  // All code sent to client
}
```

### 4. Caching Strategy

```typescript
// Static data (rarely changes)
fetch(url, { cache: 'force-cache' })

// Dynamic data (always fresh)
fetch(url, { cache: 'no-store' })

// ISR (revalidate periodically)
fetch(url, { next: { revalidate: 3600 } })
```

### 5. Loading and Error States

Always provide loading and error boundaries:

```
app/
├── layout.tsx
├── page.tsx
├── loading.tsx          ← Loading state
├── error.tsx            ← Error boundary
└── not-found.tsx        ← 404 page
```

### 6. Metadata for SEO

Always set metadata:

```typescript
export const metadata = {
  title: 'Page Title',
  description: 'Page description',
  openGraph: { ... },
};
```

### 7. Image Optimization

Always use `<Image>` component instead of `<img>`:

```typescript
import Image from 'next/image';

<Image src="/photo.jpg" alt="Photo" width={500} height={300} />
```

### 8. Type Safety

Use TypeScript interfaces for all data:

```typescript
interface PageProps {
  params: { id: string };
  searchParams: { [key: string]: string | string[] | undefined };
}

export default async function Page({ params, searchParams }: PageProps) {
  // Type-safe
}
```

---

## Common Patterns

### Authentication with Middleware

```typescript
// middleware.ts
import { NextRequest, NextResponse } from 'next/server';

export async function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token');

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}
```

### Database with Prisma

```typescript
// lib/prisma.ts
import { PrismaClient } from '@prisma/client';

const globalForPrisma = global as unknown as { prisma: PrismaClient };

export const prisma = globalForPrisma.prisma || new PrismaClient();

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;
```

### State Management with Zustand

```typescript
// lib/store.ts
import { create } from 'zustand';

interface State {
  count: number;
  increment: () => void;
}

export const useStore = create<State>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}));
```

---

## Performance Tips

1. **Use Server Components** - Reduce client-side JavaScript
2. **Optimize Images** - Always use `next/image`
3. **Code Splitting** - Automatic with App Router
4. **Lazy Loading** - Use `dynamic()` for heavy components
5. **Caching** - Use appropriate cache strategies
6. **Prefetching** - Links are automatically prefetched
7. **Bundle Analysis** - Run `npm run build` to analyze bundles

---

## Resources

- **Official Docs:** https://nextjs.org/docs
- **Learn Next.js:** https://nextjs.org/learn
- **Examples:** https://github.com/vercel/next.js/tree/canary/examples
- **Discord:** https://nextjs.org/discord
- **GitHub:** https://github.com/vercel/next.js

---

## Troubleshooting

### "use client" Not Working

Make sure directive is at the very top of the file:

```typescript
'use client'; // Must be first line

import { useState } from 'react';
```

### Hydration Errors

Ensure server and client HTML match. Common causes:
- Using browser APIs in Server Components
- Different content on server vs client
- Invalid HTML nesting

### Build Errors

```bash
# Clear cache
rm -rf .next
npm run dev
```

### Type Errors

```bash
# Regenerate types
npm run build
```

This comprehensive skill covers Next.js 14+ with App Router, Server Components, and modern patterns!
