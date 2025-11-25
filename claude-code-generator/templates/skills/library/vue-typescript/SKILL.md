---
name: vue-typescript
description: Expert knowledge in Vue 3 with TypeScript including Composition API, script setup syntax, Pinia state management, Vue Router, and testing with Vitest.
allowed-tools: [Read, Write, Edit, Bash]
---

# Vue 3 TypeScript Skill

Comprehensive guide for building modern web applications with Vue 3 and TypeScript.

## Quick Start

### Project Setup

```bash
# Create new Vue project with Vite
npm create vue@latest

# Select options:
# - TypeScript: Yes
# - JSX: No (or Yes if needed)
# - Vue Router: Yes
# - Pinia: Yes
# - Vitest: Yes
# - ESLint: Yes
# - Prettier: Yes

cd my-vue-app
npm install
npm run dev
```

### Manual Setup

```bash
# Create Vite project
npm create vite@latest my-vue-app -- --template vue-ts
cd my-vue-app
npm install

# Install additional dependencies
npm install vue-router@4 pinia
npm install -D @vitejs/plugin-vue @vue/test-utils vitest jsdom
```

### Basic Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000
  }
})
```

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

## Composition API

### Script Setup Syntax

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Props
interface Props {
  title: string
  count?: number
  isActive?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  count: 0,
  isActive: false
})

// Emits
interface Emits {
  (e: 'update', value: number): void
  (e: 'delete', id: string): void
}

const emit = defineEmits<Emits>()

// Reactive state
const counter = ref(0)
const user = ref({
  name: 'John',
  email: 'john@example.com'
})

// Computed
const doubleCount = computed(() => counter.value * 2)

// Methods
const increment = () => {
  counter.value++
  emit('update', counter.value)
}

// Lifecycle
onMounted(() => {
  console.log('Component mounted')
})
</script>

<template>
  <div class="container">
    <h1>{{ props.title }}</h1>
    <p>Count: {{ counter }}</p>
    <p>Double: {{ doubleCount }}</p>
    <button @click="increment">Increment</button>
  </div>
</template>

<style scoped>
.container {
  padding: 20px;
}
</style>
```

### Ref vs Reactive

```typescript
import { ref, reactive, toRefs } from 'vue'

// ref - for primitives and single values
const count = ref(0)
const name = ref('John')
const user = ref({ name: 'John', age: 30 })

// Access with .value
count.value++
console.log(name.value)
user.value.name = 'Jane'

// reactive - for objects
const state = reactive({
  count: 0,
  name: 'John',
  user: {
    name: 'John',
    age: 30
  }
})

// Direct access
state.count++
console.log(state.name)
state.user.name = 'Jane'

// toRefs - convert reactive object to refs
const { count: countRef, name: nameRef } = toRefs(state)

// ✅ GOOD - Use ref for primitives
const isLoading = ref(false)
const userId = ref<number | null>(null)

// ✅ GOOD - Use reactive for complex objects
const form = reactive({
  email: '',
  password: '',
  rememberMe: false
})
```

### Component with TypeScript

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

interface User {
  id: number
  name: string
  email: string
  role: 'admin' | 'user'
}

interface Props {
  user: User
  editable?: boolean
}

interface Emits {
  (e: 'update:user', user: User): void
  (e: 'delete'): void
}

const props = withDefaults(defineProps<Props>(), {
  editable: false
})

const emit = defineEmits<Emits>()

const isEditing = ref(false)
const editForm = ref<User>({ ...props.user })

const displayName = computed(() => {
  return `${props.user.name} (${props.user.role})`
})

const toggleEdit = () => {
  isEditing.value = !isEditing.value
  editForm.value = { ...props.user }
}

const saveUser = () => {
  emit('update:user', editForm.value)
  isEditing.value = false
}

const deleteUser = () => {
  if (confirm('Are you sure?')) {
    emit('delete')
  }
}
</script>

<template>
  <div class="user-card">
    <div v-if="!isEditing">
      <h2>{{ displayName }}</h2>
      <p>{{ user.email }}</p>
      <button v-if="editable" @click="toggleEdit">Edit</button>
      <button @click="deleteUser">Delete</button>
    </div>

    <form v-else @submit.prevent="saveUser">
      <input v-model="editForm.name" type="text" required />
      <input v-model="editForm.email" type="email" required />
      <select v-model="editForm.role">
        <option value="user">User</option>
        <option value="admin">Admin</option>
      </select>
      <button type="submit">Save</button>
      <button type="button" @click="toggleEdit">Cancel</button>
    </form>
  </div>
</template>
```

---

## Composables

### useCounter Composable

```typescript
// composables/useCounter.ts
import { ref, computed } from 'vue'

export function useCounter(initialValue = 0) {
  const count = ref(initialValue)

  const doubleCount = computed(() => count.value * 2)

  const increment = () => count.value++
  const decrement = () => count.value--
  const reset = () => count.value = initialValue

  return {
    count,
    doubleCount,
    increment,
    decrement,
    reset
  }
}

// Usage in component
import { useCounter } from '@/composables/useCounter'

const { count, doubleCount, increment } = useCounter(10)
```

### useFetch Composable

```typescript
// composables/useFetch.ts
import { ref, isRef, unref, watchEffect, type Ref } from 'vue'

interface UseFetchOptions {
  immediate?: boolean
  refetch?: Ref<boolean>
}

export function useFetch<T>(url: string | Ref<string>, options: UseFetchOptions = {}) {
  const { immediate = true } = options

  const data = ref<T | null>(null)
  const error = ref<Error | null>(null)
  const isLoading = ref(false)

  const fetchData = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch(unref(url))

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      data.value = await response.json()
    } catch (e) {
      error.value = e as Error
    } finally {
      isLoading.value = false
    }
  }

  if (immediate) {
    fetchData()
  }

  // Refetch when URL changes
  if (isRef(url)) {
    watchEffect(() => {
      fetchData()
    })
  }

  return {
    data,
    error,
    isLoading,
    refetch: fetchData
  }
}

// Usage
interface User {
  id: number
  name: string
}

const userId = ref(1)
const url = computed(() => `/api/users/${userId.value}`)

const { data, error, isLoading, refetch } = useFetch<User>(url)
```

### useLocalStorage Composable

```typescript
// composables/useLocalStorage.ts
import { ref, watch } from 'vue'

export function useLocalStorage<T>(key: string, defaultValue: T) {
  const storedValue = localStorage.getItem(key)
  const value = ref<T>(storedValue ? JSON.parse(storedValue) : defaultValue)

  watch(value, (newValue) => {
    localStorage.setItem(key, JSON.stringify(newValue))
  }, { deep: true })

  return value
}

// Usage
const theme = useLocalStorage<'light' | 'dark'>('theme', 'light')
const user = useLocalStorage<User | null>('user', null)
```

---

## Vue Router

### Router Setup

```typescript
// router/index.ts
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('@/views/AboutView.vue')
  },
  {
    path: '/users',
    name: 'users',
    component: () => import('@/views/UsersView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/users/:id',
    name: 'user-detail',
    component: () => import('@/views/UserDetailView.vue'),
    props: true
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('token')

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
```

### Using Router in Components

```vue
<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Route params
const userId = computed(() => route.params.id as string)

// Query params
const page = computed(() => route.query.page as string)

// Navigate programmatically
const goToUser = (id: number) => {
  router.push({ name: 'user-detail', params: { id } })
}

const goBack = () => {
  router.back()
}
</script>

<template>
  <div>
    <h1>Current Route: {{ route.name }}</h1>
    <router-link to="/">Home</router-link>
    <router-link :to="{ name: 'about' }">About</router-link>
    <router-link :to="{ name: 'user-detail', params: { id: 1 } }">
      User 1
    </router-link>

    <button @click="goToUser(2)">Go to User 2</button>
    <button @click="goBack">Go Back</button>

    <router-view />
  </div>
</template>
```

---

## Pinia State Management

### Store Definition

```typescript
// stores/userStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface User {
  id: number
  name: string
  email: string
  role: 'admin' | 'user'
}

export const useUserStore = defineStore('user', () => {
  // State
  const users = ref<User[]>([])
  const currentUser = ref<User | null>(null)
  const isLoading = ref(false)

  // Getters
  const adminUsers = computed(() =>
    users.value.filter(user => user.role === 'admin')
  )

  const isAdmin = computed(() =>
    currentUser.value?.role === 'admin'
  )

  // Actions
  const fetchUsers = async () => {
    isLoading.value = true
    try {
      const response = await fetch('/api/users')
      users.value = await response.json()
    } catch (error) {
      console.error('Failed to fetch users:', error)
    } finally {
      isLoading.value = false
    }
  }

  const addUser = async (user: Omit<User, 'id'>) => {
    const response = await fetch('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(user)
    })
    const newUser = await response.json()
    users.value.push(newUser)
  }

  const updateUser = async (id: number, updates: Partial<User>) => {
    const response = await fetch(`/api/users/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    })
    const updatedUser = await response.json()
    const index = users.value.findIndex(u => u.id === id)
    if (index !== -1) {
      users.value[index] = updatedUser
    }
  }

  const deleteUser = async (id: number) => {
    await fetch(`/api/users/${id}`, { method: 'DELETE' })
    users.value = users.value.filter(u => u.id !== id)
  }

  const login = async (email: string, password: string) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })
    currentUser.value = await response.json()
  }

  const logout = () => {
    currentUser.value = null
  }

  return {
    // State
    users,
    currentUser,
    isLoading,
    // Getters
    adminUsers,
    isAdmin,
    // Actions
    fetchUsers,
    addUser,
    updateUser,
    deleteUser,
    login,
    logout
  }
})
```

### Using Store in Components

```vue
<script setup lang="ts">
import { useUserStore } from '@/stores/userStore'
import { storeToRefs } from 'pinia'

const userStore = useUserStore()

// Use storeToRefs to preserve reactivity
const { users, currentUser, isLoading, adminUsers } = storeToRefs(userStore)

// Actions can be destructured directly
const { fetchUsers, addUser, deleteUser } = userStore

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div>
    <div v-if="isLoading">Loading...</div>

    <div v-else>
      <h2>All Users ({{ users.length }})</h2>
      <ul>
        <li v-for="user in users" :key="user.id">
          {{ user.name }} - {{ user.email }}
          <button @click="deleteUser(user.id)">Delete</button>
        </li>
      </ul>

      <h2>Admin Users ({{ adminUsers.length }})</h2>
      <ul>
        <li v-for="user in adminUsers" :key="user.id">
          {{ user.name }}
        </li>
      </ul>
    </div>
  </div>
</template>
```

---

## Forms and Validation

### Basic Form

```vue
<script setup lang="ts">
import { reactive, ref } from 'vue'

interface LoginForm {
  email: string
  password: string
  rememberMe: boolean
}

const form = reactive<LoginForm>({
  email: '',
  password: '',
  rememberMe: false
})

const errors = reactive({
  email: '',
  password: ''
})

const isSubmitting = ref(false)

const validateEmail = (email: string): boolean => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

const validate = (): boolean => {
  let isValid = true

  if (!form.email) {
    errors.email = 'Email is required'
    isValid = false
  } else if (!validateEmail(form.email)) {
    errors.email = 'Invalid email format'
    isValid = false
  } else {
    errors.email = ''
  }

  if (!form.password) {
    errors.password = 'Password is required'
    isValid = false
  } else if (form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
    isValid = false
  } else {
    errors.password = ''
  }

  return isValid
}

const handleSubmit = async () => {
  if (!validate()) return

  isSubmitting.value = true

  try {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })

    if (!response.ok) {
      throw new Error('Login failed')
    }

    const data = await response.json()
    console.log('Login successful:', data)
  } catch (error) {
    console.error('Login error:', error)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleSubmit">
    <div>
      <label for="email">Email</label>
      <input
        id="email"
        v-model="form.email"
        type="email"
        @blur="validate"
      />
      <span v-if="errors.email" class="error">{{ errors.email }}</span>
    </div>

    <div>
      <label for="password">Password</label>
      <input
        id="password"
        v-model="form.password"
        type="password"
        @blur="validate"
      />
      <span v-if="errors.password" class="error">{{ errors.password }}</span>
    </div>

    <div>
      <label>
        <input v-model="form.rememberMe" type="checkbox" />
        Remember me
      </label>
    </div>

    <button type="submit" :disabled="isSubmitting">
      {{ isSubmitting ? 'Logging in...' : 'Login' }}
    </button>
  </form>
</template>
```

### Vuelidate Integration

```bash
npm install @vuelidate/core @vuelidate/validators
```

```vue
<script setup lang="ts">
import { reactive } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { required, email, minLength } from '@vuelidate/validators'

const form = reactive({
  email: '',
  password: '',
  confirmPassword: ''
})

const rules = {
  email: { required, email },
  password: { required, minLength: minLength(8) },
  confirmPassword: {
    required,
    sameAs: (value: string) => value === form.password
  }
}

const v$ = useVuelidate(rules, form)

const handleSubmit = async () => {
  const isValid = await v$.value.$validate()

  if (!isValid) return

  // Submit form
  console.log('Form is valid:', form)
}
</script>

<template>
  <form @submit.prevent="handleSubmit">
    <div>
      <input v-model="form.email" type="email" />
      <span v-for="error of v$.email.$errors" :key="error.$uid" class="error">
        {{ error.$message }}
      </span>
    </div>

    <div>
      <input v-model="form.password" type="password" />
      <span v-for="error of v$.password.$errors" :key="error.$uid" class="error">
        {{ error.$message }}
      </span>
    </div>

    <button type="submit">Submit</button>
  </form>
</template>
```

---

## Template Refs

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Element ref
const inputRef = ref<HTMLInputElement | null>(null)

// Component ref
const childRef = ref<InstanceType<typeof ChildComponent> | null>(null)

onMounted(() => {
  // Access DOM element
  inputRef.value?.focus()

  // Call child component method
  childRef.value?.someMethod()
})

const focusInput = () => {
  inputRef.value?.focus()
}
</script>

<template>
  <div>
    <input ref="inputRef" type="text" />
    <button @click="focusInput">Focus Input</button>

    <ChildComponent ref="childRef" />
  </div>
</template>
```

---

## Testing with Vitest

### Component Test

```typescript
// UserCard.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import UserCard from '@/components/UserCard.vue'

describe('UserCard', () => {
  it('renders user name', () => {
    const wrapper = mount(UserCard, {
      props: {
        user: {
          id: 1,
          name: 'John Doe',
          email: 'john@example.com',
          role: 'user'
        }
      }
    })

    expect(wrapper.text()).toContain('John Doe')
  })

  it('emits delete event when delete button clicked', async () => {
    const wrapper = mount(UserCard, {
      props: {
        user: {
          id: 1,
          name: 'John Doe',
          email: 'john@example.com',
          role: 'user'
        }
      }
    })

    await wrapper.find('button').trigger('click')

    expect(wrapper.emitted('delete')).toBeTruthy()
  })

  it('shows edit form when editable', async () => {
    const wrapper = mount(UserCard, {
      props: {
        user: {
          id: 1,
          name: 'John Doe',
          email: 'john@example.com',
          role: 'user'
        },
        editable: true
      }
    })

    expect(wrapper.find('button').text()).toBe('Edit')

    await wrapper.find('button').trigger('click')

    expect(wrapper.find('form').exists()).toBe(true)
  })
})
```

### Composable Test

```typescript
// useCounter.spec.ts
import { describe, it, expect } from 'vitest'
import { useCounter } from '@/composables/useCounter'

describe('useCounter', () => {
  it('initializes with default value', () => {
    const { count } = useCounter()
    expect(count.value).toBe(0)
  })

  it('initializes with custom value', () => {
    const { count } = useCounter(10)
    expect(count.value).toBe(10)
  })

  it('increments count', () => {
    const { count, increment } = useCounter()
    increment()
    expect(count.value).toBe(1)
  })

  it('computes double count', () => {
    const { count, doubleCount, increment } = useCounter(5)
    expect(doubleCount.value).toBe(10)
    increment()
    expect(doubleCount.value).toBe(12)
  })
})
```

---

## Best Practices

### 1. Use Script Setup

```vue
<!-- ✅ GOOD -->
<script setup lang="ts">
import { ref } from 'vue'

const count = ref(0)
</script>

<!-- ❌ BAD -->
<script lang="ts">
import { defineComponent, ref } from 'vue'

export default defineComponent({
  setup() {
    const count = ref(0)
    return { count }
  }
})
</script>
```

### 2. Type Props and Emits

```typescript
// ✅ GOOD
interface Props {
  title: string
  count?: number
}

const props = defineProps<Props>()

// ❌ BAD
const props = defineProps(['title', 'count'])
```

### 3. Use Composables for Reusable Logic

```typescript
// ✅ GOOD - Extract to composable
// composables/useAuth.ts
export function useAuth() {
  const user = ref(null)
  const login = async () => { /* ... */ }
  return { user, login }
}

// ❌ BAD - Duplicate logic in every component
```

### 4. Proper Reactive References

```typescript
// ✅ GOOD
const count = ref(0)
const increment = () => count.value++

// ❌ BAD
let count = 0
const increment = () => count++
```

---

## Resources

- Vue 3 Documentation: https://vuejs.org/
- Pinia Documentation: https://pinia.vuejs.org/
- Vue Router: https://router.vuejs.org/
- Vite: https://vitejs.dev/
- Vitest: https://vitest.dev/
- Vue Test Utils: https://test-utils.vuejs.org/
