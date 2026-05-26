import { useMemo } from 'react';
import LoadingSpinner from './LoadingSpinner';
import '../styles/FeatureImportance.css';

const QUESTION_LABELS = {
  Q1: 'Influence on academic outcomes',
  Q2: 'Recovery from disappointment',
  Q3: 'Motivation without visible results',
  Q4: "Failures don't define ability",
  Q5: 'Learning from mistakes',
  Q6: 'Control under pressure',
  Q7: 'Problems are temporary',
  Q8: 'Confidence across subjects',
  Q9: 'Taking responsibility',
  Q10: 'Finding ways to overcome',
};

const INSIGHTS = {
  Q1: 'Believing in your ability to influence outcomes is the foundation of personal control.',
  Q2: 'Quick recovery from setbacks signals strong emotional resilience.',
  Q3: 'Sustained motivation without immediate feedback shows deep intrinsic drive.',
  Q4: 'Separating identity from failure enables a growth mindset.',
  Q5: 'Reflective learning from mistakes strongly influences AQ prediction.',
  Q6: 'Maintaining control under pressure demonstrates mature coping strategies.',
  Q7: 'Viewing problems as temporary prevents learned helplessness.',
  Q8: 'Compartmentalizing setbacks prevents negative spiraling across domains.',
  Q9: 'Taking ownership of improvement drives adaptive behavior.',
  Q10: 'Self-efficacy in overcoming challenges is a core resilience indicator.',
};

function FeatureImportance({ data, isLoading }) {
  if (isLoading) {
    return <LoadingSpinner message="Loading feature importance data..." />;
  }

  if (!data || !data.features || data.features.length === 0) {
    return (
      <div className="feature-importance">
        <div className="section-header">
          <h2>🔬 Feature Importance (SHAP Analysis)</h2>
          <p>Understanding which factors most influence AQ prediction</p>
        </div>
        <div className="no-data-message">
          <div className="empty-state-icon">🔍</div>
          <h3>No Feature Data Available</h3>
          <p>Start the backend server to load SHAP feature importance data.</p>
        </div>
      </div>
    );
  }

  const { features } = data;

  // Sort by importance descending
  const sortedFeatures = useMemo(() => {
    return [...features].sort((a, b) => (b.importance || 0) - (a.importance || 0));
  }, [features]);

  const maxImportance = useMemo(() => {
    return Math.max(...sortedFeatures.map(f => f.importance || 0), 0.01);
  }, [sortedFeatures]);

  return (
    <div className="feature-importance">
      <div className="section-header">
        <h2>🔬 Feature Importance (SHAP Analysis)</h2>
        <p>Discover which questions most strongly influence AQ prediction</p>
      </div>

      <div className="importance-chart card">
        <h3>📊 Global Feature Rankings</h3>

        <div className="feature-rows">
          {sortedFeatures.map((feature, idx) => {
            const featureId = feature.feature || feature.name || `Q${idx + 1}`;
            const label = QUESTION_LABELS[featureId] || featureId;
            const importance = feature.importance || 0;
            const barWidth = (importance / maxImportance) * 100;
            const rank = feature.rank || idx + 1;
            const isTop3 = rank <= 3;

            let barClass = 'mid';
            if (rank <= 3) barClass = 'top';
            else if (rank >= 8) barClass = 'low';

            return (
              <div key={featureId} className="feature-row">
                <div className="feature-row-header">
                  <span className={`rank-badge ${isTop3 ? 'top-3' : 'regular'}`}>
                    {rank}
                  </span>
                  <div className="feature-name">
                    <span className="feature-question-id">{featureId}</span>
                    <span className="feature-description"> — {label}</span>
                  </div>
                  <span className="feature-importance-value">
                    {importance.toFixed(4)}
                  </span>
                </div>

                <div className="feature-bar-track">
                  <div
                    className={`feature-bar-fill ${barClass}`}
                    style={{ width: `${barWidth}%` }}
                  ></div>
                </div>

                {isTop3 && INSIGHTS[featureId] && (
                  <div className="insight-card">
                    <strong>💡 Insight:</strong> {INSIGHTS[featureId]}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="chart-legend">
          <div className="legend-item">
            <span className="legend-dot high"></span>
            High Impact
          </div>
          <div className="legend-item">
            <span className="legend-dot medium"></span>
            Medium Impact
          </div>
          <div className="legend-item">
            <span className="legend-dot low"></span>
            Low Impact
          </div>
        </div>
      </div>
    </div>
  );
}

export default FeatureImportance;
