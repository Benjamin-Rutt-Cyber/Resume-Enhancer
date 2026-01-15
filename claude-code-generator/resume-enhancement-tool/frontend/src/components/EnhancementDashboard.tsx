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
    <div className="dashboard-container">
      <h2 className="dashboard-title">Create Enhancement</h2>

      {/* Create Enhancement Form */}
      <div className="dashboard-form">
        <div className="form-group">
          <label htmlFor="resume" className="form-label">
            Select Resume <span className="form-required">*</span>
          </label>
          <select
            id="resume"
            value={selectedResume}
            onChange={(e) => setSelectedResume(e.target.value)}
            className="dashboard-select"
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

        <div className="form-group">
          <label htmlFor="type" className="form-label">
            Enhancement Type <span className="form-required">*</span>
          </label>
          <select
            id="type"
            value={enhancementType}
            onChange={(e) =>
              setEnhancementType(
                e.target.value as 'job_tailoring' | 'industry_revamp'
              )
            }
            className="dashboard-select"
            disabled={loading}
            aria-required="true"
            aria-label="Select enhancement type"
          >
            <option value="job_tailoring">Job-Specific Tailoring</option>
            <option value="industry_revamp">Industry Revamp</option>
          </select>
        </div>

        {enhancementType === 'job_tailoring' ? (
          <div className="form-group">
            <label htmlFor="job" className="form-label">
              Select Job <span className="form-required">*</span>
            </label>
            <select
              id="job"
              value={selectedJob}
              onChange={(e) => setSelectedJob(e.target.value)}
              className="dashboard-select"
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
          <div className="form-group">
            <label htmlFor="industry" className="form-label">
              Target Industry <span className="form-required">*</span>
            </label>
            <select
              id="industry"
              value={selectedIndustry}
              onChange={(e) => setSelectedIndustry(e.target.value)}
              className="dashboard-select"
              disabled={loading}
            >
              <option value="IT">IT / Software Development</option>
              <option value="Cybersecurity">Cybersecurity</option>
              <option value="Finance">Finance</option>
            </select>
          </div>
        )}

        {enhancementType === 'job_tailoring' && (
          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={runAnalysis}
                onChange={(e) => setRunAnalysis(e.target.checked)}
                disabled={loading}
                className="dashboard-checkbox"
              />
              <span>Run ATS keyword analysis and job match scoring</span>
            </label>
            <p className="help-text">
              Enable this to analyze your resume against the job description and get keyword matching insights and a job match score.
            </p>
          </div>
        )}

        {error && <div className="error-note">❌ {error}</div>}

        <button
          onClick={handleCreateEnhancement}
          disabled={loading || !selectedResume}
          className="btn btn-primary"
          style={{ width: 'fit-content' }}
          aria-busy={loading}
          aria-label="Create enhancement request"
        >
          {loading ? 'Creating...' : 'Create Enhancement'}
        </button>
      </div>

      {/* Enhancements List */}
      <div className="enhancement-list">
        <div className="list-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <h3 className="dashboard-subtitle" style={{ margin: 0 }}>Enhancement Requests</h3>
            <button
              onClick={loadEnhancements}
              className="refresh-btn"
              disabled={deletingId !== null}
              aria-label="Refresh enhancements list"
            >
              🔄 Refresh
            </button>
            {lastPolled && (
              <span className="lastPolled">
                Last updated: {lastPolled.toLocaleTimeString()}
              </span>
            )}
          </div>
          {enhancements.length > 0 && (
            <button
              onClick={handleDeleteAllEnhancements}
              className="btn bg-danger"
              disabled={deletingId !== null}
              aria-busy={deletingId === 'all'}
            >
              {deletingId === 'all' ? 'Deleting...' : 'Delete All Enhancements'}
            </button>
          )}
        </div>
        {enhancements.length === 0 ? (
          <p className="empty-state-card">
            No enhancement requests yet. Create one above to get started!
          </p>
        ) : (
          <div className="list">
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

  const getStatusClass = (status: string) => {
    switch (status) {
      case 'completed': return 'status-completed';
      case 'failed': return 'status-failed';
      case 'in_progress': return 'status-in-progress';
      default: return 'status-pending';
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

  const getCoverLetterStatusClass = (status: string) => {
    switch (status) {
      case 'completed': return 'status-completed';
      case 'failed': return 'status-failed';
      case 'in_progress': return 'status-in-progress';
      case 'skipped': return 'status-skipped';
      default: return 'status-pending';
    }
  };

  const getCoverLetterStatusLabel = (status: string) => {
    switch (status) {
      case 'in_progress': return 'Generating...';
      case 'completed': return 'Ready';
      case 'failed': return 'Failed';
      case 'skipped': return 'Not Available';
      default: return 'Pending';
    }
  };

  return (
    <div className="enhancement-card">
      <div className="card-header">
        <h4 className="card-title">
          {enhancement.enhancement_type === 'job_tailoring'
            ? 'Job Tailoring'
            : 'Industry Revamp'}
        </h4>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className={`status-badge ${getStatusClass(enhancement.status)}`}>
            {enhancement.status}
          </span>
          <button
            onClick={onDelete}
            className="btn btn-icon"
            disabled={isDeleting}
            title="Delete this enhancement"
            aria-label="Delete enhancement"
            aria-busy={isDeleting}
          >
            {isDeleting ? '...' : '✕'}
          </button>
        </div>
      </div>
      <div className="card-content">
        <p className="card-text">
          <strong>Resume:</strong> {resume?.filename || 'Unknown'}
        </p>
        {job && (
          <p className="card-text">
            <strong>Job:</strong> {job.title}
            {job.company && ` at ${job.company}`}
          </p>
        )}
        {enhancement.industry && (
          <p className="card-text">
            <strong>Industry:</strong> {enhancement.industry}
          </p>
        )}
        <p className="card-text">
          <strong>Created:</strong>{' '}
          {new Date(enhancement.created_at).toLocaleString()}
        </p>
        {enhancement.job_match_score !== null && (
          <div className="match-score-container" style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <strong>Job Match Score: </strong>
            <span
              className="status-badge"
              style={{
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
        <div className="cover-letter-section">
          <div className="cover-letter-header">
            <strong>Cover Letter:</strong>
            <span className={`status-badge ${getCoverLetterStatusClass(enhancement.cover_letter_status)}`}>
              {getCoverLetterStatusLabel(enhancement.cover_letter_status)}
            </span>
          </div>

          {enhancement.cover_letter_status === 'completed' && (
            <div className="card-actions">
              <button
                onClick={() => handleDownloadCoverLetter('md')}
                className="btn btn-secondary"
              >
                Download Markdown
              </button>
              <button
                onClick={() => handleDownloadCoverLetter('pdf')}
                className="btn btn-primary"
              >
                Download PDF
              </button>
              <button
                onClick={() => handleDownloadCoverLetter('docx')}
                className="btn btn-primary"
              >
                Download DOCX
              </button>
            </div>
          )}

          {enhancement.cover_letter_status === 'in_progress' && (
            <p className="pending-note">⏳ Generating cover letter...</p>
          )}

          {enhancement.cover_letter_status === 'pending' &&
            enhancement.status === 'completed' && (
              <p className="pending-note">
                ⏳ Will generate after resume completes...
              </p>
            )}

          {enhancement.cover_letter_status === 'failed' &&
            enhancement.cover_letter_error && (
              <p className="error-note">
                ❌ {enhancement.cover_letter_error}
              </p>
            )}

          {enhancement.cover_letter_status === 'skipped' && (
            <p className="help-text">
              Cover letters are only generated for job-specific tailoring, not
              industry revamps.
            </p>
          )}
        </div>
      )}

      {enhancement.status === 'completed' && (
        <div className="card-actions">
          <button
            onClick={() => handleDownload('md')}
            className="btn btn-secondary"
          >
            Download Markdown
          </button>
          <button
            onClick={() => handleDownload('pdf')}
            className="btn btn-primary"
          >
            Download PDF
          </button>
          <button
            onClick={handleDownloadDocx}
            className="btn btn-primary"
          >
            Download DOCX
          </button>
          <button
            onClick={handleViewComparison}
            className="btn btn-info"
          >
            View Comparison
          </button>
        </div>
      )}
      {enhancement.status === 'pending' && (
        <p className="pending-note">
          ⏳ Waiting for Claude Code to process...
        </p>
      )}
      {enhancement.status === 'failed' && enhancement.error_message && (
        <p className="error-note">❌ {enhancement.error_message}</p>
      )}
    </div>
  );
};
