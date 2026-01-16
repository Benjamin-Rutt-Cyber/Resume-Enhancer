import axios from 'axios';
import type {
  Resume,
  Job,
  Enhancement,
  CreateJobRequest,
  CreateTailorEnhancementRequest,
  CreateRevampEnhancementRequest,
  StylePreviewsResponse,
  StyleSelectionResponse,
  AnalysisResponse,
  AchievementSuggestionsResponse,
  ComparisonData,
} from '../types';

// Construct API base URL with robust handling for missing /api suffix and trailing slashes
const getApiBaseUrl = () => {
  let url = import.meta.env.VITE_API_URL || '/api';
  // Remove trailing slash if present
  if (url.endsWith('/')) {
    url = url.slice(0, -1);
  }
  // Append /api if not already present
  if (!url.endsWith('/api')) {
    url += '/api';
  }
  return url;
};

const API_BASE_URL = getApiBaseUrl();

/**
 * SECURITY: Track if we're currently refreshing the token to prevent race conditions
 */
let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

/**
 * Subscribe to token refresh completion
 */
const subscribeTokenRefresh = (callback: (token: string) => void) => {
  refreshSubscribers.push(callback);
};

/**
 * Notify all subscribers that token has been refreshed
 */
const onTokenRefreshed = (token: string) => {
  refreshSubscribers.forEach(callback => callback(token));
  refreshSubscribers = [];
};

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // SECURITY: Include credentials to send/receive HttpOnly cookies
  withCredentials: true,
});

// Request interceptor - add JWT token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle 401 errors with token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried, try to refresh the token
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Don't retry for auth endpoints (login, signup, refresh)
      if (originalRequest.url?.includes('/auth/')) {
        // Clear auth data and redirect
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/signup')) {
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      // If already refreshing, wait for it to complete
      if (isRefreshing) {
        return new Promise((resolve) => {
          subscribeTokenRefresh((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(api(originalRequest));
          });
        });
      }

      isRefreshing = true;

      try {
        // SECURITY: Refresh token is in HttpOnly cookie, automatically sent
        const response = await api.post('/auth/refresh');
        const { access_token } = response.data;

        // Store new access token
        localStorage.setItem('authToken', access_token);

        // Update authorization header
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        originalRequest.headers.Authorization = `Bearer ${access_token}`;

        // Notify subscribers
        onTokenRefreshed(access_token);
        isRefreshing = false;

        // Retry original request
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed - clear auth and redirect to login
        isRefreshing = false;
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');

        if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/signup')) {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Resume API
export const resumeApi = {
  uploadResume: async (file: File): Promise<Resume> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<Resume>('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  listResumes: async (): Promise<{ resumes: Resume[]; total: number }> => {
    const response = await api.get('/resumes');
    return response.data;
  },

  getResume: async (id: string): Promise<Resume> => {
    const response = await api.get(`/resumes/${id}`);
    return response.data;
  },

  deleteResume: async (id: string): Promise<void> => {
    await api.delete(`/resumes/${id}`);
  },

  deleteAllResumes: async (): Promise<void> => {
    await api.delete('/resumes');
  },
};

// Job API
export const jobApi = {
  createJob: async (job: CreateJobRequest): Promise<Job> => {
    const response = await api.post<Job>('/jobs', job);
    return response.data;
  },

  listJobs: async (): Promise<{ jobs: Job[]; total: number }> => {
    const response = await api.get('/jobs');
    return response.data;
  },

  getJob: async (id: string): Promise<Job> => {
    const response = await api.get(`/jobs/${id}`);
    return response.data;
  },
};

// Enhancement API
export const enhancementApi = {
  createTailorEnhancement: async (
    data: CreateTailorEnhancementRequest
  ): Promise<Enhancement> => {
    const response = await api.post<Enhancement>('/enhancements/tailor', data);
    return response.data;
  },

  createRevampEnhancement: async (
    data: CreateRevampEnhancementRequest
  ): Promise<Enhancement> => {
    const response = await api.post<Enhancement>('/enhancements/revamp', data);
    return response.data;
  },

  listEnhancements: async (): Promise<{
    enhancements: Enhancement[];
    total: number;
  }> => {
    const response = await api.get('/enhancements');
    return response.data;
  },

  getEnhancement: async (id: string): Promise<Enhancement> => {
    const response = await api.get(`/enhancements/${id}`);
    return response.data;
  },

  downloadEnhancement: async (
    id: string,
    format: 'pdf' | 'md' = 'pdf'
  ): Promise<Blob> => {
    const response = await api.get(`/enhancements/${id}/download`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  },

  downloadEnhancementDocx: async (id: string): Promise<Blob> => {
    const response = await api.get(`/enhancements/${id}/download/docx`, {
      responseType: 'blob',
    });
    return response.data;
  },

  finalizeEnhancement: async (id: string): Promise<Enhancement> => {
    const response = await api.post(`/enhancements/${id}/finalize`);
    return response.data;
  },

  deleteEnhancement: async (id: string): Promise<void> => {
    await api.delete(`/enhancements/${id}`);
  },

  deleteAllEnhancements: async (): Promise<void> => {
    await api.delete('/enhancements');
  },

  downloadCoverLetter: async (
    enhancementId: string,
    format: 'md' | 'pdf' | 'docx' = 'md'
  ): Promise<Blob> => {
    const response = await api.get(
      `/enhancements/${enhancementId}/download/cover-letter`,
      {
        params: { format },
        responseType: 'blob',
      }
    );
    return response.data;
  },
};

// Style Preview API
export const styleApi = {
  generateStylePreviews: async (
    resumeId: string
  ): Promise<StylePreviewsResponse> => {
    const response = await api.post<StylePreviewsResponse>(
      `/resumes/${resumeId}/style-previews`
    );
    return response.data;
  },

  getStylePreviews: async (
    resumeId: string
  ): Promise<StylePreviewsResponse> => {
    const response = await api.get<StylePreviewsResponse>(
      `/resumes/${resumeId}/style-previews`
    );
    return response.data;
  },

  selectStyle: async (
    resumeId: string,
    style: string
  ): Promise<StyleSelectionResponse> => {
    const response = await api.post<StyleSelectionResponse>(
      `/resumes/${resumeId}/select-style`,
      { style }
    );
    return response.data;
  },
};

// Analysis API
export const analysisApi = {
  getAnalysis: async (enhancementId: string): Promise<AnalysisResponse> => {
    const response = await api.get<AnalysisResponse>(
      `/enhancements/${enhancementId}/analysis`
    );
    return response.data;
  },

  getAchievementSuggestions: async (
    enhancementId: string
  ): Promise<AchievementSuggestionsResponse> => {
    const response = await api.get<AchievementSuggestionsResponse>(
      `/enhancements/${enhancementId}/achievements`
    );
    return response.data;
  },
};

// Comparison API
export const comparisonApi = {
  getComparison: async (enhancementId: string): Promise<ComparisonData> => {
    const response = await api.get<ComparisonData>(
      `/enhancements/${enhancementId}/comparison`
    );
    return response.data;
  },
};

export default api;
