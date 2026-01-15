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
      <div className="comparison-container">
        <div className="loading-container">
          <h2>Loading comparison...</h2>
        </div>
      </div>
    );
  }

  if (error || !comparison) {
    return (
      <div className="comparison-container">
        <div className="error-container">
          <h2>Error</h2>
          <p>{error || 'Failed to load comparison data'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="comparison-container">
      {/* Header */}
      <header className="comparison-header">
        <h1 className="comparison-title">Resume Comparison</h1>
        {analysis && (
          <div className="score-container">
            <span className="score-label">Job Match Score:</span>
            <span
              className="score-badge-large"
              style={{
                backgroundColor: getScoreColor(analysis.job_match_score),
              }}
            >
              {analysis.job_match_score}%
            </span>
          </div>
        )}
      </header>

      {/* Two-column comparison */}
      <div className="comparison-grid">
        <div className="comparison-column">
          <h2 className="column-title">Original Resume</h2>
          <div className="text-box">
            <pre className="pre-text">{comparison.original_text}</pre>
          </div>
        </div>

        <div className="comparison-column">
          <h2 className="column-title">Enhanced Resume</h2>
          <div className="text-box">
            <div
              className="markdown-content"
              dangerouslySetInnerHTML={{ __html: renderMarkdown(comparison.enhanced_text) }}
            />
          </div>
        </div>
      </div>

      {/* ATS Analysis Section */}
      {analysis && (
        <div className="analysis-section">
          <h2 className="section-title">ATS Keyword Analysis</h2>

          {/* Keyword Grid */}
          <div className="keyword-grid">
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
          <div className="recommendations-section">
            <h3 className="subsection-title">Recommendations</h3>
            <ul className="recommendations-list">
              {analysis.ats_analysis.recommendations.map((rec, index) => (
                <li key={index} className="recommendation-item">
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
  const bgColor = color === 'green' ? 'rgba(76, 175, 80, 0.1)' : 'rgba(244, 67, 54, 0.1)';
  const badgeColor = color === 'green' ? '#4CAF50' : '#f44336';
  const borderColor = color === 'green' ? '#81c784' : '#e57373';

  return (
    <div className="keyword-box" style={{ backgroundColor: bgColor, borderColor: borderColor }}>
      <div className="keyword-box-header">
        <h3 className="keyword-box-title">{title}</h3>
        <span className="keyword-count" style={{ backgroundColor: badgeColor }}>
          {count}
        </span>
      </div>
      <div className="keyword-list">
        {keywords.length === 0 ? (
          <p className="empty-keywords">
            {color === 'green' ? 'No matching keywords found' : 'All keywords covered!'}
          </p>
        ) : (
          keywords.map((keyword, index) => (
            <span
              key={index}
              className="keyword-badge"
              style={{ backgroundColor: badgeColor }}
            >
              {keyword}
            </span>
          ))
        )}
      </div>
    </div>
  );
};
