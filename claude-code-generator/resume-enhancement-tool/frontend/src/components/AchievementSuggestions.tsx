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
      <div style={styles.collapsedContainer}>
        <button onClick={() => setExpanded(true)} style={styles.expandButton}>
          View Achievement Quantification Suggestions
        </button>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>Achievement Quantification Suggestions</h3>
        <button onClick={() => setExpanded(false)} style={styles.closeButton}>
          ✕
        </button>
      </div>

      {loading && (
        <div style={styles.loadingContainer}>
          <p>Loading suggestions...</p>
        </div>
      )}

      {error && (
        <div style={styles.errorContainer}>
          <p>{error}</p>
        </div>
      )}

      {suggestions && !loading && (
        <>
          <div style={styles.summary}>
            <p style={styles.summaryText}>{suggestions.summary}</p>
            <div style={styles.stats}>
              <div style={styles.statItem}>
                <span style={styles.statNumber}>{suggestions.total_achievements}</span>
                <span style={styles.statLabel}>Total Achievements</span>
              </div>
              <div style={styles.statItem}>
                <span style={styles.statNumber}>{suggestions.unquantified_count}</span>
                <span style={styles.statLabel}>Unquantified</span>
              </div>
            </div>
          </div>

          {suggestions.suggestions.length === 0 ? (
            <div style={styles.emptyState}>
              <p>Great! All achievements are already quantified.</p>
            </div>
          ) : (
            <div style={styles.suggestionsList}>
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
    <div style={styles.suggestionCard}>
      <div style={styles.cardHeader}>
        <span
          style={{
            ...styles.typeBadge,
            backgroundColor: getTypeColor(achievementType),
          }}
        >
          {achievementType}
        </span>
        <span style={styles.locationBadge}>{location}</span>
      </div>

      <p style={styles.achievementText}>{achievement}</p>

      <div style={styles.metricsSection}>
        <strong style={styles.metricsLabel}>Suggested metrics to add:</strong>
        <ul style={styles.metricsList}>
          {suggestedMetrics.map((metric, index) => (
            <li key={index} style={styles.metricItem}>
              {metric}
            </li>
          ))}
        </ul>
      </div>

      {alreadyQuantified && (
        <div style={styles.quantifiedNote}>
          ℹ️ This achievement already contains some quantification
        </div>
      )}
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  collapsedContainer: {
    marginTop: '2rem',
    textAlign: 'center',
  },
  expandButton: {
    padding: '0.75rem 1.5rem',
    fontSize: '1rem',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#2196F3',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  container: {
    marginTop: '2rem',
    backgroundColor: '#fff',
    borderRadius: '8px',
    padding: '2rem',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1.5rem',
  },
  title: {
    margin: 0,
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#333',
  },
  closeButton: {
    width: '32px',
    height: '32px',
    backgroundColor: '#f5f5f5',
    border: 'none',
    borderRadius: '50%',
    fontSize: '20px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#666',
    transition: 'background-color 0.2s',
  },
  loadingContainer: {
    textAlign: 'center',
    padding: '2rem',
    color: '#666',
  },
  errorContainer: {
    textAlign: 'center',
    padding: '2rem',
    color: '#f44336',
    backgroundColor: '#ffebee',
    borderRadius: '4px',
  },
  summary: {
    marginBottom: '2rem',
    padding: '1.5rem',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px',
    borderLeft: '4px solid #2196F3',
  },
  summaryText: {
    margin: '0 0 1rem 0',
    fontSize: '1rem',
    lineHeight: '1.6',
    color: '#555',
  },
  stats: {
    display: 'flex',
    gap: '2rem',
  },
  statItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  statNumber: {
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#2196F3',
  },
  statLabel: {
    fontSize: '0.875rem',
    color: '#888',
    marginTop: '0.25rem',
  },
  emptyState: {
    textAlign: 'center',
    padding: '2rem',
    color: '#4CAF50',
    fontSize: '1.1rem',
    backgroundColor: '#e8f5e9',
    borderRadius: '8px',
  },
  suggestionsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  suggestionCard: {
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    padding: '1.5rem',
    backgroundColor: '#fafafa',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem',
  },
  typeBadge: {
    padding: '0.25rem 0.75rem',
    borderRadius: '12px',
    color: '#fff',
    fontSize: '0.875rem',
    fontWeight: '500',
    textTransform: 'capitalize',
  },
  locationBadge: {
    padding: '0.25rem 0.75rem',
    borderRadius: '12px',
    backgroundColor: '#e0e0e0',
    color: '#555',
    fontSize: '0.875rem',
    fontWeight: '500',
  },
  achievementText: {
    margin: '0 0 1rem 0',
    fontSize: '1rem',
    lineHeight: '1.6',
    color: '#333',
    padding: '0.75rem',
    backgroundColor: '#fff',
    borderRadius: '4px',
    border: '1px solid #e0e0e0',
  },
  metricsSection: {
    marginTop: '1rem',
  },
  metricsLabel: {
    fontSize: '0.95rem',
    color: '#555',
  },
  metricsList: {
    listStyleType: 'none',
    padding: 0,
    margin: '0.5rem 0 0 0',
  },
  metricItem: {
    padding: '0.5rem 0.75rem',
    marginBottom: '0.5rem',
    backgroundColor: '#e3f2fd',
    borderRadius: '4px',
    color: '#1976d2',
    fontSize: '0.9rem',
    borderLeft: '3px solid #2196F3',
  },
  quantifiedNote: {
    marginTop: '1rem',
    padding: '0.75rem',
    backgroundColor: '#fff3e0',
    borderRadius: '4px',
    color: '#f57c00',
    fontSize: '0.875rem',
  },
};
