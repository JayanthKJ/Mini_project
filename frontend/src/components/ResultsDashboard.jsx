import { useMemo } from 'react';
import RecommendationCard from './RecommendationCard';
import CoreDimensions from './CoreDimensions';
import '../styles/ResultsDashboard.css';

function ResultsDashboard({ results, onReset }) {
  const {
    aq_score = 0,
    aq_category = 'Medium',
    confidence = 0,
    core_scores = {},
    weak_dimensions = [],
    behavioral_pattern = '',
    recommendations = [],
    model_predictions = {},
    model_confidences = {},
    feature_importance = [],
  } = results;

  // Category styling
  const categoryClass = useMemo(() => {
    const cat = aq_category.toLowerCase();
    if (cat.includes('high')) return 'high';
    if (cat.includes('low')) return 'low';
    return 'medium';
  }, [aq_category]);

  // Gauge color
  const gaugeColor = useMemo(() => {
    switch (categoryClass) {
      case 'high': return '#10b981';
      case 'low': return '#ef4444';
      default: return '#f59e0b';
    }
  }, [categoryClass]);

  // AQ Score gauge: score is typically 10-50 range
  const maxScore = 50;
  const scorePercent = Math.min(Math.round((aq_score / maxScore) * 100), 100);

  const gaugeStyle = {
    background: `conic-gradient(
      ${gaugeColor} ${scorePercent * 3.6}deg,
      rgba(0,0,0,0.06) ${scorePercent * 3.6}deg
    )`,
    mask: 'radial-gradient(farthest-side, transparent calc(100% - 12px), #fff calc(100% - 11px))',
    WebkitMask: 'radial-gradient(farthest-side, transparent calc(100% - 12px), #fff calc(100% - 11px))',
  };

  // Download JSON
  const handleDownloadJSON = () => {
    const blob = new Blob([JSON.stringify(results, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `aq-analysis-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Print
  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="results-dashboard">
      {/* AQ Overview */}
      <div className="aq-overview card-elevated">
        <div className="aq-gauge">
          <div className="aq-gauge-ring" style={gaugeStyle}></div>
          <div className="aq-gauge-inner">
            <div className="aq-score-value" style={{ color: gaugeColor }}>
              {aq_score}
            </div>
            <div className="aq-score-label">AQ Score</div>
          </div>
        </div>

        <div className="aq-details">
          <div>
            <h2>Your AQ Analysis</h2>
            <span className={`aq-category-badge ${categoryClass}`}>
              {categoryClass === 'high' && '🟢'}
              {categoryClass === 'medium' && '🟡'}
              {categoryClass === 'low' && '🔴'}
              {' '}{aq_category}
            </span>
          </div>

          <div className="confidence-section">
            <span className="confidence-label">
              Model Confidence: <span className="confidence-value">{(confidence * 100).toFixed(1)}%</span>
            </span>
            <div className="confidence-bar-track">
              <div
                className="confidence-bar-fill"
                style={{ width: `${Math.min(confidence * 100, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* CORE Dimensions */}
      {core_scores && Object.keys(core_scores).length > 0 && (
        <CoreDimensions scores={core_scores} />
      )}

      {/* Weak Dimensions */}
      {weak_dimensions && weak_dimensions.length > 0 && (
        <div className="weak-section">
          <div className="section-header">
            <h2>⚠️ Areas for Improvement</h2>
            <p>These dimensions need your attention for growth</p>
          </div>
          <div className="weak-cards">
            {weak_dimensions.map((dim, idx) => (
              <div key={idx} className="weak-card" style={{ animationDelay: `${idx * 0.1}s` }}>
                <div className="weak-card-header">
                  <span className="weak-dimension-name">{dim.dimension}</span>
                  <span className={`severity-badge ${(dim.severity || 'medium').toLowerCase()}`}>
                    {dim.severity || 'Moderate'}
                  </span>
                </div>
                <div className="weak-scores">
                  <div className="weak-score-item">
                    <span className="weak-score-label">Current</span>
                    <span className="weak-score-value current">{dim.current_score}</span>
                  </div>
                  <div className="weak-score-item">
                    <span className="weak-score-label">Target</span>
                    <span className="weak-score-value target">{dim.target_score}</span>
                  </div>
                  <div className="weak-score-item">
                    <span className="weak-score-label">Gap</span>
                    <span className="weak-score-value improvement">+{dim.improvement_needed}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Behavioral Pattern */}
      {behavioral_pattern && (
        <div className="pattern-section">
          <div className="section-header">
            <h2>🧠 Behavioral Pattern</h2>
            <p>Your resilience and personality interpretation</p>
          </div>
          <div className="pattern-card">
            <p className="pattern-text">{behavioral_pattern}</p>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="recommendations-section">
          <div className="section-header">
            <h2>💡 Personalized Recommendations</h2>
            <p>Actionable steps to improve your Adversity Quotient</p>
          </div>
          <div className="recommendations-grid">
            {recommendations.map((rec, idx) => (
              <RecommendationCard
                key={idx}
                recommendation={rec}
              />
            ))}
          </div>
        </div>
      )}

      {/* Export Options */}
      <div className="export-section">
        <button className="btn btn-secondary" onClick={handlePrint}>
          🖨️ Print Results
        </button>
        <button className="btn btn-secondary" onClick={handleDownloadJSON}>
          📥 Download JSON
        </button>
      </div>

      {/* Reset */}
      <div className="reset-section">
        <button className="btn btn-primary btn-lg" onClick={onReset}>
          🔄 Take Another Assessment
        </button>
      </div>
    </div>
  );
}

export default ResultsDashboard;
