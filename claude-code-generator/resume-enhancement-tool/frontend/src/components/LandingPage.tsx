import React from 'react';
import { Link } from 'react-router-dom';
import { DarkModeToggle } from './DarkModeToggle';

export const LandingPage: React.FC = () => {
  return (
    <div className="app-container">
      {/* Header/Nav */}
      <header className="app-header">
        <div className="header-inner">
          <div className="logo">Resume Enhancement</div>
          <div className="header-actions">
            <Link to="/login" className="nav-link">
              Sign In
            </Link>
            <Link to="/signup" className="btn btn-primary">
              Get Started
            </Link>
            <DarkModeToggle />
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="landing-hero">
        <h1 className="landing-title">
          Build a Resume That Gets You Hired
        </h1>
        <p className="landing-subtitle">
          Create professional, ATS-friendly resumes tailored to any job description.
          Powered by AI to maximize your chances of landing interviews.
        </p>
        <div className="hero-cta" style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginBottom: '4rem' }}>
          <Link to="/signup" className="btn btn-primary" style={{ padding: '1rem 2rem', fontSize: '1rem' }}>
            Create My Resume
          </Link>
          <Link to="/login" className="btn btn-secondary" style={{ padding: '1rem 2rem', fontSize: '1rem' }}>
            I Have an Account
          </Link>
        </div>
        <div className="stats-bar" style={{ maxWidth: '600px', margin: '0 auto', justifyContent: 'center', gap: '3rem', background: 'transparent', boxShadow: 'none' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--primary)', lineHeight: 1 }}>38%</div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>More Interviews</div>
          </div>
          <div style={{ width: '1px', height: '40px', backgroundColor: 'var(--border)' }}></div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--primary)', lineHeight: 1 }}>2x</div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Faster Results</div>
          </div>
          <div style={{ width: '1px', height: '40px', backgroundColor: 'var(--border)' }}></div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--primary)', lineHeight: 1 }}>100%</div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>ATS Compatible</div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="features-inner">
          <h2 className="section-title">Everything You Need</h2>
          <p className="section-subtitle">
            Professional tools to create resumes that stand out
          </p>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
              </div>
              <h3 className="feature-title">AI-Powered Writing</h3>
              <p className="feature-text">
                Get intelligent suggestions to improve your resume content and make it more impactful.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <circle cx="8.5" cy="8.5" r="1.5"></circle>
                  <polyline points="21 15 16 10 5 21"></polyline>
                </svg>
              </div>
              <h3 className="feature-title">Multiple Styles</h3>
              <p className="feature-text">
                Choose from professional writing styles to match your industry and target role.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
              </div>
              <h3 className="feature-title">ATS Optimized</h3>
              <p className="feature-text">
                Automatically optimize your resume to pass Applicant Tracking Systems used by employers.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                  <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                  <line x1="12" y1="22.08" x2="12" y2="12"></line>
                </svg>
              </div>
              <h3 className="feature-title">Job Tailoring</h3>
              <p className="feature-text">
                Customize your resume for each job application to maximize your chances of getting hired.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="16 18 22 12 16 6"></polyline>
                  <polyline points="8 6 2 12 8 18"></polyline>
                </svg>
              </div>
              <h3 className="feature-title">Cover Letters</h3>
              <p className="feature-text">
                Automatically generate professional cover letters tailored to each position.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
              </div>
              <h3 className="feature-title">Export Options</h3>
              <p className="feature-text">
                Download your resume in PDF, DOCX, or Markdown format for any application.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="cta-section">
        <div className="cta-inner">
          <h2 className="cta-title">Ready to Land Your Dream Job?</h2>
          <p className="cta-text">
            Join thousands of job seekers who have successfully landed interviews with our tool.
          </p>
          <Link to="/signup" className="btn btn-primary btn-large">
            Create Your Resume Now
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="app-footer" style={{ marginTop: 0 }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '2rem', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <h4 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem' }}>Resume Enhancement</h4>
            <p style={{ fontSize: '0.875rem', lineHeight: 1.6, color: 'var(--text-secondary)' }}>
              Build professional resumes that get you hired.
            </p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <h4 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem' }}>Product</h4>
            <Link to="/signup" style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', textDecoration: 'none' }}>Get Started</Link>
            <Link to="/login" style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', textDecoration: 'none' }}>Sign In</Link>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <h4 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem' }}>Resources</h4>
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', textDecoration: 'none' }}>
              API Docs
            </a>
          </div>
        </div>
        <div style={{ borderTop: '1px solid var(--border)', paddingTop: '2rem', textAlign: 'center', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          © 2026 Resume Enhancement Tool. Powered by Claude AI.
        </div>
      </footer>
    </div>
  );
};
