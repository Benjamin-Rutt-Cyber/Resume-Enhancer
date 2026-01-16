import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { User, LoginCredentials, SignupCredentials } from '../types';
import { authApi } from '../services/authApi';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isAdmin: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  signup: (credentials: SignupCredentials) => Promise<void>;
  logout: (logoutAll?: boolean) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
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
          // Token is invalid, try to refresh
          try {
            const refreshResponse = await authApi.refreshToken();
            authApi.storeAuthData(refreshResponse.access_token, storedUser);
            // Verify the new token works
            const currentUser = await authApi.getCurrentUser();
            setUser(currentUser);
            authApi.storeAuthData(refreshResponse.access_token, currentUser);
          } catch (refreshError) {
            // Refresh also failed, clear stored data
            await authApi.logout();
            setUser(null);
          }
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

  /**
   * Logout from current session or all sessions
   * @param logoutAll - If true, invalidates all sessions across devices
   */
  const logout = async (logoutAll: boolean = false) => {
    await authApi.logout(logoutAll);
    setUser(null);
    // Redirect to login page
    window.location.href = '/login';
  };

  /**
   * Change password - requires re-login after
   */
  const changePassword = async (currentPassword: string, newPassword: string) => {
    await authApi.changePassword(currentPassword, newPassword);
    setUser(null);
    // Redirect to login page
    window.location.href = '/login';
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    isAdmin: user?.role === 'admin',
    login,
    signup,
    logout,
    changePassword,
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
