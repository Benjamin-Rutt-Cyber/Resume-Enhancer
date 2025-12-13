import React, { useState, useEffect } from 'react';
import { enhancementApi } from '../services/api';
import type { Enhancement, Resume, Job } from '../types';

interface EnhancementDashboardProps {
  resumes: Resume[];
  jobs: Job[];
  onEnhancementCreated: (enhancement: Enhancement) => void;
}

export const EnhancementDashboard: React.FC<EnhancementDashboardProps> = ({
  resumes,
  jobs,
  onEnhancementCreated,
}) => {
  const [enhancements, setEnhancements] = useState<Enhancement[]>([]);
  const [selectedResume, setSelectedResume] = useState('');
  const [enhancementType, setEnhancementType] = useState<
    'job_tailoring' | 'industry_revamp'
  >('job_tailoring');
  const [selectedJob, setSelectedJob] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState('IT');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadEnhancements();

    // Poll for updates every 3 seconds
    const interval = setInterval(() => {
      loadEnhancements();
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const loadEnhancements = async () => {
    try {
      const result = await enhancementApi.listEnhancements();
      setEnhancements(result.enhancements);
    } catch (err) {
      console.error('Failed to load enhancements:', err);
    }
  };

  const handleCreateEnhancement = async () => {
    if (!selectedResume) {
      setError('Please select a resume');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let enhancement: Enhancement;

      if (enhancementType === 'job_tailoring') {
        if (!selectedJob) {
          setError('Please select a job');
          return;
        }
        enhancement = await enhancementApi.createTailorEnhancement({
          resume_id: selectedResume,
          job_id: selectedJob,
          enhancement_type: 'job_tailoring',
        });
      } else {
        enhancement = await enhancementApi.createRevampEnhancement({
          resume_id: selectedResume,
          industry: selectedIndustry,
        });
      }

      onEnhancementCreated(enhancement);
      await loadEnhancements();
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          'Failed to create enhancement. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Create Enhancement</h2>

      {/* Create Enhancement Form */}
      <div style={styles.form}>
        <div style={styles.formGroup}>
          <label htmlFor="resume" style={styles.label}>
            Select Resume <span style={styles.required}>*</span>
          </label>
          <select
            id="resume"
            value={selectedResume}
            onChange={(e) => setSelectedResume(e.target.value)}
            style={styles.select}
            disabled={loading || resumes.length === 0}
          >
            <option value="">
              {resumes.length === 0
                ? 'No resumes uploaded yet'
                : 'Choose a resume...'}
            </option>
            {resumes.map((resume) => (
              <option key={resume.id} value={resume.id}>
                {resume.filename} ({resume.word_count} words)
              </option>
            ))}
          </select>
        </div>

        <div style={styles.formGroup}>
          <label htmlFor="type" style={styles.label}>
            Enhancement Type <span style={styles.required}>*</span>
          </label>
          <select
            id="type"
            value={enhancementType}
            onChange={(e) =>
              setEnhancementType(
                e.target.value as 'job_tailoring' | 'industry_revamp'
              )
            }
            style={styles.select}
            disabled={loading}
          >
            <option value="job_tailoring">Job-Specific Tailoring</option>
            <option value="industry_revamp">Industry Revamp</option>
          </select>
        </div>

        {enhancementType === 'job_tailoring' ? (
          <div style={styles.formGroup}>
            <label htmlFor="job" style={styles.label}>
              Select Job <span style={styles.required}>*</span>
            </label>
            <select
              id="job"
              value={selectedJob}
              onChange={(e) => setSelectedJob(e.target.value)}
              style={styles.select}
              disabled={loading || jobs.length === 0}
            >
              <option value="">
                {jobs.length === 0
                  ? 'No jobs added yet'
                  : 'Choose a job...'}
              </option>
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.title}
                  {job.company ? ` at ${job.company}` : ''}
                </option>
              ))}
            </select>
          </div>
        ) : (
          <div style={styles.formGroup}>
            <label htmlFor="industry" style={styles.label}>
              Target Industry <span style={styles.required}>*</span>
            </label>
            <select
              id="industry"
              value={selectedIndustry}
              onChange={(e) => setSelectedIndustry(e.target.value)}
              style={styles.select}
              disabled={loading}
            >
              <option value="IT">IT / Software Development</option>
              <option value="Cybersecurity">Cybersecurity</option>
              <option value="Finance">Finance</option>
            </select>
          </div>
        )}

        {error && <div style={styles.error}>{error}</div>}

        <button
          onClick={handleCreateEnhancement}
          disabled={loading || !selectedResume}
          style={{
            ...styles.button,
            ...(loading || !selectedResume ? styles.buttonDisabled : {}),
          }}
        >
          {loading ? 'Creating...' : 'Create Enhancement'}
        </button>
      </div>

      {/* Enhancements List */}
      <div style={styles.listContainer}>
        <h3 style={styles.subtitle}>Enhancement Requests</h3>
        {enhancements.length === 0 ? (
          <p style={styles.emptyState}>
            No enhancement requests yet. Create one above to get started!
          </p>
        ) : (
          <div style={styles.list}>
            {enhancements.map((enhancement) => (
              <EnhancementCard
                key={enhancement.id}
                enhancement={enhancement}
                resumes={resumes}
                jobs={jobs}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

interface EnhancementCardProps {
  enhancement: Enhancement;
  resumes: Resume[];
  jobs: Job[];
}

const EnhancementCard: React.FC<EnhancementCardProps> = ({
  enhancement,
  resumes,
  jobs,
}) => {
  const resume = resumes.find((r) => r.id === enhancement.resume_id);
  const job =
    enhancement.job_id && jobs.find((j) => j.id === enhancement.job_id);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return '#4CAF50';
      case 'failed':
        return '#f44336';
      default:
        return '#ff9800';
    }
  };

  const handleDownload = async (format: 'pdf' | 'md') => {
    try {
      const blob = await enhancementApi.downloadEnhancement(
        enhancement.id,
        format
      );
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `enhanced_resume_${enhancement.id}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert('Failed to download file');
    }
  };

  return (
    <div style={styles.card}>
      <div style={styles.cardHeader}>
        <h4 style={styles.cardTitle}>
          {enhancement.enhancement_type === 'job_tailoring'
            ? 'Job Tailoring'
            : 'Industry Revamp'}
        </h4>
        <span
          style={{
            ...styles.status,
            backgroundColor: getStatusColor(enhancement.status),
          }}
        >
          {enhancement.status}
        </span>
      </div>
      <div style={styles.cardBody}>
        <p style={styles.cardText}>
          <strong>Resume:</strong> {resume?.filename || 'Unknown'}
        </p>
        {job && (
          <p style={styles.cardText}>
            <strong>Job:</strong> {job.title}
            {job.company && ` at ${job.company}`}
          </p>
        )}
        {enhancement.industry && (
          <p style={styles.cardText}>
            <strong>Industry:</strong> {enhancement.industry}
          </p>
        )}
        <p style={styles.cardText}>
          <strong>Created:</strong>{' '}
          {new Date(enhancement.created_at).toLocaleString()}
        </p>
      </div>
      {enhancement.status === 'completed' && (
        <div style={styles.cardActions}>
          <button
            onClick={() => handleDownload('md')}
            style={{ ...styles.actionButton, ...styles.actionButtonSecondary }}
          >
            Download Markdown
          </button>
          <button
            onClick={() => handleDownload('pdf')}
            style={styles.actionButton}
          >
            Download PDF
          </button>
        </div>
      )}
      {enhancement.status === 'pending' && (
        <p style={styles.pendingNote}>
          ⏳ Waiting for Claude Code to process...
        </p>
      )}
      {enhancement.status === 'failed' && enhancement.error_message && (
        <p style={styles.errorNote}>❌ {enhancement.error_message}</p>
      )}
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
  subtitle: {
    fontSize: '1.25rem',
    fontWeight: 'bold',
    marginBottom: '1rem',
    color: '#555',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
    padding: '1.5rem',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px',
    marginBottom: '2rem',
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
  select: {
    padding: '0.75rem',
    fontSize: '1rem',
    border: '1px solid #ccc',
    borderRadius: '4px',
    backgroundColor: '#fff',
  },
  button: {
    padding: '0.75rem 1.5rem',
    fontSize: '1rem',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#2196F3',
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
  listContainer: {
    marginTop: '2rem',
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  emptyState: {
    padding: '2rem',
    textAlign: 'center',
    color: '#888',
    backgroundColor: '#f5f5f5',
    borderRadius: '8px',
  },
  card: {
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    padding: '1.5rem',
    backgroundColor: '#fff',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem',
  },
  cardTitle: {
    fontSize: '1.1rem',
    fontWeight: 'bold',
    margin: 0,
    color: '#333',
  },
  status: {
    padding: '0.25rem 0.75rem',
    borderRadius: '12px',
    color: '#fff',
    fontSize: '0.875rem',
    fontWeight: '500',
    textTransform: 'capitalize',
  },
  cardBody: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  cardText: {
    margin: 0,
    color: '#666',
    fontSize: '0.95rem',
  },
  cardActions: {
    marginTop: '1rem',
    display: 'flex',
    gap: '0.5rem',
  },
  actionButton: {
    padding: '0.5rem 1rem',
    fontSize: '0.9rem',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#4CAF50',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  actionButtonSecondary: {
    backgroundColor: '#757575',
  },
  pendingNote: {
    marginTop: '0.5rem',
    color: '#ff9800',
    fontSize: '0.9rem',
    fontStyle: 'italic',
  },
  errorNote: {
    marginTop: '0.5rem',
    color: '#f44336',
    fontSize: '0.9rem',
  },
};
