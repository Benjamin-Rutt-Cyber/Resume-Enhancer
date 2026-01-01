import React, { useState, useEffect, useMemo } from 'react';
import { styleApi } from '../services/api';
import type { StylePreviewItem } from '../types';

interface StylePreviewProps {
  resumeId: string;
  onStyleSelected: (style: string) => void;
  onClose?: () => void;
}

interface StyleCardProps {
  preview: StylePreviewItem;
  isSelected: boolean;
  onSelect: () => void;
}

// Move styles outside component to prevent recreation on every render
const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '40px 20px',
  } as React.CSSProperties,
  header: {
    textAlign: 'center' as const,
    marginBottom: '40px',
  } as React.CSSProperties,
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '10px',
  } as React.CSSProperties,
  subtitle: {
    fontSize: '16px',
    color: '#666',
    maxWidth: '600px',
    margin: '0 auto',
  } as React.CSSProperties,
  loadingContainer: {
    textAlign: 'center' as const,
    padding: '60px 20px',
  } as React.CSSProperties,
  spinner: {
    display: 'inline-block',
    width: '50px',
    height: '50px',
    border: '4px solid #f3f3f3',
    borderTop: '4px solid #3498db',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    marginBottom: '20px',
  } as React.CSSProperties,
  loadingText: {
    fontSize: '18px',
    color: '#666',
  } as React.CSSProperties,
  errorContainer: {
    backgroundColor: '#fee',
    border: '1px solid #fcc',
    borderRadius: '8px',
    padding: '20px',
    margin: '20px 0',
    textAlign: 'center' as const,
  } as React.CSSProperties,
  errorText: {
    color: '#c33',
    fontSize: '16px',
  } as React.CSSProperties,
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '24px',
    marginBottom: '40px',
  } as React.CSSProperties,
  card: {
    border: '2px solid #ddd',
    borderRadius: '12px',
    padding: '24px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    backgroundColor: '#fff',
  } as React.CSSProperties,
  cardSelected: {
    border: '2px solid #3498db',
    backgroundColor: '#f0f8ff',
    boxShadow: '0 4px 12px rgba(52, 152, 219, 0.2)',
  } as React.CSSProperties,
  cardHover: {
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
  } as React.CSSProperties,
  cardHeader: {
    marginBottom: '12px',
  } as React.CSSProperties,
  styleName: {
    fontSize: '22px',
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  } as React.CSSProperties,
  checkmark: {
    color: '#3498db',
    fontSize: '24px',
    fontWeight: 'bold',
  } as React.CSSProperties,
  styleDescription: {
    fontSize: '14px',
    color: '#7f8c8d',
    marginBottom: '16px',
  } as React.CSSProperties,
  previewLabel: {
    fontSize: '12px',
    fontWeight: 'bold',
    color: '#555',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
    marginBottom: '8px',
  } as React.CSSProperties,
  previewText: {
    backgroundColor: '#f8f9fa',
    padding: '16px',
    borderRadius: '8px',
    fontSize: '14px',
    lineHeight: '1.6',
    color: '#333',
    fontStyle: 'italic',
    border: '1px solid #e9ecef',
  } as React.CSSProperties,
  continueContainer: {
    textAlign: 'center' as const,
    marginTop: '40px',
  } as React.CSSProperties,
  continueButton: {
    backgroundColor: '#3498db',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    padding: '16px 48px',
    fontSize: '18px',
    fontWeight: 'bold',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 2px 8px rgba(52, 152, 219, 0.3)',
  } as React.CSSProperties,
  continueButtonDisabled: {
    backgroundColor: '#bdc3c7',
    cursor: 'not-allowed',
    boxShadow: 'none',
  } as React.CSSProperties,
  continueButtonHover: {
    backgroundColor: '#2980b9',
    boxShadow: '0 4px 12px rgba(52, 152, 219, 0.4)',
  } as React.CSSProperties,
};

// Memoize StyleCard to prevent unnecessary re-renders
const StyleCard = React.memo<StyleCardProps>(({ preview, isSelected, onSelect }) => {
  const [isHovered, setIsHovered] = useState(false);

  // Memoize cardStyle calculation
  const cardStyle = useMemo(() => ({
    ...styles.card,
    ...(isSelected ? styles.cardSelected : {}),
    ...(isHovered && !isSelected ? styles.cardHover : {}),
  }), [isSelected, isHovered]);

  return (
    <div
      onClick={onSelect}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={cardStyle}
    >
      <div style={styles.cardHeader}>
        <div style={styles.styleName}>
          {preview.name}
          {isSelected && <span style={styles.checkmark}>✓</span>}
        </div>
        <p style={styles.styleDescription}>{preview.description}</p>
      </div>

      <div>
        <div style={styles.previewLabel}>Professional Summary Preview:</div>
        <div style={styles.previewText}>{preview.preview_text}</div>
      </div>
    </div>
  );
});

const StylePreview: React.FC<StylePreviewProps> = ({ resumeId, onStyleSelected }) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [previews, setPreviews] = useState<StylePreviewItem[]>([]);
  const [selectedStyle, setSelectedStyle] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);

  useEffect(() => {
    const abortController = new AbortController();

    const fetchPreviews = async () => {
      setLoading(true);
      setError(null);

      try {
        // Try to get existing previews
        const response = await styleApi.getStylePreviews(resumeId);

        // Only update state if component is still mounted
        if (!abortController.signal.aborted) {
          setPreviews(response.previews);
        }
      } catch (err: any) {
        // Ignore errors from aborted requests
        if (err.name === 'CanceledError' || abortController.signal.aborted) {
          return;
        }

        console.error('Error fetching style previews:', err);
        if (err.response?.status === 404) {
          // Previews haven't been generated yet - show manual generation message
          setError('manual-generation-needed');
        } else {
          setError(
            err.response?.data?.detail ||
              'Failed to load style previews. Please try again.'
          );
        }
      } finally {
        if (!abortController.signal.aborted) {
          setLoading(false);
        }
      }
    };

    fetchPreviews();

    // Cleanup function to abort request if component unmounts
    return () => {
      abortController.abort();
    };
  }, [resumeId]);

  const handleRetry = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await styleApi.getStylePreviews(resumeId);
      setPreviews(response.previews);
    } catch (err: any) {
      console.error('Error fetching style previews:', err);
      if (err.response?.status === 404) {
        setError('manual-generation-needed');
      } else {
        setError(
          err.response?.data?.detail ||
            'Failed to load style previews. Please try again.'
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const handleStyleSelect = (style: string) => {
    setSelectedStyle(style);
  };

  const handleContinue = async () => {
    if (!selectedStyle) {
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await styleApi.selectStyle(resumeId, selectedStyle);
      onStyleSelected(selectedStyle);
    } catch (err: any) {
      console.error('Error saving style selection:', err);
      setError(
        err.response?.data?.detail ||
          'Failed to save style selection. Please try again.'
      );
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingContainer}>
          <div style={styles.spinner}></div>
          <p style={styles.loadingText}>
            Generating Style Previews...
            <br />
            <small style={{ color: '#999', fontSize: '14px' }}>
              This may take a few seconds
            </small>
          </p>
        </div>
        <style>
          {`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}
        </style>
      </div>
    );
  }

  if (error) {
    if (error === 'manual-generation-needed') {
      return (
        <div style={styles.container}>
          <div style={styles.header}>
            <h1 style={styles.title}>Generate Style Previews</h1>
          </div>
          <div style={{
            ...styles.errorContainer,
            backgroundColor: '#e3f2fd',
            border: '2px solid #2196F3',
            padding: '32px',
            maxWidth: '700px',
            margin: '0 auto',
          }}>
            <h2 style={{ color: '#1976d2', marginBottom: '16px', fontSize: '20px' }}>
              📝 Manual Generation Required
            </h2>
            <p style={{ color: '#333', fontSize: '16px', marginBottom: '16px', lineHeight: '1.6' }}>
              Style previews need to be generated using Claude Code. This uses your existing Claude subscription - no API key needed!
            </p>
            <div style={{ textAlign: 'left', backgroundColor: '#fff', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
              <p style={{ fontWeight: 'bold', marginBottom: '12px', color: '#333' }}>Steps:</p>
              <ol style={{ color: '#555', lineHeight: '1.8', paddingLeft: '20px' }}>
                <li>Go back to your <strong>Claude Code chat</strong></li>
                <li>Say: <code style={{ backgroundColor: '#f5f5f5', padding: '2px 8px', borderRadius: '4px', color: '#d32f2f' }}>"Generate style previews for my latest resume"</code></li>
                <li>Wait ~30 seconds for Claude Code to generate 5 style previews</li>
                <li>Come back here and click <strong>"Check for Previews"</strong></li>
              </ol>
            </div>
            <p style={{ color: '#666', fontSize: '14px', marginBottom: '20px' }}>
              Resume ID: <code style={{ backgroundColor: '#f5f5f5', padding: '4px 8px', borderRadius: '4px' }}>{resumeId}</code>
            </p>
            <button
              onClick={handleRetry}
              style={{
                padding: '14px 32px',
                backgroundColor: '#2196F3',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: 'bold',
                boxShadow: '0 2px 8px rgba(33, 150, 243, 0.3)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#1976d2';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#2196F3';
              }}
            >
              Check for Previews
            </button>
          </div>
        </div>
      );
    }

    return (
      <div style={styles.container}>
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>{error}</p>
          <button
            onClick={handleRetry}
            style={{
              marginTop: '16px',
              padding: '10px 24px',
              backgroundColor: '#3498db',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Choose Your Resume Style</h1>
        <p style={styles.subtitle}>
          Select the writing style that best matches your target role and
          personality. Each preview shows how your Professional Summary would be
          written in that style.
        </p>
      </div>

      <div style={styles.grid}>
        {previews.map((preview) => {
          const isSelected = selectedStyle === preview.style;

          return (
            <StyleCard
              key={preview.style}
              preview={preview}
              isSelected={isSelected}
              onSelect={() => handleStyleSelect(preview.style)}
            />
          );
        })}
      </div>

      {error && (
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>{error}</p>
        </div>
      )}

      <div style={styles.continueContainer}>
        <button
          onClick={handleContinue}
          disabled={!selectedStyle || saving}
          style={{
            ...styles.continueButton,
            ...(!selectedStyle || saving ? styles.continueButtonDisabled : {}),
          }}
          onMouseEnter={(e) => {
            if (selectedStyle && !saving) {
              e.currentTarget.style.backgroundColor = '#2980b9';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(52, 152, 219, 0.4)';
            }
          }}
          onMouseLeave={(e) => {
            if (selectedStyle && !saving) {
              e.currentTarget.style.backgroundColor = '#3498db';
              e.currentTarget.style.boxShadow = '0 2px 8px rgba(52, 152, 219, 0.3)';
            }
          }}
        >
          {saving ? 'Saving...' : 'Continue'}
        </button>
        {!selectedStyle && (
          <p style={{ color: '#999', fontSize: '14px', marginTop: '12px' }}>
            Please select a style to continue
          </p>
        )}
      </div>
    </div>
  );
};

export default StylePreview;
