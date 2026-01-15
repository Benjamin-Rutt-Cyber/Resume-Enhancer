import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { User, LoginCredentials, SignupCredentials } from '../types';
import { authApi } from '../services/authApi';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  signup: (credentials: SignupCredentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // On mount, check for existing token and restore session
  useEffect(() => {
    const restoreSession = async () => {
      const token = authApi.getStoredToken();
      const storedUser = authApi.getStoredUser();

      if (token && storedUser) {
        // Verify token is still valid by fetching current user
        try {
          const currentUser = await authApi.getCurrentUser();
          setUser(currentUser);
          // Update stored user in case of any changes
          authApi.storeAuthData(token, currentUser);
        } catch (error) {
          // Token is invalid, clear stored data
          authApi.logout();
          setUser(null);
        }
      }

      setIsLoading(false);
    };

    restoreSession();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    const { access_token, user } = await authApi.login(credentials);
    authApi.storeAuthData(access_token, user);
    setUser(user);
  };

  const signup = async (credentials: SignupCredentials) => {
    const { access_token, user } = await authApi.signup(credentials);
    authApi.storeAuthData(access_token, user);
    setUser(user);
  };

  const logout = () => {
    authApi.logout();
    setUser(null);
    // Redirect to login page
    window.location.href = '/login';
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    signup,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
