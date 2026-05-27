const DIMENSION_INFO = {
  Control: {
    icon: '🎯',
    color: '#6366f1',
    questions: ['Q1', 'Q5', 'Q9'],
    description: 'Belief in personal influence and problem-solving ability.',
    idealScore: 15,
  },
  Ownership: {
    icon: '🔑',
    color: '#14b8a6',
    questions: ['Q2', 'Q6'],
    description: 'Taking responsibility and learning from mistakes.',
    idealScore: 10,
  },
  Reach: {
    icon: '🌐',
    color: '#f59e0b',
    questions: ['Q3', 'Q7'],
    description: 'Preventing setbacks from affecting all life areas.',
    idealScore: 10,
  },
  Endurance: {
    icon: '⏳',
    color: '#10b981',
    questions: ['Q4', 'Q8', 'Q10'],
    description: 'Belief that problems are temporary and solvable.',
    idealScore: 15,
  },
};

function CoreDimensions({ dimensions, scores }) {
  const dimensionData = dimensions || DIMENSION_INFO;
  const entries = Object.entries(DIMENSION_INFO);

  return (
    <div className="core-section">
      <div className="section-header">
        <h2>🧩 CORE Dimensions</h2>
        <p>Your Adversity Quotient is built on four key dimensions</p>
      </div>
      <div className="dimensions-grid">
        {entries.map(([name, info]) => {
          const score = scores ? scores[name] : null;
          const ideal = info.idealScore;
          const percentage = score != null ? Math.round((score / ideal) * 100) : null;
          const isWeak = percentage != null && percentage < 60;
          const dimClass = name.toLowerCase();

          return (
            <div
              key={name}
              className={`dimension-card ${dimClass}`}
            >
              <div className="dimension-card-header">
                <div className="dimension-name">
                  <span className="dimension-icon">{info.icon}</span>
                  <span className="dimension-title">{name}</span>
                </div>
                {score != null && (
                  <span className="dimension-score-badge">
                    {Number(score).toFixed(2)}/{ideal}
                  </span>
                )}
              </div>

              <p className="dimension-description">{info.description}</p>

              <div className="dimension-questions">
                {info.questions.map(q => (
                  <span key={q} className="dimension-q-tag">{q}</span>
                ))}
              </div>

              {percentage != null && (
                <>
                  <div className="dimension-progress-track">
                    <div
                      className={`dimension-progress-fill ${dimClass}`}
                      style={{ width: `${Math.min(percentage, 100)}%` }}
                    ></div>
                  </div>
                  {isWeak && (
                    <div className="dimension-weak-alert">
                      ⚠️ Needs improvement
                    </div>
                  )}
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default CoreDimensions;
