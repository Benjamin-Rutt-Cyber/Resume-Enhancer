import api from './api';
import type { User, AuthResponse, LoginCredentials, SignupCredentials } from '../types';

/**
 * Authentication API service
 * Handles user authentication, registration, and token management
 */
export const authApi = {
  /**
   * Register a new user account
   */
  signup: async (credentials: SignupCredentials): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/signup', credentials);
    return response.data;
  },

  /**
   * Login with email and password
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
   * Logout (clear local token)
   */
  logout: () => {
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
   */
  storeAuthData: (token: string, user: User) => {
    localStorage.setItem('authToken', token);
    localStorage.setItem('user', JSON.stringify(user));
  },
};
