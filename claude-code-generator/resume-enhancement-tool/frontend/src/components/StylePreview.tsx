import React, { useState, useMemo } from 'react';
import { styleApi } from '../services/api';

interface StylePreviewProps {
  resumeId: string;
  onStyleSelected: (style: string) => void;
  onClose?: () => void;
}

interface StyleOption {
  id: string;
  name: string;
  description: string;
  tone: string;
  bestFor: string;
}

// Static style options - no API call needed
const STYLE_OPTIONS: StyleOption[] = [
  {
    id: 'professional',
    name: 'Professional',
    description: 'Traditional corporate tone with formal language',
    tone: 'Formal, corporate, traditional',
    bestFor: 'Corporate jobs, traditional industries (Banking, Healthcare, Government)'
  },
  {
    id: 'executive',
    name: 'Executive',
    description: 'Senior leadership language with strategic focus',
    tone: 'Authoritative, strategic, refined',
    bestFor: 'Leadership roles, management positions, C-suite applications'
  },
  {
    id: 'technical',
    name: 'Technical',
    description: 'Detailed technical terminology with specific metrics',
    tone: 'Precise, technical, data-driven',
    bestFor: 'Engineering roles, technical specialist positions, data-driven companies'
  },
  {
    id: 'creative',
    name: 'Creative',
    description: 'Dynamic personality-focused with engaging language',
    tone: 'Engaging, personality-driven, dynamic',
    bestFor: 'Startups, tech companies, innovative organizations, marketing/design roles'
  },
  {
    id: 'concise',
    name: 'Concise',
    description: 'Brief impactful statements in scannable format',
    tone: 'Brief, impactful, scannable',
    bestFor: 'Senior roles where brevity matters, executive-level positions'
  }
];

// Move styles outside component
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
    maxWidth: '700px',
    margin: '0 auto',
    lineHeight: '1.6',
  } as React.CSSProperties,
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
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
  description: {
    fontSize: '15px',
    color: '#555',
    marginBottom: '12px',
    lineHeight: '1.5',
  } as React.CSSProperties,
  detail: {
    fontSize: '13px',
    color: '#666',
    marginBottom: '8px',
    lineHeight: '1.4',
  } as React.CSSProperties,
  label: {
    fontWeight: '600',
    color: '#444',
  } as React.CSSProperties,
  bestFor: {
    backgroundColor: '#f8f9fa',
    padding: '12px',
    borderRadius: '6px',
    fontSize: '13px',
    color: '#495057',
    marginTop: '12px',
    lineHeight: '1.5',
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
  errorText: {
    color: '#c33',
    textAlign: 'center' as const,
    padding: '20px',
    fontSize: '16px',
  } as React.CSSProperties,
};

interface StyleCardProps {
  style: StyleOption;
  isSelected: boolean;
  onSelect: () => void;
}

const StyleCard = React.memo<StyleCardProps>(({ style, isSelected, onSelect }) => {
  const [isHovered, setIsHovered] = useState(false);

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
      role="button"
      tabIndex={0}
      aria-label={`Select ${style.name} writing style`}
      aria-pressed={isSelected}
    >
      <div style={styles.styleName}>
        {style.name}
        {isSelected && <span style={styles.checkmark}>✓</span>}
      </div>

      <p style={styles.description}>{style.description}</p>

      <div style={styles.detail}>
        <span style={styles.label}>Tone:</span> {style.tone}
      </div>

      <div style={styles.bestFor}>
        <span style={styles.label}>Best for:</span> {style.bestFor}
      </div>
    </div>
  );
});

StyleCard.displayName = 'StyleCard';

const StylePreview: React.FC<StylePreviewProps> = ({ resumeId, onStyleSelected }) => {
  const [selectedStyle, setSelectedStyle] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSelectStyle = (styleId: string) => {
    setSelectedStyle(styleId);
    setError(null);
  };

  const handleContinue = async () => {
    if (!selectedStyle) {
      setError('Please select a writing style');
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
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Choose Your Writing Style</h1>
        <p style={styles.subtitle}>
          Select the writing style that best matches your target role and industry.
          This style will be applied consistently throughout your enhanced resume.
        </p>
      </div>

      <div style={styles.grid}>
        {STYLE_OPTIONS.map((style) => (
          <StyleCard
            key={style.id}
            style={style}
            isSelected={selectedStyle === style.id}
            onSelect={() => handleSelectStyle(style.id)}
          />
        ))}
      </div>

      {error && <div style={styles.errorText}>{error}</div>}

      <div style={styles.continueContainer}>
        <button
          onClick={handleContinue}
          disabled={!selectedStyle || saving}
          style={{
            ...styles.continueButton,
            ...((!selectedStyle || saving) ? styles.continueButtonDisabled : {}),
          }}
          aria-label="Continue with selected style"
          aria-busy={saving}
        >
          {saving ? 'Saving...' : 'Continue with Selected Style'}
        </button>
      </div>
    </div>
  );
};

export default StylePreview;
