import { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import QuestionnaireForm from './components/QuestionnaireForm';
import ResultsDashboard from './components/ResultsDashboard';
import ModelComparison from './components/ModelComparison';
import FeatureImportance from './components/FeatureImportance';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorAlert from './components/ErrorAlert';
import {
  predictAQ,
  getModelComparison,
  getFeatureImportance,
  getCoreDimensions,
  checkHealth,
} from './api/service';
import './styles/App.css';
import './styles/DarkMode.css';

function App() {
  // Theme
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('aq-dark-mode');
    return saved ? JSON.parse(saved) : false;
  });

  // Navigation
  const [activeTab, setActiveTab] = useState('questionnaire');

  // Data states
  const [results, setResults] = useState(null);
  const [modelData, setModelData] = useState(null);
  const [featureData, setFeatureData] = useState(null);
  const [dimensionData, setDimensionData] = useState(null);

  // UI states
  const [isLoading, setIsLoading] = useState(false);
  const [isPageLoading, setIsPageLoading] = useState(true);
  const [error, setError] = useState(null);
  const [backendOnline, setBackendOnline] = useState(false);

  // Apply dark mode
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
    localStorage.setItem('aq-dark-mode', JSON.stringify(darkMode));
  }, [darkMode]);

  // Load initial data on mount
  useEffect(() => {
    async function loadInitialData() {
      setIsPageLoading(true);
      try {
        const healthResult = await checkHealth();
        setBackendOnline(true);

        const [dimensions, models, features] = await Promise.allSettled([
          getCoreDimensions(),
          getModelComparison(),
          getFeatureImportance(),
        ]);

        if (dimensions.status === 'fulfilled') setDimensionData(dimensions.value);
        if (models.status === 'fulfilled') setModelData(models.value);
        if (features.status === 'fulfilled') setFeatureData(features.value);
      } catch (err) {
        setBackendOnline(false);
        console.warn('Backend not available:', err.message);
      } finally {
        setIsPageLoading(false);
      }
    }

    loadInitialData();
  }, []);

  // Handle prediction
  const handlePredict = useCallback(async (answers) => {
    setIsLoading(true);
    setError(null);

    try {
      const prediction = await predictAQ(answers);
      setResults(prediction);
      setActiveTab('results');

      // Also refresh feature importance if included in response
      if (prediction.feature_importance) {
        setFeatureData(prev => prev || { features: prediction.feature_importance });
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Handle reset
  const handleReset = useCallback(() => {
    setResults(null);
    setActiveTab('questionnaire');
    setError(null);
  }, []);

  // Toggle dark mode
  const handleToggleDarkMode = useCallback(() => {
    setDarkMode(prev => !prev);
  }, []);

  // Dismiss error
  const handleDismissError = useCallback(() => {
    setError(null);
  }, []);

  // Retry loading data
  const handleRetry = useCallback(async () => {
    setError(null);
    setIsPageLoading(true);
    try {
      await checkHealth();
      setBackendOnline(true);
      const [dimensions, models, features] = await Promise.allSettled([
        getCoreDimensions(),
        getModelComparison(),
        getFeatureImportance(),
      ]);
      if (dimensions.status === 'fulfilled') setDimensionData(dimensions.value);
      if (models.status === 'fulfilled') setModelData(models.value);
      if (features.status === 'fulfilled') setFeatureData(features.value);
    } catch (err) {
      setBackendOnline(false);
      setError('Cannot connect to backend server. Please ensure it is running.');
    } finally {
      setIsPageLoading(false);
    }
  }, []);

  // Render active tab content
  const renderTabContent = () => {
    switch (activeTab) {
      case 'questionnaire':
        return (
          <QuestionnaireForm
            onSubmit={handlePredict}
            isLoading={isLoading}
          />
        );

      case 'results':
        if (!results) {
          return (
            <div className="empty-state">
              <div className="empty-state-icon">📊</div>
              <h2>No Results Yet</h2>
              <p>Complete the questionnaire to see your AQ analysis.</p>
              <button
                className="btn btn-primary"
                onClick={() => setActiveTab('questionnaire')}
              >
                Take the Assessment
              </button>
            </div>
          );
        }
        return (
          <ResultsDashboard
            results={results}
            onReset={handleReset}
          />
        );

      case 'models':
        return (
          <ModelComparison
            data={modelData}
            isLoading={isPageLoading && !modelData}
          />
        );

      case 'features':
        return (
          <FeatureImportance
            data={featureData}
            isLoading={isPageLoading && !featureData}
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className="app">
      <Header
        activeTab={activeTab}
        onTabChange={setActiveTab}
        darkMode={darkMode}
        onToggleDarkMode={handleToggleDarkMode}
      />

      <main className="main-content">
        {/* Backend status indicator */}
        {!isPageLoading && !backendOnline && (
          <div className="backend-status offline">
            <span className="status-dot"></span>
            Backend Offline — Start your FastAPI server at localhost:8000
            <button className="btn btn-ghost btn-sm" onClick={handleRetry}>
              Retry Connection
            </button>
          </div>
        )}

        {!isPageLoading && backendOnline && (
          <div className="backend-status online">
            <span className="status-dot"></span>
            Backend Connected
          </div>
        )}

        {/* Error alert */}
        {error && (
          <ErrorAlert
            message={error}
            onRetry={activeTab === 'questionnaire' ? null : handleRetry}
            onDismiss={handleDismissError}
          />
        )}

        {/* Page loading state */}
        {isPageLoading ? (
          <LoadingSpinner message="Connecting to backend..." />
        ) : (
          <div className="tab-content fade-in">
            {renderTabContent()}
          </div>
        )}
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <p>AQ Prediction System — Research-based Adversity Quotient Analysis</p>
          <p className="footer-note">
            No data is stored or collected. All processing is temporary and ephemeral.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
