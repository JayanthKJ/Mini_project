function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="loading-container">
      <div className="spinner-modern">
        <div className="spinner-ring"></div>
        <div className="spinner-ring inner"></div>
      </div>
      <p className="loading-text pulse-text">{message}</p>
    </div>
  );
}

export default LoadingSpinner;
