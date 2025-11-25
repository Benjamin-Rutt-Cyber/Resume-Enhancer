# Mobile Application

A cross-platform mobile application built with React Native, delivering native performance with a single codebase for iOS and Android.

## Overview

This mobile app provides a complete solution with:
- Cross-platform support (iOS & Android)
- Native performance and feel
- Backend API integration
- Offline support with local storage
- Push notifications
- User authentication
- Modern UI/UX design

## Tech Stack

### Mobile Framework
- React Native with TypeScript
- React Navigation for routing
- Native modules integration
- Platform-specific code when needed

### State Management
- Context API / Redux / MobX
- Async storage for persistence
- API state management

### Backend Integration
- RESTful API client
- JWT authentication
- Real-time updates (optional)
- File uploads
- Error handling and retry logic

### Native Features
- Camera and photo library
- Location services
- Push notifications
- Biometric authentication
- Device information

### Development Tools
- Expo (optional, for faster development)
- React Native CLI
- TypeScript for type safety
- ESLint and Prettier

## Features

- User authentication (email/password, social login)
- Profile management
- Real-time data synchronization
- Offline support
- Push notifications
- Image capture and upload
- Location services
- In-app navigation
- Form validation
- Error handling
- Loading states
- Pull-to-refresh
- Infinite scroll / pagination

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- iOS Development:
  - macOS
  - Xcode 14+
  - CocoaPods
- Android Development:
  - Android Studio
  - Android SDK
  - Java JDK 11+

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **iOS Setup** (macOS only)
   ```bash
   cd ios
   pod install
   cd ..
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API URL and keys
   ```

### Running the App

#### iOS Simulator
```bash
# Start Metro bundler
npm start

# In another terminal
npm run ios
# or for specific device
npm run ios -- --simulator="iPhone 14 Pro"
```

#### Android Emulator
```bash
# Start Metro bundler
npm start

# In another terminal
npm run android
```

#### Physical Device

**iOS:**
1. Open `ios/<AppName>.xcworkspace` in Xcode
2. Select your device
3. Click Run

**Android:**
1. Enable USB debugging on your device
2. Connect via USB
3. Run `npm run android`

### Development with Expo (if using)

```bash
# Start Expo
npm start

# Scan QR code with:
# - Expo Go app (iOS/Android)
# - Camera app (iOS)
```

## Project Structure

```
.
├── src/
│   ├── components/          # Reusable components
│   │   ├── common/         # Common UI components
│   │   ├── forms/          # Form components
│   │   └── navigation/     # Navigation components
│   │
│   ├── screens/            # Screen components
│   │   ├── auth/          # Authentication screens
│   │   ├── home/          # Home screen
│   │   ├── profile/       # Profile screen
│   │   └── settings/      # Settings screen
│   │
│   ├── navigation/         # Navigation configuration
│   │   ├── AppNavigator.tsx
│   │   ├── AuthNavigator.tsx
│   │   └── types.ts
│   │
│   ├── services/          # API and services
│   │   ├── api.ts        # API client
│   │   ├── auth.ts       # Authentication service
│   │   └── storage.ts    # Local storage service
│   │
│   ├── store/            # State management
│   │   ├── slices/      # Redux slices
│   │   ├── context/     # Context providers
│   │   └── index.ts     # Store configuration
│   │
│   ├── hooks/           # Custom React hooks
│   ├── utils/           # Helper functions
│   ├── constants/       # App constants
│   ├── types/          # TypeScript types
│   ├── assets/         # Images, fonts, etc.
│   └── App.tsx         # App entry point
│
├── ios/                # iOS native code
├── android/            # Android native code
├── __tests__/         # Test files
├── .env.example       # Environment template
├── app.json          # App configuration
├── package.json      # Dependencies
└── README.md        # This file
```

## Configuration

### Environment Variables

Create a `.env` file:

```bash
# API Configuration
API_URL=https://api.your-app.com
API_TIMEOUT=30000

# Authentication
AUTH_DOMAIN=your-app.auth0.com

# Push Notifications
FCM_KEY=your-fcm-key
APNS_KEY=your-apns-key

# Analytics (optional)
ANALYTICS_ID=your-analytics-id

# Feature Flags
ENABLE_PUSH_NOTIFICATIONS=true
ENABLE_BIOMETRICS=true
```

### App Configuration

Edit `app.json` or `app.config.js`:

```json
{
  "expo": {
    "name": "Your App Name",
    "slug": "your-app",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "ios": {
      "bundleIdentifier": "com.yourcompany.yourapp",
      "buildNumber": "1"
    },
    "android": {
      "package": "com.yourcompany.yourapp",
      "versionCode": 1
    }
  }
}
```

## Features Implementation

### Authentication

```typescript
// Login example
import { useAuth } from './hooks/useAuth';

function LoginScreen() {
  const { login, loading, error } = useAuth();

  const handleLogin = async () => {
    try {
      await login(email, password);
      // Navigate to home
    } catch (err) {
      // Handle error
    }
  };

  return (
    // UI implementation
  );
}
```

### API Integration

```typescript
// API service example
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const api = axios.create({
  baseURL: process.env.API_URL,
  timeout: 30000,
});

// Add auth token to requests
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### Push Notifications

```typescript
// Push notification setup
import messaging from '@react-native-firebase/messaging';

async function requestUserPermission() {
  const authStatus = await messaging().requestPermission();
  const enabled =
    authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
    authStatus === messaging.AuthorizationStatus.PROVISIONAL;

  if (enabled) {
    const token = await messaging().getToken();
    // Send token to backend
  }
}
```

### Offline Support

```typescript
// Offline storage example
import AsyncStorage from '@react-native-async-storage/async-storage';

async function cacheData(key: string, data: any) {
  try {
    await AsyncStorage.setItem(key, JSON.stringify(data));
  } catch (error) {
    console.error('Cache error:', error);
  }
}

async function getCachedData(key: string) {
  try {
    const data = await AsyncStorage.getItem(key);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error('Cache retrieval error:', error);
    return null;
  }
}
```

## Testing

### Unit Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

### Component Testing

```typescript
// Example component test
import { render, fireEvent } from '@testing-library/react-native';
import LoginButton from './LoginButton';

test('calls onPress when pressed', () => {
  const onPress = jest.fn();
  const { getByText } = render(<LoginButton onPress={onPress} />);

  fireEvent.press(getByText('Login'));
  expect(onPress).toHaveBeenCalled();
});
```

### E2E Testing (Detox)

```bash
# Build for testing
detox build --configuration ios.sim.debug

# Run E2E tests
detox test --configuration ios.sim.debug
```

## Building for Production

### iOS

1. **Update version and build number**
   ```bash
   # Edit ios/<AppName>/Info.plist
   CFBundleShortVersionString: 1.0.0
   CFBundleVersion: 1
   ```

2. **Build in Xcode**
   - Open `ios/<AppName>.xcworkspace`
   - Select "Any iOS Device" or your connected device
   - Product > Archive
   - Follow App Store upload process

3. **Or build via command line**
   ```bash
   cd ios
   xcodebuild -workspace <AppName>.xcworkspace \
     -scheme <AppName> \
     -configuration Release \
     -archivePath <AppName>.xcarchive \
     archive
   ```

### Android

1. **Generate keystore** (first time only)
   ```bash
   keytool -genkey -v -keystore my-app.keystore \
     -alias my-app-alias -keyalg RSA \
     -keysize 2048 -validity 10000
   ```

2. **Configure signing** in `android/app/build.gradle`:
   ```gradle
   signingConfigs {
     release {
       storeFile file('my-app.keystore')
       storePassword 'password'
       keyAlias 'my-app-alias'
       keyPassword 'password'
     }
   }
   ```

3. **Build APK/AAB**
   ```bash
   cd android

   # Build APK
   ./gradlew assembleRelease

   # Build AAB (for Play Store)
   ./gradlew bundleRelease
   ```

4. **Output location**
   - APK: `android/app/build/outputs/apk/release/app-release.apk`
   - AAB: `android/app/build/outputs/bundle/release/app-release.aab`

## Publishing

### iOS App Store

1. Create app in App Store Connect
2. Upload build via Xcode or Transporter
3. Fill in app information
4. Submit for review

### Google Play Store

1. Create app in Play Console
2. Upload AAB file
3. Fill in app information
4. Submit for review

## Performance Optimization

- Use `React.memo` for component optimization
- Implement virtualization for long lists (FlatList)
- Lazy load screens and components
- Optimize images (use WebP format)
- Use Hermes JavaScript engine
- Profile with React DevTools and Flipper
- Minimize bridge calls between JS and native code

## Debugging

### React Native Debugger
```bash
# Install
brew install --cask react-native-debugger

# Or download from GitHub releases
```

### Flipper
- Built-in with React Native 0.62+
- Network inspection
- Layout inspector
- Crash reporter
- Performance monitoring

### Console Logs
```bash
# iOS
npx react-native log-ios

# Android
npx react-native log-android
```

## Common Issues

### Metro Bundler Issues
```bash
# Clear cache
npm start -- --reset-cache

# Clear watchman
watchman watch-del-all

# Clear node modules
rm -rf node_modules && npm install
```

### iOS Build Issues
```bash
# Clear derived data
rm -rf ~/Library/Developer/Xcode/DerivedData

# Reinstall pods
cd ios && rm -rf Pods && pod install
```

### Android Build Issues
```bash
# Clean gradle
cd android && ./gradlew clean

# Clear gradle cache
rm -rf ~/.gradle/caches/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Ensure all tests pass
6. Submit a pull request

## License

[Your License Here]

## Support

- Documentation: [Your docs URL]
- Issues: [GitHub Issues]
- Email: mobile-support@your-company.com

---

**Built with Claude Code Generator** - Modern mobile development, simplified.
