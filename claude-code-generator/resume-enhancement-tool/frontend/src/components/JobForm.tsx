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
    <div style={styles.container}>
      <h2 style={styles.title}>Add Job Description</h2>
      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.formGroup}>
          <label htmlFor="title" style={styles.label}>
            Job Title <span style={styles.required}>*</span>
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Senior Software Engineer"
            required
            style={styles.input}
            disabled={loading}
          />
        </div>

        <div style={styles.formGroup}>
          <label htmlFor="company" style={styles.label}>
            Company (Optional)
          </label>
          <input
            type="text"
            id="company"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            placeholder="e.g., Tech Corp"
            style={styles.input}
            disabled={loading}
          />
        </div>

        <div style={styles.formGroup}>
          <label htmlFor="description" style={styles.label}>
            Job Description <span style={styles.required}>*</span>
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Paste the full job description here..."
            required
            rows={10}
            style={{ ...styles.input, ...styles.textarea }}
            disabled={loading}
          />
        </div>

        {error && <div style={styles.error}>{error}</div>}

        <button
          type="submit"
          disabled={loading || !title || !description}
          style={{
            ...styles.button,
            ...(loading || !title || !description ? styles.buttonDisabled : {}),
          }}
        >
          {loading ? 'Creating...' : 'Add Job Description'}
        </button>
      </form>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    marginBottom: '2rem',
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    marginBottom: '1rem',
    color: '#333',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  label: {
    fontSize: '1rem',
    fontWeight: '500',
    color: '#555',
  },
  required: {
    color: '#d32f2f',
  },
  input: {
    padding: '0.75rem',
    fontSize: '1rem',
    border: '1px solid #ccc',
    borderRadius: '4px',
    fontFamily: 'inherit',
  },
  textarea: {
    resize: 'vertical',
    minHeight: '200px',
  },
  button: {
    padding: '0.75rem 1.5rem',
    fontSize: '1rem',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#4CAF50',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.3s ease',
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
    cursor: 'not-allowed',
  },
  error: {
    padding: '0.75rem',
    backgroundColor: '#ffebee',
    color: '#c62828',
    borderRadius: '4px',
    border: '1px solid #ef5350',
  },
};
