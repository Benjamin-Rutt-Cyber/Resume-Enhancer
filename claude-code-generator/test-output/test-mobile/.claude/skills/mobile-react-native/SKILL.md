---
name: mobile-react-native
description: Expert knowledge in React Native mobile development including Expo, TypeScript, navigation, state management, native modules, and deployment to iOS and Android.
allowed-tools: [Read, Write, Edit, Bash]
---

# React Native Skill

Comprehensive guide for building cross-platform mobile applications with React Native and TypeScript.

## Quick Start

### Expo Setup (Recommended for beginners)

```bash
# Install Expo CLI
npm install -g expo-cli

# Create new project
npx create-expo-app my-app --template expo-template-blank-typescript
cd my-app

# Start development server
npx expo start

# Install dependencies
npm install @react-navigation/native @react-navigation/native-stack
npm install react-native-safe-area-context react-native-screens
```

### Bare React Native Setup

```bash
# Create new project
npx react-native@latest init MyApp --template react-native-template-typescript
cd MyApp

# iOS
cd ios && pod install && cd ..
npx react-native run-ios

# Android
npx react-native run-android
```

### Project Structure

```
my-app/
├── src/
│   ├── components/
│   │   ├── Button.tsx
│   │   └── Card.tsx
│   ├── screens/
│   │   ├── HomeScreen.tsx
│   │   └── ProfileScreen.tsx
│   ├── navigation/
│   │   └── AppNavigator.tsx
│   ├── services/
│   │   └── api.ts
│   ├── store/
│   │   └── userStore.ts
│   ├── types/
│   │   └── index.ts
│   └── utils/
│       └── helpers.ts
├── App.tsx
└── package.json
```

---

## Core Components

### View and Text

```typescript
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface Props {
  title: string;
  description?: string;
}

const Card: React.FC<Props> = ({ title, description }) => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{title}</Text>
      {description && (
        <Text style={styles.description}>{description}</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 8,
    marginVertical: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    color: '#666',
  },
});

export default Card;
```

### Button and TouchableOpacity

```typescript
import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
} from 'react-native';

interface Props {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
  loading?: boolean;
  style?: ViewStyle;
}

const Button: React.FC<Props> = ({
  title,
  onPress,
  variant = 'primary',
  disabled = false,
  loading = false,
  style,
}) => {
  return (
    <TouchableOpacity
      style={[
        styles.button,
        variant === 'primary' ? styles.primary : styles.secondary,
        disabled && styles.disabled,
        style,
      ]}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.7}
    >
      {loading ? (
        <ActivityIndicator color="#fff" />
      ) : (
        <Text style={styles.text}>{title}</Text>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primary: {
    backgroundColor: '#007AFF',
  },
  secondary: {
    backgroundColor: '#6c757d',
  },
  disabled: {
    opacity: 0.5,
  },
  text: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default Button;
```

### Image and ScrollView

```typescript
import React from 'react';
import { ScrollView, Image, StyleSheet, View } from 'react-native';

interface Props {
  images: string[];
}

const ImageGallery: React.FC<Props> = ({ images }) => {
  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.container}
    >
      {images.map((uri, index) => (
        <View key={index} style={styles.imageContainer}>
          <Image
            source={{ uri }}
            style={styles.image}
            resizeMode="cover"
          />
        </View>
      ))}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
  },
  imageContainer: {
    marginRight: 12,
  },
  image: {
    width: 200,
    height: 150,
    borderRadius: 8,
  },
});

export default ImageGallery;
```

### FlatList

```typescript
import React from 'react';
import {
  FlatList,
  View,
  Text,
  StyleSheet,
  RefreshControl,
} from 'react-native';

interface User {
  id: number;
  name: string;
  email: string;
}

interface Props {
  users: User[];
  onRefresh: () => void;
  refreshing: boolean;
  onEndReached: () => void;
}

const UserList: React.FC<Props> = ({
  users,
  onRefresh,
  refreshing,
  onEndReached,
}) => {
  const renderItem = ({ item }: { item: User }) => (
    <View style={styles.item}>
      <Text style={styles.name}>{item.name}</Text>
      <Text style={styles.email}>{item.email}</Text>
    </View>
  );

  const renderEmpty = () => (
    <View style={styles.empty}>
      <Text>No users found</Text>
    </View>
  );

  return (
    <FlatList
      data={users}
      renderItem={renderItem}
      keyExtractor={(item) => item.id.toString()}
      ListEmptyComponent={renderEmpty}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
      onEndReached={onEndReached}
      onEndReachedThreshold={0.5}
      contentContainerStyle={styles.container}
    />
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  item: {
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 8,
    marginBottom: 12,
  },
  name: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  email: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  empty: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 32,
  },
});

export default UserList;
```

---

## Navigation

### React Navigation Setup

```bash
npm install @react-navigation/native @react-navigation/native-stack
npm install react-native-screens react-native-safe-area-context
```

```typescript
// navigation/AppNavigator.tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import HomeScreen from '../screens/HomeScreen';
import ProfileScreen from '../screens/ProfileScreen';
import DetailsScreen from '../screens/DetailsScreen';

export type RootStackParamList = {
  Home: undefined;
  Profile: { userId: number };
  Details: { itemId: number; title: string };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

const AppNavigator: React.FC = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerStyle: {
            backgroundColor: '#007AFF',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{ title: 'Home' }}
        />
        <Stack.Screen
          name="Profile"
          component={ProfileScreen}
          options={{ title: 'Profile' }}
        />
        <Stack.Screen
          name="Details"
          component={DetailsScreen}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
```

### Using Navigation

```typescript
import React from 'react';
import { View, Text, Button } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';

type Props = NativeStackScreenProps<RootStackParamList, 'Home'>;

const HomeScreen: React.FC<Props> = ({ navigation }) => {
  const handleNavigate = () => {
    navigation.navigate('Profile', { userId: 123 });
  };

  const handleDetails = () => {
    navigation.navigate('Details', {
      itemId: 456,
      title: 'Item Details',
    });
  };

  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Text>Home Screen</Text>
      <Button title="Go to Profile" onPress={handleNavigate} />
      <Button title="Go to Details" onPress={handleDetails} />
    </View>
  );
};

export default HomeScreen;
```

### Bottom Tab Navigation

```bash
npm install @react-navigation/bottom-tabs
```

```typescript
import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import HomeScreen from '../screens/HomeScreen';
import ProfileScreen from '../screens/ProfileScreen';
import SettingsScreen from '../screens/SettingsScreen';

const Tab = createBottomTabNavigator();

const TabNavigator: React.FC = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap = 'home';

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          } else if (route.name === 'Settings') {
            iconName = focused ? 'settings' : 'settings-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
};

export default TabNavigator;
```

---

## Styling

### Responsive Design

```typescript
import { StyleSheet, Dimensions, Platform } from 'react-native';

const { width, height } = Dimensions.get('window');

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: width * 0.05, // 5% of screen width
  },
  card: {
    width: width - 32,
    height: height * 0.3,
  },
  // Platform-specific styles
  shadow: {
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
      },
      android: {
        elevation: 3,
      },
    }),
  },
});
```

### Flexbox Layouts

```typescript
const styles = StyleSheet.create({
  // Center content
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  // Row layout
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  // Column layout
  column: {
    flexDirection: 'column',
    flex: 1,
  },
  // Space between items
  spaceBetween: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
});
```

---

## State Management

### Context API

```typescript
// contexts/AuthContext.tsx
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface User {
  id: number;
  name: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    // API call
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();
    setUser(data.user);
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

// Usage
import { useAuth } from '../contexts/AuthContext';

const LoginScreen = () => {
  const { login, isAuthenticated } = useAuth();

  const handleLogin = async () => {
    await login('user@example.com', 'password');
  };

  return (
    // ...
  );
};
```

---

## AsyncStorage

```bash
npm install @react-native-async-storage/async-storage
```

```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';

// Store data
const storeData = async (key: string, value: any) => {
  try {
    await AsyncStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error('Error storing data:', error);
  }
};

// Retrieve data
const getData = async (key: string) => {
  try {
    const value = await AsyncStorage.getItem(key);
    return value ? JSON.parse(value) : null;
  } catch (error) {
    console.error('Error retrieving data:', error);
    return null;
  }
};

// Remove data
const removeData = async (key: string) => {
  try {
    await AsyncStorage.removeItem(key);
  } catch (error) {
    console.error('Error removing data:', error);
  }
};

// Clear all data
const clearAll = async () => {
  try {
    await AsyncStorage.clear();
  } catch (error) {
    console.error('Error clearing data:', error);
  }
};

// Usage
const saveUser = async (user: User) => {
  await storeData('user', user);
};

const loadUser = async () => {
  const user = await getData('user');
  setUser(user);
};
```

---

## API Integration

```typescript
// services/api.ts
const API_URL = 'https://api.example.com';

export const api = {
  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_URL}${endpoint}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  async put<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    return response.json();
  },

  async delete<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'DELETE',
    });

    return response.json();
  },
};

// Usage
import { useState, useEffect } from 'react';
import { api } from '../services/api';

const UsersScreen = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const data = await api.get<User[]>('/users');
      setUsers(data);
    } catch (error) {
      console.error('Error loading users:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    // ...
  );
};
```

---

## Forms and Input

```typescript
import React, { useState } from 'react';
import {
  View,
  TextInput,
  Text,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import Button from '../components/Button';

interface FormData {
  email: string;
  password: string;
}

const LoginScreen: React.FC = () => {
  const [form, setForm] = useState<FormData>({
    email: '',
    password: '',
  });

  const [errors, setErrors] = useState<Partial<FormData>>({});
  const [loading, setLoading] = useState(false);

  const validate = (): boolean => {
    const newErrors: Partial<FormData> = {};

    if (!form.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(form.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!form.password) {
      newErrors.password = 'Password is required';
    } else if (form.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    setLoading(true);
    try {
      // API call
      await api.post('/login', form);
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <View style={styles.form}>
        <TextInput
          style={[styles.input, errors.email && styles.inputError]}
          placeholder="Email"
          value={form.email}
          onChangeText={(email) => setForm({ ...form, email })}
          keyboardType="email-address"
          autoCapitalize="none"
          autoCorrect={false}
        />
        {errors.email && <Text style={styles.error}>{errors.email}</Text>}

        <TextInput
          style={[styles.input, errors.password && styles.inputError]}
          placeholder="Password"
          value={form.password}
          onChangeText={(password) => setForm({ ...form, password })}
          secureTextEntry
          autoCapitalize="none"
        />
        {errors.password && <Text style={styles.error}>{errors.password}</Text>}

        <Button
          title="Login"
          onPress={handleSubmit}
          loading={loading}
          style={styles.button}
        />
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
  },
  form: {
    padding: 20,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    fontSize: 16,
  },
  inputError: {
    borderColor: 'red',
  },
  error: {
    color: 'red',
    fontSize: 12,
    marginBottom: 12,
  },
  button: {
    marginTop: 16,
  },
});

export default LoginScreen;
```

---

## Platform-Specific Code

```typescript
import { Platform, StyleSheet } from 'react-native';

// Platform checks
if (Platform.OS === 'ios') {
  // iOS-specific code
}

if (Platform.OS === 'android') {
  // Android-specific code
}

// Platform.select
const styles = StyleSheet.create({
  container: {
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
      },
      android: {
        elevation: 3,
      },
      default: {
        // Other platforms
      },
    }),
  },
});

// Separate files
// MyComponent.ios.tsx
// MyComponent.android.tsx
import MyComponent from './MyComponent'; // Automatically picks correct file
```

---

## Testing

```typescript
// __tests__/UserCard.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import UserCard from '../components/UserCard';

describe('UserCard', () => {
  const mockUser = {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
  };

  it('renders user name', () => {
    const { getByText } = render(<UserCard user={mockUser} />);
    expect(getByText('John Doe')).toBeTruthy();
  });

  it('calls onPress when pressed', () => {
    const onPress = jest.fn();
    const { getByText } = render(
      <UserCard user={mockUser} onPress={onPress} />
    );

    fireEvent.press(getByText('John Doe'));
    expect(onPress).toHaveBeenCalledWith(mockUser);
  });
});
```

---

## Deployment

### Expo Build

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Configure build
eas build:configure

# Build for iOS
eas build --platform ios

# Build for Android
eas build --platform android

# Build for both
eas build --platform all

# Submit to stores
eas submit --platform ios
eas submit --platform android
```

### Bare React Native

```bash
# iOS
cd ios
pod install
cd ..

# Build iOS
npx react-native run-ios --configuration Release

# Android
cd android
./gradlew assembleRelease

# APK location: android/app/build/outputs/apk/release/
```

---

## Best Practices

1. **Use TypeScript** for type safety
2. **Optimize FlatList** with `getItemLayout`, `removeClippedSubviews`
3. **Use React.memo** for expensive components
4. **Lazy load images** with libraries like `react-native-fast-image`
5. **Handle keyboard properly** with `KeyboardAvoidingView`
6. **Use SafeAreaView** for notch devices
7. **Implement error boundaries** for crash handling
8. **Cache network requests** to improve performance
9. **Test on real devices** not just simulators
10. **Follow platform design guidelines** (iOS Human Interface, Material Design)

---

## Resources

- React Native Documentation: https://reactnative.dev/
- Expo Documentation: https://docs.expo.dev/
- React Navigation: https://reactnavigation.org/
- React Native Directory: https://reactnative.directory/
- Awesome React Native: https://github.com/jondot/awesome-react-native
