import React, { useState } from 'react';
import { jobApi } from '../services/api';
import type { Job } from '../types';

interface JobFormProps {
  onJobCreated: (job: Job) => void;
}

export const JobForm: React.FC<JobFormProps> = ({ onJobCreated }) => {
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const job = await jobApi.createJob({
        title,
        company: company || undefined,
        description_text: description,
        source: 'paste',
      });
      onJobCreated(job);
      // Reset form
      setTitle('');
      setCompany('');
      setDescription('');
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Failed to create job. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <label htmlFor="title" className="form-label">
            Job Title <span className="form-required">*</span>
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Senior Software Engineer"
            required
            className="form-input"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="company" className="form-label">
            Company (Optional)
          </label>
          <input
            type="text"
            id="company"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            placeholder="e.g., Tech Corp"
            className="form-input"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="description" className="form-label">
            Job Description <span className="form-required">*</span>
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Paste the full job description here..."
            required
            rows={10}
            className="form-textarea"
            disabled={loading}
          />
        </div>

        {error && (
          <div className="error-message">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ flexShrink: 0 }}>
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <span>{error}</span>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !title || !description}
          className="btn btn-primary"
          style={{ width: 'fit-content' }}
        >
          {loading ? 'Creating...' : 'Add Job Description'}
        </button>
      </form>
    </div>
  );
};
