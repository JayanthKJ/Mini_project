function Header({ activeTab, onTabChange, darkMode, onToggleDarkMode }) {
  const tabs = [
    { id: 'questionnaire', label: 'Questionnaire' },
    { id: 'results', label: 'Results' },
    { id: 'models', label: 'Model Comparison' },
    { id: 'features', label: 'Feature Importance' },
  ];

  return (
    <header className="app-header">
      <div className="header-inner">
        <div className="header-top">
          <div className="header-brand">
            <h1>AQ Prediction System</h1>
            <p>Adversity Quotient Analysis Dashboard</p>
          </div>
          <button
            className="dark-mode-toggle"
            onClick={onToggleDarkMode}
            aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            title={darkMode ? 'Light Mode' : 'Dark Mode'}
            style={{ fontSize: '0.8rem', padding: '0 8px', width: 'auto' }}
          >
            {darkMode ? 'Light' : 'Dark'}
          </button>
        </div>
        <nav className="nav-tabs" role="tablist">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`nav-tab${activeTab === tab.id ? ' active' : ''}`}
              onClick={() => onTabChange(tab.id)}
              role="tab"
              aria-selected={activeTab === tab.id}
              id={`tab-${tab.id}`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
}

export default Header;
