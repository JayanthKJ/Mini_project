const BASE_URL = 'http://localhost:8000';
const TIMEOUT_MS = 15000;

async function fetchWithTimeout(url, options = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `Server error: ${response.status} ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error('Request timed out. Please check your connection and try again.');
    }
    if (error.message === 'Failed to fetch') {
      throw new Error('Cannot connect to the backend server. Please ensure it is running at ' + BASE_URL);
    }
    throw error;
  }
}

export async function predictAQ(answers) {
  return fetchWithTimeout(`${BASE_URL}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(answers),
  });
}

export async function getModelComparison() {
  return fetchWithTimeout(`${BASE_URL}/model-comparison`);
}

export async function getFeatureImportance() {
  return fetchWithTimeout(`${BASE_URL}/feature-importance`);
}

export async function getCoreDimensions() {
  return fetchWithTimeout(`${BASE_URL}/core-dimensions`);
}

export async function checkHealth() {
  return fetchWithTimeout(`${BASE_URL}/health`);
}
