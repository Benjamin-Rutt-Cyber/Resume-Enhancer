import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  FileText,
  Zap,
  Layout,
  Download,
  Star,
  Shield,
  Briefcase
} from 'lucide-react';
import { DarkModeToggle } from './DarkModeToggle';
import { fadeIn, staggerContainer, hoverScale, reveal } from '../lib/motion';


export const LandingPage: React.FC = () => {
  return (
    <div className="landing-container">
      {/* Navigation */}
      <motion.nav
        variants={fadeIn}
        initial="initial"
        animate="animate"
        className="landing-nav"
      >
        <div className="nav-content">
          <div className="logo-section">
            <span className="logo-icon">✨</span>
            <span className="logo-text">re-vsion</span>
          </div>
          <div className="nav-links">
            <Link to="/login" className="nav-link">Sign In</Link>
            <Link to="/signup" className="nav-btn-primary">Get Started</Link>
            <DarkModeToggle />
          </div>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <motion.div
            variants={staggerContainer}
            initial="initial"
            animate="animate"
            className="hero-text-container"
          >
            <motion.h1 variants={fadeIn} className="hero-title">
              Craft Your Perfect <br />
              <span className="gradient-text">Resume with AI</span>
            </motion.h1>
            <motion.p variants={fadeIn} className="hero-subtitle">
              Transform your career prospects with our AI-powered resume builder.
              Tailor your CV to any job description and beat the ATS systems instantly.
            </motion.p>
            <motion.div variants={fadeIn} className="hero-cta-group">
              <Link to="/signup" className="cta-primary">
                Create Free Resume <ArrowRight size={20} />
              </Link>
              <Link to="/login" className="cta-secondary">
                View Demo
              </Link>
            </motion.div>

            <motion.div variants={fadeIn} className="hero-stats">
              <div className="stat-pill">
                <Star size={16} style={{ color: '#fbbf24' }} />
                <span>Trusted by 10,000+ Job Seekers</span>
              </div>
            </motion.div>
          </motion.div>

          <motion.div
            variants={reveal}
            initial="initial"
            animate="animate"
            className="hero-visual"
          >
            <div className="visual-card-stack">
              <div className="card-back"></div>
              <div className="card-middle"></div>
              <div className="card-front">
                <div className="resume-preview-header">
                  <div className="skeleton-avatar"></div>
                  <div className="skeleton-lines">
                    <div className="line title"></div>
                    <div className="line subtitle"></div>
                  </div>
                </div>
                <div className="resume-preview-body">
                  <div className="skeleton-block"></div>
                  <div className="skeleton-block"></div>
                  <div className="skeleton-block"></div>
                </div>
                <div className="ai-badge">
                  <Zap size={16} /> AI Enhanced
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        <div className="hero-bg-gradient"></div>
      </section>

      {/* Features Grid */}
      <section className="features-section">
        <motion.div
          variants={staggerContainer}
          initial="initial"
          whileInView="animate"
          viewport={{ once: true, margin: "-100px" }}
          className="section-container"
        >
          <motion.div variants={fadeIn} className="section-header">
            <h2 className="section-title">Why Choose re-vsion?</h2>
            <p className="section-description">
              Powerful tools designed to get you hired faster at top companies.
            </p>
          </motion.div>

          <div className="features-grid">
            {[
              {
                icon: <Zap size={24} />,
                title: "AI Optimization",
                desc: "Smart keyword matching to pass ATS filters effortlessly."
              },
              {
                icon: <Layout size={24} />,
                title: "Modern Templates",
                desc: "Clean, professional designs that recruiters love."
              },
              {
                icon: <FileText size={24} />,
                title: "Cover Letters",
                desc: "Generate tailored cover letters in seconds."
              },
              {
                icon: <Briefcase size={24} />,
                title: "Job Tailoring",
                desc: "Custom-tailor your resume for every single application."
              },
              {
                icon: <Shield size={24} />,
                title: "Data Privacy",
                desc: "Your data is secure and never shared with recruiters."
              },
              {
                icon: <Download size={24} />,
                title: "Multi-Format",
                desc: "Export to PDF, DOCX, or Markdown with one click."
              }
            ].map((feature, idx) => (
              <motion.div
                key={idx}
                variants={fadeIn}
                whileHover="hover"
                className="feature-card"
              >
                <motion.div variants={hoverScale} className="feature-icon-wrapper">{feature.icon}</motion.div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-desc">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* Testimonials / Social Proof */}
      <section className="proof-section">
        <div className="section-container">
          <div className="proof-grid">
            <div className="proof-content">
              <h2>Join the Success Stories</h2>
              <p>Thousands have landed their dream jobs using our tools.</p>
              <div className="stat-row">
                <div className="stat">
                  <span className="stat-num">38%</span>
                  <span className="stat-lbl">More Interviews</span>
                </div>
                <div className="stat">
                  <span className="stat-num">2x</span>
                  <span className="stat-lbl">Faster Hired</span>
                </div>
              </div>
            </div>
            <div className="proof-cards">
              <motion.div
                variants={hoverScale}
                whileHover="hover"
                whileTap="tap"
                className="testimonial-card"
              >
                <div className="stars">★★★★★</div>
                <p>"I got 3 interviews in my first week after using this tool. The AI suggestions are game-changing!"</p>
                <div className="user-info">
                  <div className="user-avatar">JD</div>
                  <div>
                    <div className="user-name">John Doe</div>
                    <div className="user-role">Software Engineer</div>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section-wrapper">
        <motion.div
          variants={reveal}
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
          className="cta-card-large"
        >
          <h2>Ready to Upgrade Your Career?</h2>
          <p>Join for free and create your first AI-enhanced resume today.</p>
          <Link to="/signup" className="cta-btn-large">
            Get Started for Free
          </Link>
          <p className="cta-note">No credit card required</p>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-col">
            <h4>re-vsion</h4>
            <p>Empowering careers with technology.</p>
          </div>
          <div className="footer-col">
            <h4>Product</h4>
            <Link to="/login">Sign In</Link>
            <Link to="/signup">Sign Up</Link>
          </div>
          <div className="footer-col">
            <h4>Resources</h4>
            <a href="#">Blog</a>
            <a href="#">Examples</a>
          </div>
          <div className="footer-col">
            <h4>Legal</h4>
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
          </div>
        </div>
        <div className="footer-bottom">
          © 2026 Resume Enhancement Tool. All rights reserved.
        </div>
      </footer>
    </div>
  );
};
