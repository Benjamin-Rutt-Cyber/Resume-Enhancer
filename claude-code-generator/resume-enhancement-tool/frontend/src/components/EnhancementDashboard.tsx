import React, { useState, useEffect, useCallback, useMemo } from 'react';
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
  const [runAnalysis, setRunAnalysis] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [lastPolled, setLastPolled] = useState<Date | null>(null);

  // Check if there are any pending enhancements
  const hasPendingEnhancements = useMemo(() => {
    return enhancements.some(
      (e) => e.status === 'pending' ||
            (e.cover_letter_status && (e.cover_letter_status === 'pending' || e.cover_letter_status === 'in_progress'))
    );
  }, [enhancements]);

  const loadEnhancements = useCallback(async () => {
    try {
      const result = await enhancementApi.listEnhancements();
      setEnhancements(result.enhancements);
      setLastPolled(new Date());
    } catch (err) {
      console.error('Failed to load enhancements:', err);
      // Don't set error state for background polling failures
    }
  }, []);

  useEffect(() => {
    // Initial load
    loadEnhancements();

    // Only poll when there are pending enhancements
    let interval: ReturnType<typeof setInterval> | null = null;

    if (hasPendingEnhancements) {
      // Poll for updates every 5 seconds (increased from 3s)
      interval = setInterval(() => {
        loadEnhancements();
      }, 5000);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [hasPendingEnhancements, loadEnhancements]);

  const handleCreateEnhancement = useCallback(async () => {
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
          setLoading(false);
          return;
        }
        enhancement = await enhancementApi.createTailorEnhancement({
          resume_id: selectedResume,
          job_id: selectedJob,
          enhancement_type: 'job_tailoring',
          run_analysis: runAnalysis,
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
  }, [selectedResume, enhancementType, selectedJob, runAnalysis, selectedIndustry, onEnhancementCreated, loadEnhancements]);

  const handleDeleteEnhancement = useCallback(async (enhancementId: string) => {
    if (!window.confirm('Are you sure you want to delete this enhancement?')) {
      return;
    }

    setDeletingId(enhancementId);
    try {
      await enhancementApi.deleteEnhancement(enhancementId);
      await loadEnhancements();
    } catch (err) {
      console.error('Failed to delete enhancement:', err);
      setError('Failed to delete enhancement. Please try again.');
    } finally {
      setDeletingId(null);
    }
  }, [loadEnhancements]);

  const handleDeleteAllEnhancements = useCallback(async () => {
    if (!window.confirm('Are you sure you want to delete ALL enhancements? This action cannot be undone!')) {
      return;
    }

    setDeletingId('all');
    try {
      await enhancementApi.deleteAllEnhancements();
      await loadEnhancements();
    } catch (err) {
      console.error('Failed to delete all enhancements:', err);
      setError('Failed to delete all enhancements. Please try again.');
    } finally {
      setDeletingId(null);
    }
  }, [loadEnhancements]);

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
            aria-required="true"
            aria-label="Select resume"
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
            aria-required="true"
            aria-label="Select enhancement type"
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

        {enhancementType === 'job_tailoring' && (
          <div style={styles.formGroup}>
            <label style={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={runAnalysis}
                onChange={(e) => setRunAnalysis(e.target.checked)}
                disabled={loading}
                style={styles.checkbox}
              />
              <span>Run ATS keyword analysis and job match scoring</span>
            </label>
            <p style={styles.helpText}>
              Enable this to analyze your resume against the job description and get keyword matching insights and a job match score.
            </p>
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
          aria-busy={loading}
          aria-label="Create enhancement request"
        >
          {loading ? 'Creating...' : 'Create Enhancement'}
        </button>
      </div>

      {/* Enhancements List */}
      <div style={styles.listContainer}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <h3 style={styles.subtitle}>Enhancement Requests</h3>
            <button
              onClick={loadEnhancements}
              style={styles.refreshButton}
              disabled={deletingId !== null}
              aria-label="Refresh enhancements list"
            >
              🔄 Refresh
            </button>
            {lastPolled && (
              <span style={styles.lastPolled}>
                Last updated: {lastPolled.toLocaleTimeString()}
              </span>
            )}
          </div>
          {enhancements.length > 0 && (
            <button
              onClick={handleDeleteAllEnhancements}
              style={styles.deleteAllButton}
              disabled={deletingId !== null}
              onMouseEnter={(e) => {
                if (!e.currentTarget.disabled) {
                  e.currentTarget.style.backgroundColor = '#c62828';
                }
              }}
              onMouseLeave={(e) => {
                if (!e.currentTarget.disabled) {
                  e.currentTarget.style.backgroundColor = '#d32f2f';
                }
              }}
              aria-busy={deletingId === 'all'}
            >
              {deletingId === 'all' ? 'Deleting...' : 'Delete All Enhancements'}
            </button>
          )}
        </div>
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
                onDelete={() => handleDeleteEnhancement(enhancement.id)}
                isDeleting={deletingId === enhancement.id}
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
  onDelete: () => void;
  isDeleting: boolean;
}

const EnhancementCard: React.FC<EnhancementCardProps> = ({
  enhancement,
  resumes,
  jobs,
  onDelete,
  isDeleting,
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

  const handleDownloadDocx = async () => {
    try {
      const blob = await enhancementApi.downloadEnhancementDocx(enhancement.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `enhanced_resume_${enhancement.id}.docx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert('Failed to download DOCX file');
    }
  };

  const handleViewComparison = () => {
    window.open(`/comparison/${enhancement.id}`, '_blank');
  };

  const getScoreColor = (score: number): string => {
    if (score >= 70) return '#4CAF50'; // Green
    if (score >= 50) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  const handleDownloadCoverLetter = async (format: 'md' | 'pdf' | 'docx') => {
    try {
      const blob = await enhancementApi.downloadCoverLetter(enhancement.id, format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `cover_letter_${enhancement.id}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      alert(err.message || 'Failed to download cover letter');
    }
  };

  const getCoverLetterStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return '#4CAF50'; // Green
      case 'failed':
        return '#f44336'; // Red
      case 'in_progress':
        return '#2196F3'; // Blue
      case 'skipped':
        return '#9E9E9E'; // Gray
      default:
        return '#ff9800'; // Orange (pending)
    }
  };

  const getCoverLetterStatusLabel = (status: string) => {
    switch (status) {
      case 'in_progress':
        return 'Generating...';
      case 'completed':
        return 'Ready';
      case 'failed':
        return 'Failed';
      case 'skipped':
        return 'Not Available';
      default:
        return 'Pending';
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span
            style={{
              ...styles.status,
              backgroundColor: getStatusColor(enhancement.status),
            }}
          >
            {enhancement.status}
          </span>
          <button
            onClick={onDelete}
            style={styles.cardDeleteButton}
            disabled={isDeleting}
            onMouseEnter={(e) => {
              if (!e.currentTarget.disabled) {
                e.currentTarget.style.backgroundColor = '#c62828';
              }
            }}
            onMouseLeave={(e) => {
              if (!e.currentTarget.disabled) {
                e.currentTarget.style.backgroundColor = '#d32f2f';
              }
            }}
            title="Delete this enhancement"
            aria-label="Delete enhancement"
            aria-busy={isDeleting}
          >
            {isDeleting ? '...' : '✕'}
          </button>
        </div>
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
        {enhancement.job_match_score !== null && (
          <div style={styles.matchScoreContainer}>
            <strong>Job Match Score: </strong>
            <span
              style={{
                ...styles.matchScoreBadge,
                backgroundColor: getScoreColor(enhancement.job_match_score),
              }}
            >
              {enhancement.job_match_score}%
            </span>
          </div>
        )}
      </div>

      {/* Cover Letter Section - Only for job_tailoring */}
      {enhancement.enhancement_type === 'job_tailoring' && (
        <div style={styles.coverLetterSection}>
          <div style={styles.coverLetterHeader}>
            <strong>Cover Letter:</strong>
            <span
              style={{
                ...styles.status,
                backgroundColor: getCoverLetterStatusColor(enhancement.cover_letter_status),
              }}
            >
              {getCoverLetterStatusLabel(enhancement.cover_letter_status)}
            </span>
          </div>

          {enhancement.cover_letter_status === 'completed' && (
            <div style={styles.coverLetterActions}>
              <button
                onClick={() => handleDownloadCoverLetter('md')}
                style={{ ...styles.actionButton, ...styles.actionButtonSecondary }}
              >
                Download Markdown
              </button>
              <button
                onClick={() => handleDownloadCoverLetter('pdf')}
                style={styles.actionButton}
              >
                Download PDF
              </button>
              <button
                onClick={() => handleDownloadCoverLetter('docx')}
                style={{ ...styles.actionButton, ...styles.actionButtonPrimary }}
              >
                Download DOCX
              </button>
            </div>
          )}

          {enhancement.cover_letter_status === 'in_progress' && (
            <p style={styles.pendingNote}>⏳ Generating cover letter...</p>
          )}

          {enhancement.cover_letter_status === 'pending' &&
            enhancement.status === 'completed' && (
              <p style={styles.pendingNote}>
                ⏳ Will generate after resume completes...
              </p>
            )}

          {enhancement.cover_letter_status === 'failed' &&
            enhancement.cover_letter_error && (
              <p style={styles.errorNote}>
                ❌ {enhancement.cover_letter_error}
              </p>
            )}

          {enhancement.cover_letter_status === 'skipped' && (
            <p style={styles.helpText}>
              Cover letters are only generated for job-specific tailoring, not
              industry revamps.
            </p>
          )}
        </div>
      )}

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
          <button
            onClick={handleDownloadDocx}
            style={{ ...styles.actionButton, ...styles.actionButtonPrimary }}
          >
            Download DOCX
          </button>
          <button
            onClick={handleViewComparison}
            style={{ ...styles.actionButton, ...styles.actionButtonInfo }}
          >
            View Comparison
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
  actionButtonPrimary: {
    backgroundColor: '#2196F3',
  },
  actionButtonInfo: {
    backgroundColor: '#00ACC1',
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '0.5rem',
    fontSize: '1rem',
    color: '#555',
    cursor: 'pointer',
  },
  checkbox: {
    marginTop: '0.25rem',
    cursor: 'pointer',
    width: '18px',
    height: '18px',
  },
  helpText: {
    margin: '0.25rem 0 0 1.75rem',
    fontSize: '0.875rem',
    color: '#888',
    fontStyle: 'italic',
    lineHeight: '1.4',
  },
  matchScoreContainer: {
    marginTop: '0.5rem',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  matchScoreBadge: {
    padding: '0.25rem 0.75rem',
    borderRadius: '12px',
    color: '#fff',
    fontSize: '0.9rem',
    fontWeight: 'bold',
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
  deleteAllButton: {
    padding: '0.5rem 1rem',
    fontSize: '0.875rem',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#d32f2f',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
    transition: 'background-color 0.2s',
  },
  cardDeleteButton: {
    padding: '0.25rem 0.5rem',
    fontSize: '1rem',
    fontWeight: 'bold',
    color: '#fff',
    backgroundColor: '#d32f2f',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    minWidth: '28px',
    minHeight: '28px',
  },
  coverLetterSection: {
    marginTop: '1rem',
    padding: '1rem',
    backgroundColor: '#f5f5f5',
    borderRadius: '4px',
    borderLeft: '3px solid #2196F3',
  },
  coverLetterHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '0.5rem',
  },
  coverLetterActions: {
    marginTop: '0.5rem',
    display: 'flex',
    gap: '0.5rem',
    flexWrap: 'wrap',
  },
  refreshButton: {
    padding: '0.4rem 0.8rem',
    fontSize: '0.875rem',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#2196F3',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
    transition: 'background-color 0.2s',
  },
  lastPolled: {
    fontSize: '0.8rem',
    color: '#888',
    fontStyle: 'italic',
  },
};
