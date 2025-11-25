---
name: svelte
description: Expert knowledge in Svelte and SvelteKit including reactive declarations, components, stores, routing, server-side rendering, and form actions.
allowed-tools: [Read, Write, Edit, Bash]
---

# Svelte & SvelteKit Skill

Comprehensive knowledge for building modern web applications with Svelte and SvelteKit.

## Quick Start

### Installation

```bash
# Create new SvelteKit app
npm create svelte@latest my-app
cd my-app

# Interactive prompts will ask:
# - Skeleton project or demo app? Skeleton
# - Type checking? Yes, using TypeScript
# - Additional options? ESLint, Prettier, Playwright, Vitest

# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:5173
```

### Project Structure

```
my-app/
├── src/
│   ├── lib/                 # Reusable components and utilities
│   │   ├── components/      # Shared components
│   │   └── server/          # Server-only code
│   ├── routes/              # File-based routing
│   │   ├── +page.svelte     # Home page
│   │   ├── +layout.svelte   # Root layout
│   │   ├── about/
│   │   │   └── +page.svelte # /about page
│   │   └── api/
│   │       └── +server.ts   # API endpoint
│   ├── app.html             # HTML template
│   └── app.css              # Global styles
├── static/                  # Static assets
├── tests/                   # Test files
├── svelte.config.js         # Svelte configuration
├── vite.config.js           # Vite configuration
└── package.json
```

### Basic Component

```svelte
<!-- src/routes/+page.svelte -->
<script lang="ts">
  let count = 0;

  function increment() {
    count += 1;
  }
</script>

<h1>Welcome to SvelteKit</h1>
<p>Count: {count}</p>
<button on:click={increment}>Increment</button>

<style>
  h1 {
    color: purple;
    font-size: 2rem;
  }
</style>
```

---

## Svelte Basics

### 1. Reactive Declarations

```svelte
<script>
  let count = 0;

  // Reactive declaration - recalculates when dependencies change
  $: doubled = count * 2;

  // Reactive statement - runs when dependencies change
  $: {
    console.log(`Count is ${count}`);
    if (count > 10) {
      alert('Count is high!');
    }
  }

  // Multiple reactive declarations
  $: tripled = count * 3;
  $: quadrupled = count * 4;
</script>

<p>Count: {count}</p>
<p>Doubled: {doubled}</p>
<p>Tripled: {tripled}</p>
<button on:click={() => count++}>Increment</button>
```

### 2. Props

```svelte
<!-- Button.svelte -->
<script lang="ts">
  export let label: string;
  export let variant: 'primary' | 'secondary' = 'primary';
  export let disabled = false;
</script>

<button class={variant} {disabled}>
  {label}
</button>

<style>
  .primary { background: blue; color: white; }
  .secondary { background: gray; color: white; }
</style>
```

Usage:

```svelte
<script>
  import Button from './Button.svelte';
</script>

<Button label="Click me" />
<Button label="Secondary" variant="secondary" />
<Button label="Disabled" disabled />
```

### 3. Events

```svelte
<!-- Child.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  function handleClick() {
    dispatch('message', {
      text: 'Hello from child'
    });
  }
</script>

<button on:click={handleClick}>Send Message</button>
```

```svelte
<!-- Parent.svelte -->
<script>
  import Child from './Child.svelte';

  function handleMessage(event) {
    console.log(event.detail.text); // "Hello from child"
  }
</script>

<Child on:message={handleMessage} />
```

### 4. Bindings

```svelte
<script>
  let name = '';
  let checked = false;
  let selected = 'option1';
  let textarea = '';
</script>

<!-- Text input -->
<input bind:value={name} placeholder="Enter name" />
<p>Hello {name}!</p>

<!-- Checkbox -->
<label>
  <input type="checkbox" bind:checked />
  Checked: {checked}
</label>

<!-- Select -->
<select bind:value={selected}>
  <option value="option1">Option 1</option>
  <option value="option2">Option 2</option>
</select>

<!-- Textarea -->
<textarea bind:value={textarea}></textarea>

<!-- Component binding -->
<input bind:this={inputElement} />
```

### 5. Conditionals

```svelte
<script>
  let user = { loggedIn: true, name: 'John' };
  let count = 5;
</script>

{#if user.loggedIn}
  <p>Welcome back, {user.name}!</p>
{:else}
  <p>Please log in</p>
{/if}

{#if count > 10}
  <p>High</p>
{:else if count > 5}
  <p>Medium</p>
{:else}
  <p>Low</p>
{/if}
```

### 6. Loops

```svelte
<script>
  let items = [
    { id: 1, name: 'Apple' },
    { id: 2, name: 'Banana' },
    { id: 3, name: 'Cherry' }
  ];
</script>

<ul>
  {#each items as item (item.id)}
    <li>{item.name}</li>
  {/each}
</ul>

<!-- With index -->
{#each items as item, i}
  <p>{i + 1}. {item.name}</p>
{/each}

<!-- With else -->
{#each items as item}
  <p>{item.name}</p>
{:else}
  <p>No items</p>
{/each}
```

### 7. Await Blocks

```svelte
<script>
  async function fetchData() {
    const res = await fetch('/api/data');
    return res.json();
  }

  let promise = fetchData();
</script>

{#await promise}
  <p>Loading...</p>
{:then data}
  <p>Data: {JSON.stringify(data)}</p>
{:catch error}
  <p>Error: {error.message}</p>
{/await}
```

---

## Stores

### Writable Store

```typescript
// stores.ts
import { writable } from 'svelte/store';

export const count = writable(0);

// With custom logic
function createCounter() {
  const { subscribe, set, update } = writable(0);

  return {
    subscribe,
    increment: () => update(n => n + 1),
    decrement: () => update(n => n - 1),
    reset: () => set(0)
  };
}

export const counter = createCounter();
```

Usage:

```svelte
<script>
  import { count, counter } from './stores';

  // Auto-subscription with $
  $: console.log($count);
</script>

<p>Count: {$count}</p>
<button on:click={() => $count++}>Increment</button>

<p>Counter: {$counter}</p>
<button on:click={counter.increment}>+</button>
<button on:click={counter.decrement}>-</button>
<button on:click={counter.reset}>Reset</button>
```

### Readable Store

```typescript
import { readable } from 'svelte/store';

export const time = readable(new Date(), function start(set) {
  const interval = setInterval(() => {
    set(new Date());
  }, 1000);

  return function stop() {
    clearInterval(interval);
  };
});
```

### Derived Store

```typescript
import { derived } from 'svelte/store';
import { count } from './stores';

export const doubled = derived(count, $count => $count * 2);
export const tripled = derived(count, $count => $count * 3);

// Multiple stores
import { firstName, lastName } from './stores';

export const fullName = derived(
  [firstName, lastName],
  ([$firstName, $lastName]) => `${$firstName} ${$lastName}`
);
```

---

## SvelteKit Routing

### File-Based Routing

```
src/routes/
├── +page.svelte             → /
├── about/
│   └── +page.svelte         → /about
├── blog/
│   ├── +page.svelte         → /blog
│   └── [slug]/
│       └── +page.svelte     → /blog/:slug
└── admin/
    └── [...path]/
        └── +page.svelte     → /admin/* (catch-all)
```

### Dynamic Routes

```svelte
<!-- src/routes/blog/[slug]/+page.svelte -->
<script lang="ts">
  export let data;
</script>

<h1>{data.post.title}</h1>
<div>{@html data.post.content}</div>
```

```typescript
// src/routes/blog/[slug]/+page.ts
export async function load({ params }) {
  const post = await fetch(`/api/posts/${params.slug}`).then(r => r.json());
  return { post };
}
```

### Layouts

```svelte
<!-- src/routes/+layout.svelte -->
<script>
  import '../app.css';
</script>

<header>
  <nav>
    <a href="/">Home</a>
    <a href="/about">About</a>
  </nav>
</header>

<main>
  <slot />
</main>

<footer>
  <p>&copy; 2024</p>
</footer>
```

Nested layout:

```svelte
<!-- src/routes/dashboard/+layout.svelte -->
<div class="dashboard">
  <aside>Sidebar</aside>
  <main>
    <slot />
  </main>
</div>
```

---

## Loading Data

### +page.ts (Universal Load)

Runs on server and client:

```typescript
// src/routes/blog/+page.ts
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
  const response = await fetch('/api/posts');
  const posts = await response.json();

  return { posts };
};
```

### +page.server.ts (Server-Only Load)

Runs only on server:

```typescript
// src/routes/dashboard/+page.server.ts
import type { PageServerLoad } from './$types';
import { db } from '$lib/server/database';

export const load: PageServerLoad = async ({ locals }) => {
  // Direct database access
  const users = await db.user.findMany();

  return { users };
};
```

### Using Loaded Data

```svelte
<!-- src/routes/blog/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types';

  export let data: PageData;
</script>

<h1>Blog Posts</h1>
{#each data.posts as post}
  <article>
    <h2>{post.title}</h2>
    <p>{post.excerpt}</p>
  </article>
{/each}
```

---

## Form Actions

### Basic Form

```svelte
<!-- src/routes/login/+page.svelte -->
<script lang="ts">
  import type { ActionData } from './$types';

  export let form: ActionData;
</script>

<form method="POST">
  <input name="email" type="email" required />
  <input name="password" type="password" required />
  <button>Log in</button>

  {#if form?.error}
    <p class="error">{form.error}</p>
  {/if}
</form>
```

```typescript
// src/routes/login/+page.server.ts
import type { Actions } from './$types';

export const actions: Actions = {
  default: async ({ request, cookies }) => {
    const data = await request.formData();
    const email = data.get('email');
    const password = data.get('password');

    // Authenticate user
    const user = await authenticateUser(email, password);

    if (!user) {
      return { error: 'Invalid credentials' };
    }

    cookies.set('session', user.sessionId, { path: '/' });

    throw redirect(303, '/dashboard');
  }
};
```

### Named Actions

```svelte
<form method="POST" action="?/create">
  <input name="title" required />
  <button>Create</button>
</form>

<form method="POST" action="?/delete">
  <input name="id" type="hidden" value="123" />
  <button>Delete</button>
</form>
```

```typescript
// +page.server.ts
export const actions: Actions = {
  create: async ({ request }) => {
    const data = await request.formData();
    // Create logic
  },

  delete: async ({ request }) => {
    const data = await request.formData();
    // Delete logic
  }
};
```

### Progressive Enhancement

```svelte
<script>
  import { enhance } from '$app/forms';
</script>

<form method="POST" use:enhance>
  <input name="email" />
  <button>Submit</button>
</form>
```

---

## API Routes

```typescript
// src/routes/api/posts/+server.ts
import type { RequestHandler } from './$types';
import { json } from '@sveltejs/kit';

export const GET: RequestHandler = async () => {
  const posts = await db.post.findMany();
  return json(posts);
};

export const POST: RequestHandler = async ({ request }) => {
  const data = await request.json();
  const post = await db.post.create({ data });
  return json(post, { status: 201 });
};
```

```typescript
// src/routes/api/posts/[id]/+server.ts
export const GET: RequestHandler = async ({ params }) => {
  const post = await db.post.findUnique({
    where: { id: params.id }
  });

  if (!post) {
    throw error(404, 'Post not found');
  }

  return json(post);
};

export const DELETE: RequestHandler = async ({ params }) => {
  await db.post.delete({ where: { id: params.id } });
  return new Response(null, { status: 204 });
};
```

---

## Hooks

### Server Hooks

```typescript
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
  // Authentication
  const session = event.cookies.get('session');

  if (session) {
    event.locals.user = await getUserFromSession(session);
  }

  // Custom headers
  const response = await resolve(event);
  response.headers.set('X-Custom-Header', 'value');

  return response;
};
```

### Client Hooks

```typescript
// src/hooks.client.ts
import type { HandleClientError } from '@sveltejs/kit';

export const handleError: HandleClientError = ({ error, event }) => {
  console.error('Client error:', error);

  return {
    message: 'An error occurred'
  };
};
```

---

## Environment Variables

```bash
# .env
DATABASE_URL="postgresql://..."
PUBLIC_API_URL="https://api.example.com"
SECRET_KEY="abc123"
```

```typescript
// Access in code
import { env } from '$env/dynamic/private';
import { PUBLIC_API_URL } from '$env/static/public';

// Private (server-only)
const dbUrl = env.DATABASE_URL;

// Public (client-accessible, prefixed with PUBLIC_)
const apiUrl = PUBLIC_API_URL;
```

---

## TypeScript

### Typed Props

```svelte
<script lang="ts">
  interface User {
    id: number;
    name: string;
    email: string;
  }

  export let user: User;
  export let onDelete: (id: number) => void;
</script>

<div>
  <p>{user.name}</p>
  <button on:click={() => onDelete(user.id)}>Delete</button>
</div>
```

### Generated Types

```svelte
<script lang="ts">
  import type { PageData, ActionData } from './$types';

  export let data: PageData;
  export let form: ActionData;
</script>
```

---

## Styling

### Scoped Styles

```svelte
<style>
  /* Scoped to this component */
  h1 {
    color: purple;
  }

  .card {
    padding: 1rem;
    border: 1px solid #ccc;
  }
</style>
```

### Global Styles

```svelte
<style global>
  /* Global styles */
  body {
    margin: 0;
    font-family: sans-serif;
  }
</style>
```

### CSS Variables

```svelte
<script>
  export let color = 'blue';
</script>

<div style="--color: {color}">
  <p>Styled text</p>
</div>

<style>
  p {
    color: var(--color);
  }
</style>
```

### Tailwind CSS

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

```svelte
<div class="p-4 bg-blue-500 text-white rounded">
  <h1 class="text-2xl font-bold">Hello Tailwind</h1>
</div>
```

---

## Transitions & Animations

```svelte
<script>
  import { fade, fly, slide } from 'svelte/transition';

  let visible = true;
</script>

<button on:click={() => visible = !visible}>Toggle</button>

{#if visible}
  <div transition:fade>Fades in and out</div>
  <div in:fly={{ y: 200 }} out:fade>Custom in/out</div>
  <div transition:slide>Slides in and out</div>
{/if}
```

### Custom Transitions

```svelte
<script>
  function spin(node, { duration }) {
    return {
      duration,
      css: t => `
        transform: rotate(${t * 360}deg);
        opacity: ${t};
      `
    };
  }
</script>

<div transition:spin={{ duration: 500 }}>
  Spinning element
</div>
```

---

## Adapters & Deployment

### Node Adapter

```bash
npm install -D @sveltejs/adapter-node
```

```javascript
// svelte.config.js
import adapter from '@sveltejs/adapter-node';

export default {
  kit: {
    adapter: adapter()
  }
};
```

### Static Adapter (SSG)

```bash
npm install -D @sveltejs/adapter-static
```

```javascript
import adapter from '@sveltejs/adapter-static';

export default {
  kit: {
    adapter: adapter()
  }
};
```

### Vercel Adapter

```bash
npm install -D @sveltejs/adapter-vercel
```

```javascript
import adapter from '@sveltejs/adapter-vercel';

export default {
  kit: {
    adapter: adapter()
  }
};
```

---

## Testing

### Vitest

```bash
npm install -D vitest @testing-library/svelte
```

```typescript
// src/lib/Button.test.ts
import { render, fireEvent } from '@testing-library/svelte';
import Button from './Button.svelte';

describe('Button', () => {
  it('renders with label', () => {
    const { getByText } = render(Button, { label: 'Click me' });
    expect(getByText('Click me')).toBeTruthy();
  });

  it('calls onClick when clicked', async () => {
    const onClick = vi.fn();
    const { getByRole } = render(Button, { label: 'Click', onClick });

    await fireEvent.click(getByRole('button'));
    expect(onClick).toHaveBeenCalled();
  });
});
```

### Playwright (E2E)

```typescript
// tests/home.test.ts
import { expect, test } from '@playwright/test';

test('home page', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('h1')).toHaveText('Welcome to SvelteKit');
});
```

---

## Best Practices

### 1. Use Reactive Declarations

```svelte
<!-- ✅ Good -->
<script>
  let count = 0;
  $: doubled = count * 2;
</script>

<!-- ❌ Avoid -->
<script>
  let count = 0;
  let doubled = 0;

  function updateDoubled() {
    doubled = count * 2;
  }
</script>
```

### 2. Component Composition

```svelte
<!-- ✅ Good: Small, focused components -->
<Card>
  <CardHeader title="My Card" />
  <CardBody>{content}</CardBody>
</Card>

<!-- ❌ Avoid: Monolithic components -->
```

### 3. Use Stores for Global State

```typescript
// ✅ Good: Global state in stores
import { writable } from 'svelte/store';
export const user = writable(null);

// ❌ Avoid: Passing props through many levels
```

### 4. Server-Side Data Loading

```typescript
// ✅ Good: Load data on server
export const load: PageServerLoad = async () => {
  const data = await db.query();
  return { data };
};
```

---

## Common Patterns

### Authentication

```typescript
// src/hooks.server.ts
export const handle: Handle = async ({ event, resolve }) => {
  const session = event.cookies.get('session');

  if (session) {
    event.locals.user = await getUserFromSession(session);
  }

  return resolve(event);
};
```

```typescript
// src/routes/dashboard/+page.server.ts
export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.user) {
    throw redirect(303, '/login');
  }

  return { user: locals.user };
};
```

### Protected Routes

```typescript
// src/routes/admin/+layout.server.ts
export const load: LayoutServerLoad = async ({ locals }) => {
  if (!locals.user?.isAdmin) {
    throw redirect(303, '/');
  }

  return {};
};
```

---

## Resources

- **Official Docs:** https://svelte.dev/docs
- **SvelteKit Docs:** https://kit.svelte.dev/docs
- **Tutorial:** https://learn.svelte.dev
- **REPL:** https://svelte.dev/repl
- **Discord:** https://svelte.dev/chat
- **GitHub:** https://github.com/sveltejs/svelte

---

## Troubleshooting

### Hydration Mismatch

Ensure server and client render the same content. Common causes:
- Using `Date.now()` or random values
- Browser-specific code

### Build Errors

```bash
# Clear build cache
rm -rf .svelte-kit
npm run dev
```

### Type Errors

```bash
# Regenerate types
npm run build
```

This comprehensive skill covers Svelte and SvelteKit with modern patterns and best practices!
