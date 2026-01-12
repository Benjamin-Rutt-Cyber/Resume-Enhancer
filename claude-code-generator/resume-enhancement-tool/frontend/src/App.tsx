import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ResumeUpload } from './components/ResumeUpload';
import { JobForm } from './components/JobForm';
import { EnhancementDashboard } from './components/EnhancementDashboard';
import { ComparisonView } from './components/ComparisonView';
import StylePreview from './components/StylePreview';
import { resumeApi, jobApi } from './services/api';
import type { Resume, Job, Enhancement } from './types';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainApp />} />
        <Route path="/comparison/:enhancementId" element={<ComparisonView />} />
      </Routes>
    </BrowserRouter>
  );
}

function MainApp() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [activeTab, setActiveTab] = useState<'upload' | 'jobs' | 'enhance'>(
    'upload'
  );
  const [showStyleSelection, setShowStyleSelection] = useState<boolean>(false);
  const [currentResumeForStyle, setCurrentResumeForStyle] = useState<Resume | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [resumesResult, jobsResult] = await Promise.all([
        resumeApi.listResumes(),
        jobApi.listJobs(),
      ]);
      setResumes(resumesResult.resumes);
      setJobs(jobsResult.jobs);
    } catch (err) {
      console.error('Failed to load data:', err);
    }
  };

  const handleResumeUploaded = (resume: Resume) => {
    setResumes([resume, ...resumes]);
    setCurrentResumeForStyle(resume);
    setShowStyleSelection(true);
  };

  const handleStyleSelected = async (style: string) => {
    console.log('Style selected:', style);
    setShowStyleSelection(false);
    setCurrentResumeForStyle(null);
    // Reload resumes to get updated selected_style
    await loadData();
    setActiveTab('jobs');
  };

  const handleCloseStyleSelection = () => {
    setShowStyleSelection(false);
    setCurrentResumeForStyle(null);
  };

  const handleSelectStyleForResume = (resume: Resume) => {
    setCurrentResumeForStyle(resume);
    setShowStyleSelection(true);
  };

  const handleDeleteResume = async (resumeId: string) => {
    if (!window.confirm('Are you sure you want to delete this resume? This action cannot be undone.')) {
      return;
    }

    try {
      await resumeApi.deleteResume(resumeId);
      await loadData();
    } catch (err) {
      console.error('Failed to delete resume:', err);
      alert('Failed to delete resume. Please try again.');
    }
  };

  const handleDeleteAllResumes = async () => {
    if (!window.confirm('Are you sure you want to delete ALL resumes? This action cannot be undone!')) {
      return;
    }

    try {
      await resumeApi.deleteAllResumes();
      await loadData();
    } catch (err) {
      console.error('Failed to delete all resumes:', err);
      alert('Failed to delete all resumes. Please try again.');
    }
  };

  const handleJobCreated = (job: Job) => {
    setJobs([job, ...jobs]);
    setActiveTab('enhance');
  };

  const handleEnhancementCreated = (enhancement: Enhancement) => {
    console.log('Enhancement created:', enhancement);
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.appTitle}>Resume Enhancement Tool</h1>
        <p style={styles.subtitle}>
          Upload your resume, add job descriptions, and create tailored versions
        </p>
      </header>

      {/* Tab Navigation */}
      <div style={styles.tabs}>
        <button
          onClick={() => setActiveTab('upload')}
          style={{
            ...styles.tab,
            ...(activeTab === 'upload' ? styles.tabActive : {}),
          }}
        >
          1. Upload Resume
          {resumes.length > 0 && (
            <span style={styles.badge}>{resumes.length}</span>
          )}
        </button>
        <button
          onClick={() => setActiveTab('jobs')}
          style={{
            ...styles.tab,
            ...(activeTab === 'jobs' ? styles.tabActive : {}),
          }}
        >
          2. Add Jobs
          {jobs.length > 0 && <span style={styles.badge}>{jobs.length}</span>}
        </button>
        <button
          onClick={() => setActiveTab('enhance')}
          style={{
            ...styles.tab,
            ...(activeTab === 'enhance' ? styles.tabActive : {}),
          }}
        >
          3. Create Enhancement
        </button>
      </div>

      {/* Tab Content */}
      <main style={styles.main}>
        {/* Style Selection Overlay */}
        {showStyleSelection && currentResumeForStyle && (
          <div style={styles.modalOverlay} onClick={handleCloseStyleSelection}>
            <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
              <button
                onClick={handleCloseStyleSelection}
                style={styles.closeButton}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#e0e0e0';
                  e.currentTarget.style.color = '#333';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#f5f5f5';
                  e.currentTarget.style.color = '#666';
                }}
                title="Close"
              >
                ✕
              </button>
              <StylePreview
                resumeId={currentResumeForStyle.id}
                onStyleSelected={handleStyleSelected}
                onClose={handleCloseStyleSelection}
              />
            </div>
          </div>
        )}

        {activeTab === 'upload' && (
          <div style={styles.section}>
            <ResumeUpload onUploadSuccess={handleResumeUploaded} />
            {resumes.length > 0 && (
              <div style={styles.listSection}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h3 style={styles.listTitle}>Uploaded Resumes</h3>
                  <button
                    onClick={handleDeleteAllResumes}
                    style={styles.deleteAllButton}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#c62828';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = '#d32f2f';
                    }}
                  >
                    Delete All Resumes
                  </button>
                </div>
                <div style={styles.list}>
                  {resumes.map((resume) => (
                    <div key={resume.id} style={styles.listItem}>
                      <div style={{ flex: 1 }}>
                        <strong>{resume.filename}</strong>
                        <div style={styles.listItemMeta}>
                          {resume.word_count} words • Uploaded{' '}
                          {new Date(resume.upload_date).toLocaleDateString()}
                          {resume.selected_style && (
                            <span style={styles.styleTag}>
                              Style: {resume.selected_style}
                            </span>
                          )}
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                          onClick={() => handleSelectStyleForResume(resume)}
                          style={styles.selectStyleButton}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.backgroundColor = '#1976d2';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = '#2196F3';
                          }}
                        >
                          Select Resume
                        </button>
                        <button
                          onClick={() => handleDeleteResume(resume.id)}
                          style={styles.deleteButton}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.backgroundColor = '#c62828';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = '#d32f2f';
                          }}
                          title="Delete this resume"
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'jobs' && (
          <div style={styles.section}>
            <JobForm onJobCreated={handleJobCreated} />
            {jobs.length > 0 && (
              <div style={styles.listSection}>
                <h3 style={styles.listTitle}>Added Jobs</h3>
                <div style={styles.list}>
                  {jobs.map((job) => (
                    <div key={job.id} style={styles.listItem}>
                      <div>
                        <strong>{job.title}</strong>
                        {job.company && <> at {job.company}</>}
                        <div style={styles.listItemMeta}>
                          Added {new Date(job.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'enhance' && (
          <div style={styles.section}>
            {resumes.length === 0 ? (
              <div style={styles.emptyState}>
                <h3>No Resumes Yet</h3>
                <p>Please upload a resume first before creating enhancements.</p>
                <button
                  onClick={() => setActiveTab('upload')}
                  style={styles.button}
                >
                  Go to Upload Resume
                </button>
              </div>
            ) : (
              <EnhancementDashboard
                resumes={resumes}
                jobs={jobs}
                onEnhancementCreated={handleEnhancementCreated}
              />
            )}
          </div>
        )}
      </main>

      <footer style={styles.footer}>
        <p style={styles.footerText}>
          Resume Enhancement Tool • API running at{' '}
          <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" style={styles.link}>
            http://localhost:8000/docs
          </a>
        </p>
      </footer>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#2196F3',
    color: '#fff',
    padding: '2rem',
    textAlign: 'center',
  },
  appTitle: {
    margin: 0,
    fontSize: '2.5rem',
    fontWeight: 'bold',
  },
  subtitle: {
    margin: '0.5rem 0 0',
    fontSize: '1.1rem',
    opacity: 0.9,
  },
  tabs: {
    display: 'flex',
    backgroundColor: '#fff',
    borderBottom: '1px solid #e0e0e0',
    padding: '0 2rem',
    gap: '1rem',
  },
  tab: {
    padding: '1rem 1.5rem',
    fontSize: '1rem',
    fontWeight: '500',
    backgroundColor: 'transparent',
    border: 'none',
    borderBottom: '3px solid transparent',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    color: '#666',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  tabActive: {
    borderBottomColor: '#2196F3',
    color: '#2196F3',
  },
  badge: {
    backgroundColor: '#4CAF50',
    color: '#fff',
    borderRadius: '12px',
    padding: '0.125rem 0.5rem',
    fontSize: '0.75rem',
    fontWeight: 'bold',
  },
  main: {
    flex: 1,
    padding: '2rem',
    maxWidth: '1200px',
    width: '100%',
    margin: '0 auto',
  },
  section: {
    backgroundColor: '#fff',
    borderRadius: '8px',
    padding: '2rem',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  listSection: {
    marginTop: '2rem',
    paddingTop: '2rem',
    borderTop: '1px solid #e0e0e0',
  },
  listTitle: {
    fontSize: '1.25rem',
    fontWeight: 'bold',
    marginBottom: '1rem',
    color: '#333',
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
  },
  listItem: {
    padding: '1rem',
    backgroundColor: '#f9f9f9',
    borderRadius: '4px',
    border: '1px solid #e0e0e0',
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
  },
  listItemMeta: {
    fontSize: '0.875rem',
    color: '#888',
    marginTop: '0.25rem',
  },
  styleTag: {
    marginLeft: '0.5rem',
    padding: '0.125rem 0.5rem',
    backgroundColor: '#e3f2fd',
    color: '#1976d2',
    borderRadius: '12px',
    fontSize: '0.75rem',
    fontWeight: 'bold',
  },
  selectStyleButton: {
    padding: '0.5rem 1rem',
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
  deleteButton: {
    padding: '0.5rem 0.75rem',
    fontSize: '1rem',
    fontWeight: 'bold',
    color: '#fff',
    backgroundColor: '#d32f2f',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    minWidth: '36px',
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
  closeButton: {
    position: 'absolute',
    top: '20px',
    right: '20px',
    width: '40px',
    height: '40px',
    backgroundColor: '#f5f5f5',
    border: 'none',
    borderRadius: '50%',
    fontSize: '24px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#666',
    transition: 'all 0.2s',
    zIndex: 10,
  },
  emptyState: {
    textAlign: 'center',
    padding: '3rem',
    color: '#666',
  },
  button: {
    marginTop: '1rem',
    padding: '0.75rem 1.5rem',
    fontSize: '1rem',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#2196F3',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  footer: {
    backgroundColor: '#fff',
    borderTop: '1px solid #e0e0e0',
    padding: '1rem 2rem',
    textAlign: 'center',
  },
  footerText: {
    margin: 0,
    color: '#888',
    fontSize: '0.9rem',
  },
  link: {
    color: '#2196F3',
    textDecoration: 'none',
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    zIndex: 1000,
    overflowY: 'auto',
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'center',
    padding: '20px',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: '12px',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
    maxWidth: '1400px',
    width: '100%',
    margin: '40px auto',
    position: 'relative',
  },
};

export default App;
