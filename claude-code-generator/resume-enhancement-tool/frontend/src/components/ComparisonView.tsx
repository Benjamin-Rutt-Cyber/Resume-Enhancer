import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { comparisonApi, analysisApi } from '../services/api';
import { AchievementSuggestions } from './AchievementSuggestions';
import type { ComparisonData, AnalysisResponse } from '../types';

export const ComparisonView: React.FC = () => {
  const { enhancementId } = useParams<{ enhancementId: string }>();
  const [comparison, setComparison] = useState<ComparisonData | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [enhancementId]);

  const loadData = async () => {
    if (!enhancementId) return;

    setLoading(true);
    setError(null);

    try {
      // Load comparison data (required)
      const comparisonData = await comparisonApi.getComparison(enhancementId);
      setComparison(comparisonData);

      // Try to load analysis data (optional - may not exist)
      try {
        const analysisData = await analysisApi.getAnalysis(enhancementId);
        setAnalysis(analysisData);
      } catch (err) {
        // Analysis is optional, so we don't treat this as an error
        console.log('No analysis data available for this enhancement');
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          'Failed to load comparison data. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 70) return '#4CAF50'; // Green
    if (score >= 50) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  const renderMarkdown = (text: string): string => {
    // Simple markdown to HTML conversion
    return text
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^- (.*$)/gim, '<li>$1</li>')
      .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
      .replace(/\n/g, '<br/>');
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingContainer}>
          <h2>Loading comparison...</h2>
        </div>
      </div>
    );
  }

  if (error || !comparison) {
    return (
      <div style={styles.container}>
        <div style={styles.errorContainer}>
          <h2>Error</h2>
          <p>{error || 'Failed to load comparison data'}</p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <h1 style={styles.title}>Resume Comparison</h1>
        {analysis && (
          <div style={styles.scoreContainer}>
            <span style={styles.scoreLabel}>Job Match Score:</span>
            <span
              style={{
                ...styles.scoreBadge,
                backgroundColor: getScoreColor(analysis.job_match_score),
              }}
            >
              {analysis.job_match_score}%
            </span>
          </div>
        )}
      </header>

      {/* Two-column comparison */}
      <div style={styles.comparisonGrid}>
        <div style={styles.column}>
          <h2 style={styles.columnTitle}>Original Resume</h2>
          <div style={styles.textBox}>
            <pre style={styles.preText}>{comparison.original_text}</pre>
          </div>
        </div>

        <div style={styles.column}>
          <h2 style={styles.columnTitle}>Enhanced Resume</h2>
          <div style={styles.textBox}>
            <div
              style={styles.markdownContent}
              dangerouslySetInnerHTML={{ __html: renderMarkdown(comparison.enhanced_text) }}
            />
          </div>
        </div>
      </div>

      {/* ATS Analysis Section */}
      {analysis && (
        <div style={styles.analysisSection}>
          <h2 style={styles.sectionTitle}>ATS Keyword Analysis</h2>

          {/* Keyword Grid */}
          <div style={styles.keywordGrid}>
            <KeywordBox
              title="Keywords Found"
              keywords={analysis.ats_analysis.match_analysis.keywords_found}
              color="green"
              count={analysis.ats_analysis.match_analysis.matched_keywords}
            />
            <KeywordBox
              title="Missing Keywords"
              keywords={analysis.ats_analysis.match_analysis.keywords_missing}
              color="red"
              count={analysis.ats_analysis.match_analysis.missing_keywords}
            />
          </div>

          {/* Recommendations */}
          <div style={styles.recommendationsSection}>
            <h3 style={styles.subsectionTitle}>Recommendations</h3>
            <ul style={styles.recommendationsList}>
              {analysis.ats_analysis.recommendations.map((rec, index) => (
                <li key={index} style={styles.recommendationItem}>
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Achievement Suggestions Section */}
      {enhancementId && (
        <AchievementSuggestions enhancementId={enhancementId} />
      )}
    </div>
  );
};

interface KeywordBoxProps {
  title: string;
  keywords: string[];
  color: 'green' | 'red';
  count: number;
}

const KeywordBox: React.FC<KeywordBoxProps> = ({ title, keywords, color, count }) => {
  const bgColor = color === 'green' ? '#e8f5e9' : '#ffebee';
  const badgeColor = color === 'green' ? '#4CAF50' : '#f44336';
  const borderColor = color === 'green' ? '#81c784' : '#e57373';

  return (
    <div style={{ ...styles.keywordBox, backgroundColor: bgColor, borderColor }}>
      <div style={styles.keywordBoxHeader}>
        <h3 style={styles.keywordBoxTitle}>{title}</h3>
        <span style={{ ...styles.keywordCount, backgroundColor: badgeColor }}>
          {count}
        </span>
      </div>
      <div style={styles.keywordList}>
        {keywords.length === 0 ? (
          <p style={styles.emptyKeywords}>
            {color === 'green' ? 'No matching keywords found' : 'All keywords covered!'}
          </p>
        ) : (
          keywords.map((keyword, index) => (
            <span
              key={index}
              style={{ ...styles.keywordBadge, backgroundColor: badgeColor }}
            >
              {keyword}
            </span>
          ))
        )}
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
    padding: '2rem',
  },
  loadingContainer: {
    textAlign: 'center',
    padding: '4rem',
    backgroundColor: '#fff',
    borderRadius: '8px',
  },
  errorContainer: {
    textAlign: 'center',
    padding: '4rem',
    backgroundColor: '#fff',
    borderRadius: '8px',
    color: '#f44336',
  },
  header: {
    backgroundColor: '#fff',
    padding: '2rem',
    borderRadius: '8px',
    marginBottom: '2rem',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    margin: 0,
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#333',
  },
  scoreContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
  },
  scoreLabel: {
    fontSize: '1.1rem',
    fontWeight: '500',
    color: '#666',
  },
  scoreBadge: {
    padding: '0.5rem 1.5rem',
    borderRadius: '20px',
    color: '#fff',
    fontSize: '1.5rem',
    fontWeight: 'bold',
  },
  comparisonGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '2rem',
    marginBottom: '2rem',
  },
  column: {
    backgroundColor: '#fff',
    borderRadius: '8px',
    padding: '1.5rem',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  columnTitle: {
    margin: '0 0 1rem 0',
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#2196F3',
  },
  textBox: {
    maxHeight: '800px',
    overflowY: 'auto',
    border: '1px solid #e0e0e0',
    borderRadius: '4px',
    padding: '1rem',
    backgroundColor: '#fafafa',
  },
  preText: {
    margin: 0,
    whiteSpace: 'pre-wrap',
    wordWrap: 'break-word',
    fontFamily: 'monospace',
    fontSize: '0.9rem',
    lineHeight: '1.6',
  },
  markdownContent: {
    fontFamily: 'system-ui, -apple-system, sans-serif',
    fontSize: '1rem',
    lineHeight: '1.6',
    color: '#333',
  },
  analysisSection: {
    backgroundColor: '#fff',
    borderRadius: '8px',
    padding: '2rem',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  sectionTitle: {
    margin: '0 0 1.5rem 0',
    fontSize: '1.75rem',
    fontWeight: 'bold',
    color: '#333',
  },
  keywordGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '2rem',
    marginBottom: '2rem',
  },
  keywordBox: {
    border: '2px solid',
    borderRadius: '8px',
    padding: '1.5rem',
  },
  keywordBoxHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem',
  },
  keywordBoxTitle: {
    margin: 0,
    fontSize: '1.25rem',
    fontWeight: 'bold',
    color: '#333',
  },
  keywordCount: {
    padding: '0.25rem 0.75rem',
    borderRadius: '12px',
    color: '#fff',
    fontSize: '1rem',
    fontWeight: 'bold',
  },
  keywordList: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '0.5rem',
  },
  keywordBadge: {
    padding: '0.25rem 0.75rem',
    borderRadius: '12px',
    color: '#fff',
    fontSize: '0.875rem',
    fontWeight: '500',
  },
  emptyKeywords: {
    margin: 0,
    color: '#888',
    fontStyle: 'italic',
  },
  recommendationsSection: {
    borderTop: '1px solid #e0e0e0',
    paddingTop: '2rem',
  },
  subsectionTitle: {
    margin: '0 0 1rem 0',
    fontSize: '1.25rem',
    fontWeight: 'bold',
    color: '#555',
  },
  recommendationsList: {
    listStyleType: 'disc',
    paddingLeft: '1.5rem',
    margin: 0,
  },
  recommendationItem: {
    marginBottom: '0.75rem',
    fontSize: '1rem',
    lineHeight: '1.6',
    color: '#555',
  },
};
