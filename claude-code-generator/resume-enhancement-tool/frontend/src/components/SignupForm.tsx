import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useDarkMode } from '../contexts/DarkModeContext';

// SECURITY: Minimum password length per spec (allows passphrases)
const MIN_PASSWORD_LENGTH = 12;

export const SignupForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [acceptTerms, setAcceptTerms] = useState(false);  // COMPLIANCE: Terms acceptance
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { signup } = useAuth();
  const { isDarkMode } = useDarkMode();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // SECURITY: Validate password length (12 characters minimum)
    if (password.length < MIN_PASSWORD_LENGTH) {
      setError(`Password must be at least ${MIN_PASSWORD_LENGTH} characters long`);
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // COMPLIANCE: Require terms acceptance
    if (!acceptTerms) {
      setError('You must accept the terms of service to create an account');
      return;
    }

    setIsLoading(true);

    try {
      await signup({
        email,
        password,
        full_name: fullName || undefined,
        accept_terms: acceptTerms,  // COMPLIANCE: Send terms acceptance
      });
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create account');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`auth-container ${isDarkMode ? 'auth-container-dark' : 'auth-container-light'}`}>
      <div className={`auth-card ${isDarkMode ? 'auth-card-dark' : 'auth-card-light'}`}>
        {/* Logo/Icon */}
        <div className="auth-header">
          <div className="auth-logo">
            ✨
          </div>
          <h2 className="auth-title">
            Create Account
          </h2>
          <p className="auth-subtitle">
            Start enhancing your resume today
          </p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}

          <div className="auth-field">
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
          </div>

          <div className="auth-field">
            <label htmlFor="full-name" className="auth-label">
              Full Name{' '}
              <span className="auth-sublabel">
                (optional)
              </span>
            </label>
            <input
              id="full-name"
              name="full-name"
              type="text"
              autoComplete="name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="auth-input"
              placeholder="John Doe"
            />
          </div>

          <div className="auth-field">
            <label htmlFor="password" className="auth-label">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="new-password"
              required
              minLength={MIN_PASSWORD_LENGTH}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="auth-input"
              placeholder="••••••••••••"
            />
            <p className="auth-hint">
              Must be at least {MIN_PASSWORD_LENGTH} characters (passphrases recommended)
            </p>
          </div>

          <div className="auth-field">
            <label htmlFor="confirm-password" className="auth-label">
              Confirm Password
            </label>
            <input
              id="confirm-password"
              name="confirm-password"
              type="password"
              autoComplete="new-password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="auth-input"
              placeholder="••••••••••••"
            />
          </div>

          {/* COMPLIANCE: Terms of Service acceptance */}
          <div className="auth-field">
            <label className="auth-checkbox-label">
              <input
                type="checkbox"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
                className="auth-checkbox"
                required
              />
              <span className="auth-checkbox-text">
                I accept the{' '}
                <a
                  href="/terms"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="auth-link"
                >
                  Terms of Service
                </a>
                {' '}and acknowledge that my data will be processed by Anthropic AI
              </span>
            </label>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="auth-button"
          >
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <div className="auth-footer">
          <p className="auth-footer-text">
            Already have an account?{' '}
            <Link
              to="/login"
              className="auth-link"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};
