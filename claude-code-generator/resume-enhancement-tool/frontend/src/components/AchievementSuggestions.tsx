import React, { useState, useEffect } from 'react';
import { analysisApi } from '../services/api';
import type { AchievementSuggestionsResponse } from '../types';

interface AchievementSuggestionsProps {
  enhancementId: string;
}

export const AchievementSuggestions: React.FC<AchievementSuggestionsProps> = ({
  enhancementId,
}) => {
  const [suggestions, setSuggestions] = useState<AchievementSuggestionsResponse | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (expanded && !suggestions && !loading) {
      loadSuggestions();
    }
  }, [expanded]);

  const loadSuggestions = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await analysisApi.getAchievementSuggestions(enhancementId);
      setSuggestions(data);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
        'Failed to load achievement suggestions. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  if (!expanded) {
    return (
      <div className="suggestions-trigger">
        <button onClick={() => setExpanded(true)} className="suggestions-btn">
          View Achievement Quantification Suggestions
        </button>
      </div>
    );
  }

  return (
    <div className="suggestions-container">
      <div className="suggestions-header">
        <h3 className="suggestions-title">Achievement Quantification Suggestions</h3>
        <button onClick={() => setExpanded(false)} className="close-btn">
          ✕
        </button>
      </div>

      {loading && (
        <div className="loading-container">
          <p>Loading suggestions...</p>
        </div>
      )}

      {error && (
        <div className="error-container">
          <p>{error}</p>
        </div>
      )}

      {suggestions && !loading && (
        <>
          <div className="suggestions-summary">
            <p className="suggestion-text">{suggestions.summary}</p>
            <div className="stats-bar" style={{ boxShadow: 'none', background: 'transparent', padding: '1rem 0', justifyContent: 'center' }}>
              <div className="suggestion-stat-item">
                <span className="suggestion-stat-number">{suggestions.total_achievements}</span>
                <span className="suggestion-stat-label">Total Achievements</span>
              </div>
              <div className="suggestion-stat-item">
                <span className="suggestion-stat-number">{suggestions.unquantified_count}</span>
                <span className="suggestion-stat-label">Unquantified</span>
              </div>
            </div>
          </div>

          {suggestions.suggestions.length === 0 ? (
            <div className="empty-state">
              <p>Great! All achievements are already quantified.</p>
            </div>
          ) : (
            <div className="suggestions-list">
              {suggestions.suggestions.map((suggestion, index) => (
                <SuggestionCard
                  key={index}
                  achievement={suggestion.achievement}
                  verb={suggestion.verb}
                  location={suggestion.location}
                  suggestedMetrics={suggestion.suggested_metrics}
                  achievementType={suggestion.achievement_type}
                  alreadyQuantified={suggestion.already_quantified}
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};

interface SuggestionCardProps {
  achievement: string;
  verb: string;
  location: string;
  suggestedMetrics: string[];
  achievementType: string;
  alreadyQuantified: boolean;
}

const SuggestionCard: React.FC<SuggestionCardProps> = ({
  achievement,
  verb: _verb,
  location,
  suggestedMetrics,
  achievementType,
  alreadyQuantified,
}) => {
  const getTypeColor = (type: string): string => {
    switch (type) {
      case 'improvement':
        return '#2196F3';
      case 'reduction':
        return '#4CAF50';
      case 'leadership':
        return '#9C27B0';
      case 'development':
        return '#FF9800';
      case 'achievement':
        return '#F44336';
      default:
        return '#757575';
    }
  };

  return (
    <div className="suggestion-card">
      <div className="card-header" style={{ marginBottom: '1rem' }}>
        <span
          className="suggestion-type-badge"
          style={{
            backgroundColor: getTypeColor(achievementType),
          }}
        >
          {achievementType}
        </span>
        <span className="suggestion-location-badge">{location}</span>
      </div>

      <p className="suggestion-text">{achievement}</p>

      <div className="metrics-section">
        <strong className="metrics-label" style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
          Suggested metrics to add:
        </strong>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {suggestedMetrics.map((metric, index) => (
            <li key={index} className="metric-item">
              {metric}
            </li>
          ))}
        </ul>
      </div>

      {alreadyQuantified && (
        <div className="quantified-note">
          ℹ️ This achievement already contains some quantification
        </div>
      )}
    </div>
  );
};
