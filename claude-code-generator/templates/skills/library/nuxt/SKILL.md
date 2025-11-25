---
name: nuxt
description: Expert knowledge in Nuxt 3 including Composition API, auto-imports, file-based routing, server routes, data fetching, and deployment strategies.
allowed-tools: [Read, Write, Edit, Bash]
---

# Nuxt.js Skill

Comprehensive knowledge for building modern Vue.js applications with Nuxt 3.

## Quick Start

### Installation

```bash
# Create new Nuxt 3 app
npx nuxi@latest init my-app
cd my-app

# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

### Project Structure

```
my-app/
├── .nuxt/               # Generated files (git-ignored)
├── .output/             # Production build
├── assets/              # Uncompiled assets (Sass, images)
├── components/          # Vue components (auto-imported)
├── composables/         # Composables (auto-imported)
├── layouts/             # Layout components
├── middleware/          # Route middleware
├── pages/               # File-based routing
├── plugins/             # Vue plugins
├── public/              # Static files served at /
├── server/              # Server routes and API
│   ├── api/            # API routes (/api/*)
│   ├── routes/         # Server routes
│   └── middleware/     # Server middleware
├── utils/               # Utilities (auto-imported)
├── app.vue              # Root component (if no pages/)
├── nuxt.config.ts       # Nuxt configuration
└── package.json
```

### Basic Page

```vue
<!-- pages/index.vue -->
<template>
  <div>
    <h1>Welcome to Nuxt 3</h1>
    <p>The Intuitive Vue Framework</p>
  </div>
</template>

<script setup lang="ts">
// Auto-imported composables
const { data: users } = await useFetch('/api/users');
</script>

<style scoped>
h1 {
  font-size: 2rem;
  font-weight: bold;
}
</style>
```

---

## Core Concepts

### 1. Auto-Imports

Nuxt automatically imports:
- Vue composables (`ref`, `computed`, `watch`)
- Nuxt composables (`useFetch`, `navigateTo`, `useState`)
- Components from `components/`
- Composables from `composables/`
- Utilities from `utils/`

```vue
<script setup>
// No imports needed!
const count = ref(0);
const doubled = computed(() => count.value * 2);

const increment = () => count.value++;
</script>
```

### 2. Composition API

```vue
<script setup lang="ts">
// Reactive state
const count = ref(0);
const user = reactive({ name: 'John', age: 30 });

// Computed properties
const doubleCount = computed(() => count.value * 2);

// Watchers
watch(count, (newValue, oldValue) => {
  console.log(`Count changed from ${oldValue} to ${newValue}`);
});

// Lifecycle hooks
onMounted(() => {
  console.log('Component mounted');
});

onUnmounted(() => {
  console.log('Component unmounted');
});
</script>
```

### 3. TypeScript Support

```vue
<script setup lang="ts">
interface User {
  id: number;
  name: string;
  email: string;
}

const user = ref<User | null>(null);

const { data } = await useFetch<User[]>('/api/users');
</script>
```

---

## Routing

### File-Based Routing

```
pages/
├── index.vue                    → /
├── about.vue                    → /about
├── users/
│   ├── index.vue                → /users
│   ├── [id].vue                 → /users/:id
│   └── create.vue               → /users/create
└── blog/
    ├── index.vue                → /blog
    └── [slug].vue               → /blog/:slug
```

### Dynamic Routes

```vue
<!-- pages/users/[id].vue -->
<template>
  <div>
    <h1>User {{ id }}</h1>
    <div v-if="user">
      <p>Name: {{ user.name }}</p>
      <p>Email: {{ user.email }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const id = route.params.id;

const { data: user } = await useFetch(`/api/users/${id}`);
</script>
```

### Catch-All Routes

```vue
<!-- pages/[...slug].vue -->
<!-- Matches /a, /a/b, /a/b/c -->
<script setup>
const route = useRoute();
const slug = route.params.slug; // ['a', 'b', 'c']
</script>
```

### Nested Routes

```
pages/
└── users/
    ├── index.vue                # /users (matches when no child)
    └── [id]/
        ├── index.vue            # /users/:id
        ├── posts.vue            # /users/:id/posts
        └── settings.vue         # /users/:id/settings
```

Parent layout:

```vue
<!-- pages/users/[id].vue -->
<template>
  <div>
    <h1>User Dashboard</h1>
    <nav>
      <NuxtLink :to="`/users/${id}`">Profile</NuxtLink>
      <NuxtLink :to="`/users/${id}/posts`">Posts</NuxtLink>
      <NuxtLink :to="`/users/${id}/settings`">Settings</NuxtLink>
    </nav>
    <NuxtPage />
  </div>
</template>
```

### Navigation

```vue
<template>
  <div>
    <!-- Declarative -->
    <NuxtLink to="/">Home</NuxtLink>
    <NuxtLink to="/about">About</NuxtLink>
    <NuxtLink :to="`/users/${userId}`">User Profile</NuxtLink>

    <!-- Programmatic -->
    <button @click="goToHome">Go Home</button>
  </div>
</template>

<script setup>
const router = useRouter();

const goToHome = () => {
  navigateTo('/');
  // or router.push('/');
};

// Navigate with query params
const goToSearch = () => {
  navigateTo({ path: '/search', query: { q: 'nuxt' } });
};
</script>
```

---

## Layouts

### Default Layout

```vue
<!-- layouts/default.vue -->
<template>
  <div>
    <header>
      <nav>
        <NuxtLink to="/">Home</NuxtLink>
        <NuxtLink to="/about">About</NuxtLink>
      </nav>
    </header>
    <main>
      <slot />
    </main>
    <footer>
      <p>&copy; 2024 My App</p>
    </footer>
  </div>
</template>
```

### Custom Layouts

```vue
<!-- layouts/admin.vue -->
<template>
  <div class="admin-layout">
    <aside>Admin Sidebar</aside>
    <main>
      <slot />
    </main>
  </div>
</template>
```

Using custom layout in a page:

```vue
<!-- pages/admin/dashboard.vue -->
<template>
  <div>
    <h1>Admin Dashboard</h1>
  </div>
</template>

<script setup>
definePageMeta({
  layout: 'admin'
});
</script>
```

---

## Components

### Auto-Imported Components

```
components/
├── Button.vue              → <Button />
├── form/
│   └── Input.vue           → <FormInput />
└── dashboard/
    └── Chart.vue           → <DashboardChart />
```

```vue
<!-- components/Button.vue -->
<template>
  <button :class="variant">
    <slot />
  </button>
</template>

<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary';
}

withDefaults(defineProps<Props>(), {
  variant: 'primary'
});
</script>
```

Usage (no import needed):

```vue
<template>
  <Button variant="primary">Click me</Button>
  <FormInput placeholder="Enter name" />
</template>
```

### Props and Emits

```vue
<!-- components/TodoItem.vue -->
<template>
  <div>
    <span>{{ todo.text }}</span>
    <button @click="emit('delete')">Delete</button>
  </div>
</template>

<script setup lang="ts">
interface Todo {
  id: number;
  text: string;
}

interface Props {
  todo: Todo;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  delete: [];
}>();
</script>
```

---

## Data Fetching

### useFetch

```vue
<script setup lang="ts">
// Basic fetch
const { data, pending, error, refresh } = await useFetch('/api/users');

// With options
const { data } = await useFetch('/api/posts', {
  method: 'POST',
  body: { title: 'New Post' },
  headers: { 'Authorization': 'Bearer token' },
  query: { page: 1 },
  lazy: true, // Don't block navigation
  server: false, // Client-side only
  pick: ['id', 'title'], // Pick specific fields
  transform: (data) => data.map(item => item.name),
});

// Dynamic URL
const userId = ref(1);
const { data: user } = await useFetch(`/api/users/${userId.value}`);

// Watch for changes
watch(userId, () => refresh());
</script>
```

### useAsyncData

```vue
<script setup>
// Custom async function
const { data, pending } = await useAsyncData('users', () => {
  return $fetch('/api/users');
});

// With key for caching
const { data: user } = await useAsyncData(`user-${id}`, () => {
  return $fetch(`/api/users/${id}`);
});
</script>
```

### useLazyFetch & useLazyAsyncData

```vue
<script setup>
// Non-blocking fetch (doesn't block navigation)
const { data, pending } = useLazyFetch('/api/users');
</script>

<template>
  <div v-if="pending">Loading...</div>
  <div v-else>
    <div v-for="user in data" :key="user.id">
      {{ user.name }}
    </div>
  </div>
</template>
```

### Refresh Data

```vue
<script setup>
const { data, refresh } = await useFetch('/api/users');

const addUser = async () => {
  await $fetch('/api/users', { method: 'POST', body: {...} });
  refresh(); // Refresh data
};
</script>
```

---

## Server Routes & API

### API Routes

```typescript
// server/api/users.get.ts
export default defineEventHandler(async (event) => {
  const users = await db.user.findMany();
  return users;
});
```

```typescript
// server/api/users.post.ts
export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const user = await db.user.create({ data: body });
  return user;
});
```

```typescript
// server/api/users/[id].get.ts
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id');
  const user = await db.user.findUnique({ where: { id } });

  if (!user) {
    throw createError({
      statusCode: 404,
      statusMessage: 'User not found'
    });
  }

  return user;
});
```

### Query Parameters

```typescript
// server/api/search.get.ts
export default defineEventHandler((event) => {
  const query = getQuery(event);
  const { q, page, limit } = query;

  // /api/search?q=nuxt&page=1&limit=10
  return { q, page, limit };
});
```

### Headers and Cookies

```typescript
// server/api/auth.ts
export default defineEventHandler((event) => {
  // Read headers
  const authorization = getHeader(event, 'authorization');

  // Read cookies
  const token = getCookie(event, 'token');

  // Set cookie
  setCookie(event, 'session', 'abc123', {
    httpOnly: true,
    secure: true,
    maxAge: 60 * 60 * 24 * 7 // 1 week
  });

  return { authorized: true };
});
```

### Database with Prisma

```typescript
// server/api/posts/index.get.ts
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export default defineEventHandler(async () => {
  const posts = await prisma.post.findMany({
    include: { author: true },
    orderBy: { createdAt: 'desc' }
  });

  return posts;
});
```

---

## State Management

### useState (Built-in)

```vue
<script setup>
// Global reactive state
const counter = useState('counter', () => 0);

const increment = () => counter.value++;
</script>
```

Shared across components:

```vue
<!-- ComponentA.vue -->
<script setup>
const count = useState('sharedCount', () => 0);
</script>
<template>
  <button @click="count++">Increment: {{ count }}</button>
</template>

<!-- ComponentB.vue -->
<script setup>
const count = useState('sharedCount'); // Same state
</script>
<template>
  <div>Count: {{ count }}</div>
</template>
```

### Pinia

```bash
npm install pinia @pinia/nuxt
```

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@pinia/nuxt'],
});
```

```typescript
// stores/user.ts
import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    name: 'John',
    email: 'john@example.com',
  }),

  getters: {
    fullInfo: (state) => `${state.name} (${state.email})`,
  },

  actions: {
    async updateName(name: string) {
      this.name = name;
      await $fetch('/api/user', { method: 'PUT', body: { name } });
    },
  },
});
```

Usage:

```vue
<script setup>
const userStore = useUserStore();
const { name, email, fullInfo } = storeToRefs(userStore);
</script>

<template>
  <div>
    <p>{{ fullInfo }}</p>
    <button @click="userStore.updateName('Jane')">Update Name</button>
  </div>
</template>
```

---

## Middleware

### Route Middleware

```typescript
// middleware/auth.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const user = useState('user');

  if (!user.value && to.path !== '/login') {
    return navigateTo('/login');
  }
});
```

Use in page:

```vue
<!-- pages/dashboard.vue -->
<script setup>
definePageMeta({
  middleware: 'auth'
});
</script>
```

### Global Middleware

```typescript
// middleware/auth.global.ts (runs on every route)
export default defineNuxtRouteMiddleware((to, from) => {
  console.log('Navigating to:', to.path);
});
```

### Server Middleware

```typescript
// server/middleware/log.ts
export default defineEventHandler((event) => {
  console.log('Request:', event.node.req.url);
});
```

---

## Plugins

```typescript
// plugins/my-plugin.ts
export default defineNuxtPlugin((nuxtApp) => {
  // Provide a helper
  return {
    provide: {
      hello: (msg: string) => `Hello ${msg}!`
    }
  };
});
```

Usage:

```vue
<script setup>
const { $hello } = useNuxtApp();
console.log($hello('World')); // "Hello World!"
</script>
```

### Vue Plugin

```typescript
// plugins/vue-plugin.ts
import VuePlugin from 'some-vue-plugin';

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(VuePlugin);
});
```

---

## Composables

```typescript
// composables/useCounter.ts
export const useCounter = () => {
  const count = useState('counter', () => 0);

  const increment = () => count.value++;
  const decrement = () => count.value--;
  const reset = () => count.value = 0;

  return {
    count,
    increment,
    decrement,
    reset,
  };
};
```

Usage (auto-imported):

```vue
<script setup>
const { count, increment, decrement } = useCounter();
</script>

<template>
  <div>
    <p>Count: {{ count }}</p>
    <button @click="increment">+</button>
    <button @click="decrement">-</button>
  </div>
</template>
```

---

## Modules

### Using Modules

```bash
npm install @nuxtjs/tailwindcss
```

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@nuxt/image',
  ],
});
```

### Popular Modules

- `@nuxtjs/tailwindcss` - Tailwind CSS
- `@pinia/nuxt` - State management
- `@nuxt/image` - Image optimization
- `@nuxtjs/color-mode` - Dark mode
- `@vueuse/nuxt` - Vue composition utilities
- `nuxt-icon` - Icon components

---

## Rendering Modes

### Universal Rendering (SSR - Default)

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  ssr: true, // Default
});
```

### Client-Side Rendering (SPA)

```typescript
export default defineNuxtConfig({
  ssr: false,
});
```

### Hybrid Rendering

```vue
<!-- pages/about.vue -->
<script setup>
definePageMeta({
  ssr: false // This page only renders on client
});
</script>
```

### Static Site Generation

```bash
# Generate static site
npm run generate

# Output in .output/public/
```

---

## Configuration

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  // App configuration
  app: {
    head: {
      title: 'My App',
      meta: [
        { name: 'description', content: 'My awesome app' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },

  // Runtime config
  runtimeConfig: {
    // Private keys (server-only)
    apiSecret: process.env.API_SECRET,

    // Public keys (exposed to client)
    public: {
      apiBase: process.env.API_BASE_URL || '/api'
    }
  },

  // CSS
  css: ['~/assets/css/main.css'],

  // Auto-import configuration
  imports: {
    dirs: ['stores', 'composables/**']
  },

  // Nitro server configuration
  nitro: {
    routeRules: {
      '/admin/**': { ssr: false },
      '/api/**': { cors: true },
    }
  },

  // Development
  devtools: { enabled: true },
});
```

### Environment Variables

```bash
# .env
API_SECRET="secret123"
API_BASE_URL="https://api.example.com"
```

Access in code:

```typescript
// Server-side
const config = useRuntimeConfig();
console.log(config.apiSecret); // Server only

// Client-side
const config = useRuntimeConfig();
console.log(config.public.apiBase); // Accessible on client
```

---

## SEO & Meta Tags

### Page Meta

```vue
<script setup lang="ts">
useSeoMeta({
  title: 'My Page',
  ogTitle: 'My Page',
  description: 'My page description',
  ogDescription: 'My page description',
  ogImage: 'https://example.com/image.jpg',
  twitterCard: 'summary_large_image',
});
</script>
```

### Dynamic Meta

```vue
<script setup>
const route = useRoute();
const { data: post } = await useFetch(`/api/posts/${route.params.id}`);

useHead({
  title: post.value?.title,
  meta: [
    { name: 'description', content: post.value?.excerpt }
  ]
});
</script>
```

---

## Deployment

### Static Hosting (Generate)

```bash
npm run generate
# Upload .output/public/ to any static host
```

### Node.js Server

```bash
npm run build
npm run preview # Test locally
node .output/server/index.mjs # Production
```

### Vercel

```bash
npm install -g vercel
vercel
```

Or connect GitHub repo to Vercel.

### Netlify

```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = ".output/public"
```

### Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
```

---

## Testing

### Vitest

```bash
npm install -D @nuxt/test-utils vitest @vue/test-utils
```

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'nuxt',
  },
});
```

```typescript
// tests/components/Button.test.ts
import { mount } from '@vue/test-utils';
import Button from '@/components/Button.vue';

describe('Button', () => {
  it('renders correctly', () => {
    const wrapper = mount(Button, {
      slots: { default: 'Click me' }
    });
    expect(wrapper.text()).toBe('Click me');
  });
});
```

---

## Best Practices

### 1. Use Auto-Imports

```vue
<!-- ✅ Good -->
<script setup>
const count = ref(0);
</script>

<!-- ❌ Avoid -->
<script setup>
import { ref } from 'vue';
const count = ref(0);
</script>
```

### 2. Use Composables for Reusable Logic

```typescript
// composables/useAuth.ts
export const useAuth = () => {
  const user = useState('user', () => null);

  const login = async (credentials) => {
    const data = await $fetch('/api/login', {
      method: 'POST',
      body: credentials
    });
    user.value = data.user;
  };

  return { user, login };
};
```

### 3. Lazy Load Components

```vue
<template>
  <div>
    <LazyHeavyComponent v-if="show" />
  </div>
</template>
```

### 4. Use Server Routes for Backend Logic

```typescript
// server/api/users.ts
export default defineEventHandler(async () => {
  // Direct database access
  return await db.user.findMany();
});
```

### 5. Optimize Images

```vue
<template>
  <NuxtImg src="/photo.jpg" width="400" height="300" />
</template>
```

---

## Common Patterns

### Authentication

```typescript
// composables/useAuth.ts
export const useAuth = () => {
  const user = useState<User | null>('user', () => null);
  const isAuthenticated = computed(() => !!user.value);

  const login = async (email: string, password: string) => {
    const data = await $fetch('/api/auth/login', {
      method: 'POST',
      body: { email, password }
    });
    user.value = data.user;
  };

  const logout = async () => {
    await $fetch('/api/auth/logout', { method: 'POST' });
    user.value = null;
    navigateTo('/login');
  };

  return { user, isAuthenticated, login, logout };
};
```

### Form Handling

```vue
<script setup lang="ts">
const form = reactive({
  name: '',
  email: '',
});

const errors = ref<Record<string, string>>({});
const loading = ref(false);

const submit = async () => {
  loading.value = true;
  errors.value = {};

  try {
    await $fetch('/api/users', {
      method: 'POST',
      body: form
    });
    navigateTo('/success');
  } catch (err: any) {
    errors.value = err.data.errors;
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <form @submit.prevent="submit">
    <input v-model="form.name" />
    <span v-if="errors.name">{{ errors.name }}</span>

    <input v-model="form.email" type="email" />
    <span v-if="errors.email">{{ errors.email }}</span>

    <button :disabled="loading">Submit</button>
  </form>
</template>
```

---

## Resources

- **Official Docs:** https://nuxt.com/docs
- **Examples:** https://nuxt.com/docs/examples
- **Modules:** https://nuxt.com/modules
- **Discord:** https://discord.com/invite/ps2h6QT
- **GitHub:** https://github.com/nuxt/nuxt

---

## Troubleshooting

### Module Not Found

```bash
# Clear .nuxt cache
rm -rf .nuxt
npm run dev
```

### Hydration Mismatch

Ensure server and client render the same content. Common causes:
- Using `Date.now()` or random values
- Browser-specific code in server components

### Port Already in Use

```bash
# Change port
PORT=3001 npm run dev
```

This comprehensive skill covers Nuxt 3 with auto-imports, server routes, and modern patterns!
