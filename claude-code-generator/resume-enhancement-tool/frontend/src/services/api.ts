import axios from 'axios';
import type {
  Resume,
  Job,
  Enhancement,
  CreateJobRequest,
  CreateTailorEnhancementRequest,
  CreateRevampEnhancementRequest,
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

  finalizeEnhancement: async (id: string): Promise<Enhancement> => {
    const response = await api.post(`/enhancements/${id}/finalize`);
    return response.data;
  },
};

export default api;
