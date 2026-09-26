export async function fetchHealth() {
  const response = await fetch('http://127.0.0.1:8000/api/health');
  return response.json();
}

export async function fetchDetections() {
  const response = await fetch('http://127.0.0.1:8000/api/detections');
  return response.json();
}
