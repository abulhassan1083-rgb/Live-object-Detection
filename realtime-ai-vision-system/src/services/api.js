export async function fetchHealth() {
  const response = await fetch('http://127.0.0.1:8000/api/health');
  if (!response.ok) {
    throw new Error('Backend health check failed');
  }
  return response.json();
}

export async function fetchDetections() {
  const response = await fetch('http://127.0.0.1:8000/api/detections');
  if (!response.ok) {
    throw new Error('Could not fetch detections');
  }
  return response.json();
}
