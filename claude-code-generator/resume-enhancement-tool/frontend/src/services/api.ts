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

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
