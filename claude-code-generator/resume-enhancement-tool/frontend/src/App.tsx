import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ResumeUpload } from './components/ResumeUpload';
import { JobForm } from './components/JobForm';
import { EnhancementDashboard } from './components/EnhancementDashboard';
import { ComparisonView } from './components/ComparisonView';
import StylePreview from './components/StylePreview';
import { DarkModeToggle } from './components/DarkModeToggle';
import { LoginForm } from './components/LoginForm';
import { SignupForm } from './components/SignupForm';
import { LandingPage } from './components/LandingPage';
import { UserMenu } from './components/UserMenu';
import { ProtectedRoute } from './components/ProtectedRoute';
import { DarkModeProvider, useDarkMode } from './contexts/DarkModeContext';
import { AuthProvider } from './contexts/AuthContext';
import { resumeApi, jobApi } from './services/api';
import type { Resume, Job, Enhancement } from './types';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <DarkModeProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginForm />} />
            <Route path="/signup" element={<SignupForm />} />
            <Route path="/" element={<LandingPage />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <MainApp />
                </ProtectedRoute>
              }
            />
            <Route
              path="/comparison/:enhancementId"
              element={
                <ProtectedRoute>
                  <ComparisonView />
                </ProtectedRoute>
              }
            />
          </Routes>
        </BrowserRouter>
      </DarkModeProvider>
    </AuthProvider>
  );
}

function MainApp() {
  const { isDarkMode } = useDarkMode();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [activeTab, setActiveTab] = useState<'upload' | 'jobs' | 'enhance'>('upload');
  const [showStyleSelection, setShowStyleSelection] = useState<boolean>(false);
  const [currentResumeForStyle, setCurrentResumeForStyle] = useState<Resume | null>(null);

  useEffect(() => {
    loadData();
    // Initialize dark mode class on body
    if (isDarkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [isDarkMode]);

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
    if (!window.confirm('Are you sure you want to delete this resume?')) {
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
    if (!window.confirm('Are you sure you want to delete ALL resumes?')) {
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
    <div className={`app-container ${isDarkMode ? 'dark-mode' : ''}`}>
      {/* Header */}
      <header className="app-header">
        <div className="app-header-inner">
          <div className="app-logo">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M16 13H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M16 17H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M10 9H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            ResumeMagic
          </div>
          <div className="header-actions">
            <UserMenu />
            <DarkModeToggle />
          </div>
        </div>
      </header>

      {/* Stats Bar */}
      <div className="stats-bar">
        <div className="stats-inner">
          <div className="stat-item">
            <div className="stat-value">{resumes.length}</div>
            <div className="stat-label">Resumes</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{jobs.length}</div>
            <div className="stat-label">Jobs</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">Ready</div>
            <div className="stat-label">Status</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="main-content">
        <div className="tabs-container">
          <div className="tabs-list">
            <button
              onClick={() => setActiveTab('upload')}
              className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
            >
              Upload Resume
              {resumes.length > 0 && <span className="tab-badge">{resumes.length}</span>}
            </button>
            <button
              onClick={() => setActiveTab('jobs')}
              className={`tab-button ${activeTab === 'jobs' ? 'active' : ''}`}
            >
              Add Jobs
              {jobs.length > 0 && <span className="tab-badge">{jobs.length}</span>}
            </button>
            <button
              onClick={() => setActiveTab('enhance')}
              className={`tab-button ${activeTab === 'enhance' ? 'active' : ''}`}
            >
              Create Enhancement
            </button>
          </div>
        </div>

        {/* Style Selection Modal */}
        {showStyleSelection && currentResumeForStyle && (
          <div className="modal-overlay" onClick={handleCloseStyleSelection}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <button onClick={handleCloseStyleSelection} className="close-button">×</button>
              <StylePreview
                resumeId={currentResumeForStyle.id}
                onStyleSelected={handleStyleSelected}
                onClose={handleCloseStyleSelection}
              />
            </div>
          </div>
        )}

        {activeTab === 'upload' && (
          <div className="section-card animate-fade-in">
            <div className="section-header">
              <h2 className="section-title">Upload Resume</h2>
              <p className="section-subtitle">Start by uploading your current resume to let our AI analyze it for you.</p>
            </div>
            <ResumeUpload onUploadSuccess={handleResumeUploaded} />

            {resumes.length > 0 && (
              <div className="list-container">
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', alignItems: 'center' }}>
                  <h3 className="section-title" style={{ fontSize: '1.25rem', margin: 0 }}>Your Resumes</h3>
                  <button onClick={handleDeleteAllResumes} className="btn btn-danger">Delete All</button>
                </div>
                <div className="list">
                  {resumes.map((resume) => (
                    <div key={resume.id} className="list-item">
                      <div className="list-item-content">
                        <div className="list-item-title">{resume.filename}</div>
                        <div className="list-item-meta">
                          {resume.word_count} words · {new Date(resume.upload_date).toLocaleDateString()}
                          {resume.selected_style && (
                            <span className="tab-badge" style={{ background: 'var(--primary-light)', color: 'var(--primary)', marginLeft: '8px' }}>
                              {resume.selected_style}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="list-item-actions" style={{ display: 'flex', gap: '0.5rem' }}>
                        <button onClick={() => handleSelectStyleForResume(resume)} className="btn btn-primary">
                          Select Style
                        </button>
                        <button onClick={() => handleDeleteResume(resume.id)} className="btn btn-icon">
                          ×
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
          <div className="section-card animate-fade-in">
            <div className="section-header">
              <h2 className="section-title">Add Job Descriptions</h2>
              <p className="section-subtitle">Paste the job description you are applying for. We'll tailor your resume to match.</p>
            </div>
            <JobForm onJobCreated={handleJobCreated} />

            {jobs.length > 0 && (
              <div className="list-container">
                <h3 className="section-title" style={{ fontSize: '1.25rem' }}>Your Jobs</h3>
                <div className="list">
                  {jobs.map((job) => (
                    <div key={job.id} className="list-item">
                      <div className="list-item-content">
                        <div className="list-item-title">
                          {job.title}
                          {job.company && <span style={{ opacity: 0.7 }}> at {job.company}</span>}
                        </div>
                        <div className="list-item-meta">
                          Added {new Date(job.created_at).toLocaleDateString()}
                        </div>
                      </div>
                      <span className="tab-badge" style={{ background: 'var(--secondary)', color: 'white' }}>Active</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'enhance' && (
          <div className="section-card animate-fade-in">
            {resumes.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '4rem 2rem' }}>
                <h3 className="section-title" style={{ fontSize: '1.5rem' }}>No Resumes Yet</h3>
                <p className="section-subtitle" style={{ marginBottom: '1.5rem' }}>Upload your resume to start creating enhancements</p>
                <button onClick={() => setActiveTab('upload')} className="btn btn-primary">
                  Upload Resume
                </button>
              </div>
            ) : (
              <>
                <div className="section-header">
                  <h2 className="section-title">Create Enhancement</h2>
                  <p className="section-subtitle">Generate tailored versions of your resume optimized for specific job descriptions.</p>
                </div>
                <EnhancementDashboard
                  resumes={resumes}
                  jobs={jobs}
                  onEnhancementCreated={handleEnhancementCreated}
                />
              </>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-inner">
          Resume Enhancement Tool · Powered by Claude AI
          <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="footer-link">
            API Documentation
          </a>
        </div>
      </footer>
    </div>
  );
}

export default App;
