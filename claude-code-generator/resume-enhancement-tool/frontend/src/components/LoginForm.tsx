import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useDarkMode } from '../contexts/DarkModeContext';
import { fadeIn, staggerContainer, hoverScale, pulse, reveal } from '../lib/motion';

export const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const { isDarkMode } = useDarkMode();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login({ email, password });
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.response?.data?.detail || 'Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      variants={fadeIn}
      initial="initial"
      animate="animate"
      className={`auth-container ${isDarkMode ? 'auth-container-dark' : 'auth-container-light'}`}
    >
      <motion.div
        variants={staggerContainer}
        className={`auth-card ${isDarkMode ? 'auth-card-dark' : 'auth-card-light'}`}
      >
        {/* Logo/Icon */}
        <motion.div variants={fadeIn} className="auth-header">
          <div className="auth-logo">
            📄
          </div>
          <h2 className="auth-title">
            Welcome Back
          </h2>
          <p className="auth-subtitle">
            Sign in to continue to Resume Enhancement Tool
          </p>
        </motion.div>

        <form onSubmit={handleSubmit} className="auth-form">
          <AnimatePresence mode="wait">
            {error && (
              <motion.div
                key="error"
                variants={reveal}
                initial="initial"
                animate="animate"
                exit={{ opacity: 0, scale: 0.95 }}
                className="auth-error"
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          <motion.div variants={fadeIn} className="auth-field">
            <label htmlFor="email" className="auth-label">
              Email Address
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="auth-input"
              placeholder="you@example.com"
            />
          </motion.div>

          <motion.div variants={fadeIn} className="auth-field">
            <label htmlFor="password" className="auth-label">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="auth-input"
              placeholder="••••••••"
            />
          </motion.div>

          <motion.div variants={fadeIn}>
            <motion.button
              variants={hoverScale}
              whileHover="hover"
              whileTap="tap"
              type="submit"
              disabled={isLoading}
              className="auth-button"
              style={{ position: 'relative', overflow: 'hidden' }}
            >
              <AnimatePresence mode="wait">
                {isLoading ? (
                  <motion.div
                    key="loading"
                    variants={pulse}
                    initial="initial"
                    animate="animate"
                    exit={{ opacity: 0 }}
                  >
                    Signing in...
                  </motion.div>
                ) : (
                  <motion.span key="idle">Sign In</motion.span>
                )}
              </AnimatePresence>
            </motion.button>
          </motion.div>
        </form>

        <motion.div variants={fadeIn} className="auth-footer">
          <p className="auth-footer-text">
            Don't have an account?{' '}
            <motion.span
              style={{ display: 'inline-block' }}
              variants={hoverScale}
              whileHover="hover"
              whileTap="tap"
            >
              <Link
                to="/signup"
                className="auth-link"
              >
                Sign up
              </Link>
            </motion.span>
          </p>
        </motion.div>
      </motion.div>
    </motion.div>
  );
};
