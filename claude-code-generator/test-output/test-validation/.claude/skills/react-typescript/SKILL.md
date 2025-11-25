---
name: react-typescript
description: Expert knowledge in React with TypeScript including components, hooks, state management, routing, and modern React patterns.
allowed-tools: [Read, Write, Edit, Bash]
---

# React TypeScript Skill

Comprehensive knowledge for building modern React applications with TypeScript.

## Quick Start

### Installation

```bash
# Create React App with TypeScript
npx create-react-app my-app --template typescript
cd my-app

# Or use Vite (faster, modern)
npm create vite@latest my-app -- --template react-ts
cd my-app
npm install

# Start development server
npm start  # CRA
npm run dev  # Vite
```

### Basic Component

```typescript
// App.tsx
import React from 'react';

function App() {
  return (
    <div className="App">
      <h1>Hello React + TypeScript</h1>
    </div>
  );
}

export default App;
```

---

## Core Concepts

### 1. Functional Components with TypeScript

```typescript
import React, { FC, ReactNode } from 'react';

// Simple component
const Greeting: FC = () => {
  return <h1>Hello!</h1>;
};

// Component with props (interface)
interface UserProps {
  name: string;
  age?: number;  // Optional
  isActive: boolean;
}

const UserCard: FC<UserProps> = ({ name, age, isActive }) => {
  return (
    <div className="user-card">
      <h2>{name}</h2>
      {age && <p>Age: {age}</p>}
      <p>Status: {isActive ? 'Active' : 'Inactive'}</p>
    </div>
  );
};

// Component with children
interface ContainerProps {
  children: ReactNode;
  className?: string;
}

const Container: FC<ContainerProps> = ({ children, className = '' }) => {
  return <div className={`container ${className}`}>{children}</div>;
};

// Component with event handlers
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
}

const Button: FC<ButtonProps> = ({
  label,
  onClick,
  variant = 'primary',
  disabled = false
}) => {
  return (
    <button
      className={`btn btn-${variant}`}
      onClick={onClick}
      disabled={disabled}
    >
      {label}
    </button>
  );
};
```

### 2. Hooks with TypeScript

#### useState
```typescript
import { useState } from 'react';

// Primitive state
const Counter: FC = () => {
  const [count, setCount] = useState<number>(0);
  const [name, setName] = useState<string>('');

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
    </div>
  );
};

// Object state
interface User {
  id: number;
  name: string;
  email: string;
}

const UserProfile: FC = () => {
  const [user, setUser] = useState<User | null>(null);

  const updateUser = (updates: Partial<User>) => {
    setUser(prev => prev ? { ...prev, ...updates } : null);
  };

  return (
    <div>
      {user && (
        <>
          <p>{user.name}</p>
          <p>{user.email}</p>
        </>
      )}
    </div>
  );
};

// Array state
const TodoList: FC = () => {
  const [todos, setTodos] = useState<string[]>([]);

  const addTodo = (todo: string) => {
    setTodos(prev => [...prev, todo]);
  };

  const removeTodo = (index: number) => {
    setTodos(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <ul>
      {todos.map((todo, index) => (
        <li key={index}>
          {todo}
          <button onClick={() => removeTodo(index)}>Remove</button>
        </li>
      ))}
    </ul>
  );
};
```

#### useEffect
```typescript
import { useEffect } from 'react';

const DataFetcher: FC<{ userId: number }> = ({ userId }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Fetch data on mount and when userId changes
  useEffect(() => {
    let isMounted = true;

    const fetchUser = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/users/${userId}`);
        const data = await response.json();
        if (isMounted) {
          setUser(data);
        }
      } catch (error) {
        console.error('Error fetching user:', error);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchUser();

    // Cleanup function
    return () => {
      isMounted = false;
    };
  }, [userId]);

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>User not found</div>;

  return <div>{user.name}</div>;
};

// Event listener effect
const WindowSize: FC = () => {
  const [size, setSize] = useState({ width: window.innerWidth, height: window.innerHeight });

  useEffect(() => {
    const handleResize = () => {
      setSize({ width: window.innerWidth, height: window.innerHeight });
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return <div>{size.width} x {size.height}</div>;
};
```

#### useContext
```typescript
import { createContext, useContext, FC, ReactNode } from 'react';

// Define context type
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

// Create context
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Provider component
const ThemeProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Custom hook to use context
const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

// Using the context
const ThemedButton: FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      className={`btn-${theme}`}
      onClick={toggleTheme}
    >
      Toggle Theme (Current: {theme})
    </button>
  );
};
```

#### Custom Hooks
```typescript
// Custom fetch hook
function useFetch<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(url);
        const json = await response.json();
        setData(json);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url]);

  return { data, loading, error };
}

// Usage
const UsersList: FC = () => {
  const { data: users, loading, error } = useFetch<User[]>('/api/users');

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {users?.map(user => <li key={user.id}>{user.name}</li>)}
    </ul>
  );
};

// Custom form hook
function useForm<T extends Record<string, any>>(initialValues: T) {
  const [values, setValues] = useState<T>(initialValues);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setValues(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const resetForm = () => {
    setValues(initialValues);
  };

  return { values, handleChange, resetForm };
}

// Usage
const LoginForm: FC = () => {
  const { values, handleChange, resetForm } = useForm({
    email: '',
    password: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Login:', values);
    resetForm();
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        name="email"
        value={values.email}
        onChange={handleChange}
      />
      <input
        type="password"
        name="password"
        value={values.password}
        onChange={handleChange}
      />
      <button type="submit">Login</button>
    </form>
  );
};
```

### 3. React Router

```typescript
import { BrowserRouter, Routes, Route, Link, useParams, useNavigate } from 'react-router-dom';

// Define route types
interface RouteParams {
  userId: string;
}

// App with routes
const App: FC = () => {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
        <Link to="/users">Users</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/users" element={<Users />} />
        <Route path="/users/:userId" element={<UserDetail />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
};

// Component with route params
const UserDetail: FC = () => {
  const { userId } = useParams<RouteParams>();
  const navigate = useNavigate();

  const goBack = () => {
    navigate('/users');
  };

  return (
    <div>
      <h1>User {userId}</h1>
      <button onClick={goBack}>Back to Users</button>
    </div>
  );
};

// Programmatic navigation
const LoginPage: FC = () => {
  const navigate = useNavigate();

  const handleLogin = async () => {
    // Login logic...
    navigate('/dashboard');  // Redirect after login
  };

  return <button onClick={handleLogin}>Login</button>;
};
```

### 4. State Management (Context API)

```typescript
// Global app state with Context
interface AppState {
  user: User | null;
  isAuthenticated: boolean;
}

interface AppContextType extends AppState {
  login: (user: User) => void;
  logout: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

const AppProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AppState>({
    user: null,
    isAuthenticated: false
  });

  const login = (user: User) => {
    setState({ user, isAuthenticated: true });
  };

  const logout = () => {
    setState({ user: null, isAuthenticated: false });
  };

  return (
    <AppContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AppContext.Provider>
  );
};

const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};
```

### 5. Forms and Validation

```typescript
import { useState, FormEvent, ChangeEvent } from 'react';

interface FormData {
  username: string;
  email: string;
  password: string;
}

interface FormErrors {
  username?: string;
  email?: string;
  password?: string;
}

const RegistrationForm: FC = () => {
  const [formData, setFormData] = useState<FormData>({
    username: '',
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsSubmitting(true);
    try {
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        console.log('Registration successful');
        // Reset form
        setFormData({ username: '', email: '', password: '' });
      }
    } catch (error) {
      console.error('Registration error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="username">Username</label>
        <input
          type="text"
          id="username"
          name="username"
          value={formData.username}
          onChange={handleChange}
        />
        {errors.username && <span className="error">{errors.username}</span>}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
        />
        {errors.email && <span className="error">{errors.email}</span>}
      </div>

      <div>
        <label htmlFor="password">Password</label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
        />
        {errors.password && <span className="error">{errors.password}</span>}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Registering...' : 'Register'}
      </button>
    </form>
  );
};
```

---

## Common Patterns

### Conditional Rendering
```typescript
const UserStatus: FC<{ user: User | null }> = ({ user }) => {
  // If-else
  if (!user) {
    return <div>Please log in</div>;
  }

  // Ternary
  return (
    <div>
      {user.isActive ? (
        <span>Active</span>
      ) : (
        <span>Inactive</span>
      )}
    </div>
  );
};

// Logical AND
const Notification: FC<{ message?: string }> = ({ message }) => {
  return (
    <div>
      {message && <div className="notification">{message}</div>}
    </div>
  );
};
```

### List Rendering
```typescript
interface Todo {
  id: number;
  text: string;
  completed: boolean;
}

const TodoList: FC<{ todos: Todo[] }> = ({ todos }) => {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id} className={todo.completed ? 'completed' : ''}>
          {todo.text}
        </li>
      ))}
    </ul>
  );
};
```

### Error Boundaries
```typescript
import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div>
          <h1>Something went wrong</h1>
          <p>{this.state.error?.message}</p>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

---

## Best Practices

1. **Use TypeScript strictly** - Enable strict mode in tsconfig.json
2. **Functional components** - Prefer function components over class components
3. **Component composition** - Break down into smaller, reusable components
4. **Props interface** - Always define prop types with interfaces
5. **Avoid inline functions** - Use useCallback for event handlers
6. **Memoization** - Use React.memo, useMemo, useCallback when needed
7. **Key prop** - Always provide unique keys for list items
8. **State location** - Keep state as low as possible in component tree
9. **Custom hooks** - Extract reusable logic into custom hooks
10. **Error handling** - Use Error Boundaries for component errors

---

## Testing

```typescript
// Component.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Counter from './Counter';

describe('Counter Component', () => {
  it('renders counter with initial value', () => {
    render(<Counter initialCount={0} />);
    expect(screen.getByText(/count: 0/i)).toBeInTheDocument();
  });

  it('increments counter on button click', () => {
    render(<Counter initialCount={0} />);
    const button = screen.getByRole('button', { name: /increment/i });

    fireEvent.click(button);
    expect(screen.getByText(/count: 1/i)).toBeInTheDocument();
  });

  it('calls onCountChange callback', () => {
    const handleCountChange = jest.fn();
    render(<Counter initialCount={0} onCountChange={handleCountChange} />);

    const button = screen.getByRole('button', { name: /increment/i });
    fireEvent.click(button);

    expect(handleCountChange).toHaveBeenCalledWith(1);
  });
});
```

---

## Project Structure

```
my-react-app/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   └── Input.tsx
│   │   └── features/
│   │       └── UserCard.tsx
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── About.tsx
│   │   └── Users.tsx
│   ├── hooks/
│   │   ├── useFetch.ts
│   │   └── useForm.ts
│   ├── context/
│   │   ├── ThemeContext.tsx
│   │   └── AuthContext.tsx
│   ├── types/
│   │   └── index.ts
│   ├── utils/
│   │   └── helpers.ts
│   ├── App.tsx
│   ├── index.tsx
│   └── index.css
├── package.json
└── tsconfig.json
```

---

## Troubleshooting

**Type errors with event handlers:**
```typescript
// Use React.MouseEvent, React.ChangeEvent, etc.
const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
  e.preventDefault();
};
```

**Context undefined error:**
- Ensure component is wrapped in Provider
- Use custom hook that checks for undefined

**State not updating:**
- Don't mutate state directly
- Use functional updates for state based on previous state

---

## Resources

- React Documentation: https://react.dev/
- TypeScript Documentation: https://www.typescriptlang.org/docs/
- React TypeScript Cheatsheet: https://react-typescript-cheatsheet.netlify.app/
- Testing Library: https://testing-library.com/react
