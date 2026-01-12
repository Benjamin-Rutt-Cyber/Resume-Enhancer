import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ResumeUpload } from './components/ResumeUpload';
import { JobForm } from './components/JobForm';
import { EnhancementDashboard } from './components/EnhancementDashboard';
import { ComparisonView } from './components/ComparisonView';
import StylePreview from './components/StylePreview';
import { DarkModeToggle } from './components/DarkModeToggle';
import { DarkModeProvider, useDarkMode } from './contexts/DarkModeContext';
import { resumeApi, jobApi } from './services/api';
import type { Resume, Job, Enhancement } from './types';

function App() {
  return (
    <DarkModeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainApp />} />
          <Route path="/comparison/:enhancementId" element={<ComparisonView />} />
        </Routes>
      </BrowserRouter>
    </DarkModeProvider>
  );
}

function MainApp() {
  const { isDarkMode } = useDarkMode();
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

  const getStyles = () => getStylesWithTheme(isDarkMode);
  const s = getStyles();

  return (
    <div style={s.container}>
      <header style={s.header}>
        <div style={s.headerContent}>
          <div>
            <h1 style={s.appTitle}>Resume Enhancement Tool</h1>
            <p style={s.subtitle}>
              Upload your resume, add job descriptions, and create tailored versions
            </p>
          </div>
          <DarkModeToggle />
        </div>
      </header>

      {/* Tab Navigation */}
      <div style={s.tabs}>
        <button
          onClick={() => setActiveTab('upload')}
          style={{
            ...s.tab,
            ...(activeTab === 'upload' ? s.tabActive : {}),
          }}
        >
          1. Upload Resume
          {resumes.length > 0 && (
            <span style={s.badge}>{resumes.length}</span>
          )}
        </button>
        <button
          onClick={() => setActiveTab('jobs')}
          style={{
            ...s.tab,
            ...(activeTab === 'jobs' ? s.tabActive : {}),
          }}
        >
          2. Add Jobs
          {jobs.length > 0 && <span style={s.badge}>{jobs.length}</span>}
        </button>
        <button
          onClick={() => setActiveTab('enhance')}
          style={{
            ...s.tab,
            ...(activeTab === 'enhance' ? s.tabActive : {}),
          }}
        >
          3. Create Enhancement
        </button>
      </div>

      {/* Tab Content */}
      <main style={s.main}>
        {/* Style Selection Overlay */}
        {showStyleSelection && currentResumeForStyle && (
          <div style={s.modalOverlay} onClick={handleCloseStyleSelection}>
            <div style={s.modalContent} onClick={(e) => e.stopPropagation()}>
              <button
                onClick={handleCloseStyleSelection}
                style={s.closeButton}
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
          <div style={s.section}>
            <ResumeUpload onUploadSuccess={handleResumeUploaded} />
            {resumes.length > 0 && (
              <div style={s.listSection}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h3 style={s.listTitle}>Uploaded Resumes</h3>
                  <button
                    onClick={handleDeleteAllResumes}
                    style={s.deleteAllButton}
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
                <div style={s.list}>
                  {resumes.map((resume) => (
                    <div key={resume.id} style={s.listItem}>
                      <div style={{ flex: 1 }}>
                        <strong>{resume.filename}</strong>
                        <div style={s.listItemMeta}>
                          {resume.word_count} words • Uploaded{' '}
                          {new Date(resume.upload_date).toLocaleDateString()}
                          {resume.selected_style && (
                            <span style={s.styleTag}>
                              Style: {resume.selected_style}
                            </span>
                          )}
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                          onClick={() => handleSelectStyleForResume(resume)}
                          style={s.selectStyleButton}
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
                          style={s.deleteButton}
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
          <div style={s.section}>
            <JobForm onJobCreated={handleJobCreated} />
            {jobs.length > 0 && (
              <div style={s.listSection}>
                <h3 style={s.listTitle}>Added Jobs</h3>
                <div style={s.list}>
                  {jobs.map((job) => (
                    <div key={job.id} style={s.listItem}>
                      <div>
                        <strong>{job.title}</strong>
                        {job.company && <> at {job.company}</>}
                        <div style={s.listItemMeta}>
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
          <div style={s.section}>
            {resumes.length === 0 ? (
              <div style={s.emptyState}>
                <h3>No Resumes Yet</h3>
                <p>Please upload a resume first before creating enhancements.</p>
                <button
                  onClick={() => setActiveTab('upload')}
                  style={s.button}
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

      <footer style={s.footer}>
        <p style={s.footerText}>
          Resume Enhancement Tool • API running at{' '}
          <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" style={s.link}>
            http://localhost:8000/docs
          </a>
        </p>
      </footer>
    </div>
  );
}

const getStylesWithTheme = (isDarkMode: boolean): Record<string, React.CSSProperties> => ({
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: isDarkMode ? '#111827' : '#f5f5f5',
    transition: 'background-color 0.3s ease',
  },
  header: {
    backgroundColor: isDarkMode ? '#1f2937' : '#2196F3',
    color: '#fff',
    padding: '2rem',
    transition: 'background-color 0.3s ease',
  },
  headerContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    maxWidth: '1200px',
    margin: '0 auto',
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
    backgroundColor: isDarkMode ? '#1f2937' : '#fff',
    borderBottom: isDarkMode ? '1px solid #374151' : '1px solid #e0e0e0',
    padding: '0 2rem',
    gap: '1rem',
    transition: 'all 0.3s ease',
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
    color: isDarkMode ? '#9ca3af' : '#666',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  tabActive: {
    borderBottomColor: isDarkMode ? '#60a5fa' : '#2196F3',
    color: isDarkMode ? '#60a5fa' : '#2196F3',
  },
  badge: {
    backgroundColor: isDarkMode ? '#059669' : '#4CAF50',
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
    backgroundColor: isDarkMode ? '#1f2937' : '#fff',
    borderRadius: '8px',
    padding: '2rem',
    boxShadow: isDarkMode
      ? '0 2px 4px rgba(0,0,0,0.3)'
      : '0 2px 4px rgba(0,0,0,0.1)',
    transition: 'all 0.3s ease',
  },
  listSection: {
    marginTop: '2rem',
    paddingTop: '2rem',
    borderTop: isDarkMode ? '1px solid #374151' : '1px solid #e0e0e0',
  },
  listTitle: {
    fontSize: '1.25rem',
    fontWeight: 'bold',
    marginBottom: '1rem',
    color: isDarkMode ? '#f3f4f6' : '#333',
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
  },
  listItem: {
    padding: '1rem',
    backgroundColor: isDarkMode ? '#374151' : '#f9f9f9',
    borderRadius: '4px',
    border: isDarkMode ? '1px solid #4b5563' : '1px solid #e0e0e0',
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    transition: 'all 0.3s ease',
    color: isDarkMode ? '#f3f4f6' : '#000',
  },
  listItemMeta: {
    fontSize: '0.875rem',
    color: isDarkMode ? '#9ca3af' : '#888',
    marginTop: '0.25rem',
  },
  styleTag: {
    marginLeft: '0.5rem',
    padding: '0.125rem 0.5rem',
    backgroundColor: isDarkMode ? '#1e3a8a' : '#e3f2fd',
    color: isDarkMode ? '#93c5fd' : '#1976d2',
    borderRadius: '12px',
    fontSize: '0.75rem',
    fontWeight: 'bold',
  },
  selectStyleButton: {
    padding: '0.5rem 1rem',
    fontSize: '0.875rem',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: isDarkMode ? '#3b82f6' : '#2196F3',
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
    backgroundColor: isDarkMode ? '#dc2626' : '#d32f2f',
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
    backgroundColor: isDarkMode ? '#dc2626' : '#d32f2f',
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
    backgroundColor: isDarkMode ? '#374151' : '#f5f5f5',
    border: 'none',
    borderRadius: '50%',
    fontSize: '24px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: isDarkMode ? '#9ca3af' : '#666',
    transition: 'all 0.2s',
    zIndex: 10,
  },
  emptyState: {
    textAlign: 'center',
    padding: '3rem',
    color: isDarkMode ? '#9ca3af' : '#666',
  },
  button: {
    marginTop: '1rem',
    padding: '0.75rem 1.5rem',
    fontSize: '1rem',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: isDarkMode ? '#3b82f6' : '#2196F3',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  footer: {
    backgroundColor: isDarkMode ? '#1f2937' : '#fff',
    borderTop: isDarkMode ? '1px solid #374151' : '1px solid #e0e0e0',
    padding: '1rem 2rem',
    textAlign: 'center',
    transition: 'all 0.3s ease',
  },
  footerText: {
    margin: 0,
    color: isDarkMode ? '#9ca3af' : '#888',
    fontSize: '0.9rem',
  },
  link: {
    color: isDarkMode ? '#60a5fa' : '#2196F3',
    textDecoration: 'none',
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: isDarkMode ? 'rgba(0, 0, 0, 0.85)' : 'rgba(0, 0, 0, 0.7)',
    zIndex: 1000,
    overflowY: 'auto',
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'center',
    padding: '20px',
  },
  modalContent: {
    backgroundColor: isDarkMode ? '#1f2937' : '#fff',
    borderRadius: '12px',
    boxShadow: isDarkMode
      ? '0 8px 32px rgba(0, 0, 0, 0.5)'
      : '0 8px 32px rgba(0, 0, 0, 0.3)',
    maxWidth: '1400px',
    width: '100%',
    margin: '40px auto',
    position: 'relative',
    transition: 'all 0.3s ease',
  },
});

export default App;
