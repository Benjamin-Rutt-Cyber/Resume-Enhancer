import React, { useState } from 'react';
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

interface StyleCardProps {
  style: StyleOption;
  isSelected: boolean;
  onSelect: () => void;
}

const StyleCard = React.memo<StyleCardProps>(({ style, isSelected, onSelect }) => {
  return (
    <div
      onClick={onSelect}
      className={`style-card ${isSelected ? 'selected' : ''}`}
      role="button"
      tabIndex={0}
      aria-label={`Select ${style.name} writing style`}
      aria-pressed={isSelected}
    >
      <div className="style-name">
        {style.name}
        {isSelected && <span className="style-checkmark">✓</span>}
      </div>

      <p className="style-description">{style.description}</p>

      <div className="style-detail">
        <span className="style-label">Tone:</span> {style.tone}
      </div>

      <div className="style-best-for">
        <span className="style-label">Best for:</span> {style.bestFor}
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
    <div className="style-preview-container">
      <div className="style-preview-header">
        <h1 className="style-preview-title">Choose Your Writing Style</h1>
        <p className="style-preview-subtitle">
          Select the writing style that best matches your target role and industry.
          This style will be applied consistently throughout your enhanced resume.
        </p>
      </div>

      <div className="style-grid">
        {STYLE_OPTIONS.map((style) => (
          <StyleCard
            key={style.id}
            style={style}
            isSelected={selectedStyle === style.id}
            onSelect={() => handleSelectStyle(style.id)}
          />
        ))}
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="continue-container">
        <button
          onClick={handleContinue}
          disabled={!selectedStyle || saving}
          className="continue-btn"
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
