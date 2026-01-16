import api from './api';
import type { User, AuthResponse, LoginCredentials, SignupCredentials, RefreshResponse } from '../types';

/**
 * Authentication API service
 *
 * SECURITY NOTES:
 * - Access tokens stored in localStorage (short-lived, 30 min)
 * - Refresh tokens stored in HttpOnly cookies (handled by browser)
 * - Token refresh happens automatically via axios interceptor
 * - Logout clears local storage AND calls backend to clear cookie
 */
export const authApi = {
  /**
   * Register a new user account
   * SECURITY: Requires terms acceptance, sets refresh token cookie
   */
  signup: async (credentials: SignupCredentials): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/signup', credentials);
    return response.data;
  },

  /**
   * Login with email and password
   * SECURITY: Sets refresh token in HttpOnly cookie
   */
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  },

  /**
   * Get current authenticated user's information
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Refresh access token using HttpOnly refresh token cookie
   * SECURITY: Refresh token sent automatically via cookie
   */
  refreshToken: async (): Promise<RefreshResponse> => {
    const response = await api.post<RefreshResponse>('/auth/refresh');
    return response.data;
  },

  /**
   * Logout - clears local storage and calls backend to clear cookie
   * @param logoutAll - If true, invalidates all sessions across devices
   */
  logout: async (logoutAll: boolean = false) => {
    try {
      // SECURITY: Call backend to clear HttpOnly cookie and optionally invalidate all tokens
      await api.post('/auth/logout', null, { params: { logout_all: logoutAll } });
    } catch (error) {
      // Even if backend call fails, clear local storage
      console.warn('Logout API call failed, clearing local storage anyway');
    }
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  },

  /**
   * Change password
   * SECURITY: Invalidates all existing tokens, requires re-login
   */
  changePassword: async (currentPassword: string, newPassword: string): Promise<void> => {
    await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    // Clear local auth data - user must re-login
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  },

  /**
   * Get stored auth token from localStorage
   */
  getStoredToken: (): string | null => {
    return localStorage.getItem('authToken');
  },

  /**
   * Get stored user from localStorage
   */
  getStoredUser: (): User | null => {
    const userJson = localStorage.getItem('user');
    if (!userJson) return null;

    try {
      return JSON.parse(userJson);
    } catch {
      return null;
    }
  },

  /**
   * Store auth token and user in localStorage
   * SECURITY: Only access token stored here; refresh token is in HttpOnly cookie
   */
  storeAuthData: (token: string, user: User) => {
    localStorage.setItem('authToken', token);
    localStorage.setItem('user', JSON.stringify(user));
  },

  /**
   * Check if user has admin role
   */
  isAdmin: (): boolean => {
    const user = authApi.getStoredUser();
    return user?.role === 'admin';
  },
};
