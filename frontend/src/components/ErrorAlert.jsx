function ErrorAlert({ message, onRetry, onDismiss }) {
  return (
    <div className="error-alert" role="alert">
      <span className="error-alert-icon">⚠️</span>
      <div className="error-alert-content">
        <p className="error-alert-message">{message}</p>
        <div className="error-alert-actions">
          {onRetry && (
            <button className="btn btn-ghost btn-sm" onClick={onRetry}>
              🔄 Retry
            </button>
          )}
        </div>
      </div>
      {onDismiss && (
        <button
          className="error-alert-dismiss"
          onClick={onDismiss}
          aria-label="Dismiss error"
        >
          ✕
        </button>
      )}
    </div>
  );
}

export default ErrorAlert;
