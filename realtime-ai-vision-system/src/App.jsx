import { useEffect, useRef, useState } from 'react';
import { fetchHealth } from './services/api';

const DETECTION_INTERVAL_MS = 200;

function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const socketRef = useRef(null);
  const detectionTimerRef = useRef(null);
  const [backendStatus, setBackendStatus] = useState('CHECKING BACKEND...');
  const [cameraStatus, setCameraStatus] = useState('CAMERA STOPPED');
  const [websocketStatus, setWebsocketStatus] = useState('WEBSOCKET DISCONNECTED');
  const [aiStatus, setAiStatus] = useState('AI DETECTION OFFLINE');
  const [detections, setDetections] = useState([]);
  const [selectedObject, setSelectedObject] = useState(null);
  const [question, setQuestion] = useState('What is this used for?');
  const [aiAnswer, setAiAnswer] = useState('The AI answer will update from the current camera frame.');
  const [currentFrame, setCurrentFrame] = useState('');

  const normalizeName = (value) => value ? value.toUpperCase() : 'NO OBJECT DETECTED';

  useEffect(() => {
    const loadBackendStatus = async () => {
      try {
        const health = await fetchHealth();
        setBackendStatus(health.status === 'ok' ? 'SYSTEM ONLINE' : 'SYSTEM OFFLINE');
      } catch (error) {
        setBackendStatus('SYSTEM OFFLINE');
      }
    };

    loadBackendStatus();
    connectWebSocket();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
      if (detectionTimerRef.current) {
        clearInterval(detectionTimerRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const socket = new WebSocket('ws://127.0.0.1:8000/ws');
      socketRef.current = socket;

      socket.onopen = () => {
        setWebsocketStatus('WEBSOCKET CONNECTED');
        setAiStatus('AI DETECTION ACTIVE');
      };

      socket.onclose = () => {
        setWebsocketStatus('RECONNECTING...');
        setAiStatus('AI DETECTION OFFLINE');
        setTimeout(connectWebSocket, 1500);
      };

      socket.onerror = () => {
        setWebsocketStatus('RECONNECTING...');
        setAiStatus('AI DETECTION OFFLINE');
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'detections' && Array.isArray(payload.detections)) {
            const nextDetections = payload.detections
              .filter((item) => item && item.class_name)
              .sort((a, b) => (b.confidence || 0) - (a.confidence || 0));

            setDetections(nextDetections);
            setSelectedObject(nextDetections[0] || null);
            if (nextDetections.length === 0) {
              setAiAnswer('No reliable object detected in the current frame.');
            }
          }
        } catch (error) {
          console.error('WebSocket message parse error:', error);
        }
      };
    } catch (error) {
      console.error('WebSocket setup error:', error);
      setWebsocketStatus('RECONNECTING...');
    }
  };

  const startCamera = async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setCameraStatus('CAMERA UNAVAILABLE');
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user' },
        audio: false,
      });

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }

      setCameraStatus('CAMERA ACTIVE');
      setAiStatus('AI DETECTION ACTIVE');

      if (detectionTimerRef.current) {
        clearInterval(detectionTimerRef.current);
      }

      detectionTimerRef.current = setInterval(() => {
        if (!videoRef.current || !socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
          return;
        }

        const video = videoRef.current;
        const canvas = canvasRef.current || document.createElement('canvas');
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        const context = canvas.getContext('2d');
        if (!context) {
          return;
        }

        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        setCurrentFrame(imageData);

        socketRef.current.send(JSON.stringify({ image: imageData }));
      }, DETECTION_INTERVAL_MS);
    } catch (error) {
      setCameraStatus('CAMERA UNAVAILABLE');
      setAiStatus('AI MODEL OFFLINE');
      console.error('Camera access error:', error);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    if (detectionTimerRef.current) {
      clearInterval(detectionTimerRef.current);
      detectionTimerRef.current = null;
    }
    setCameraStatus('CAMERA STOPPED');
    setAiStatus('AI DETECTION OFFLINE');
  };

  const selectedDetection = selectedObject || detections[0] || null;
  const currentLabel = selectedDetection ? normalizeName(selectedDetection.class_name) : 'NO OBJECT DETECTED';
  const currentConfidence = selectedDetection ? `${((selectedDetection.confidence || 0) * 100).toFixed(1)}%` : '0%';
  const currentMaterial = selectedDetection?.material || 'Unknown';

  const askAi = async () => {
    if (!selectedDetection) {
      setAiAnswer('Unable to determine this from the current image. No reliable object is currently visible.');
      return;
    }

    try {
      const currentQuestion = question.trim();
      const response = await fetch('http://127.0.0.1:8000/api/questions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image: currentFrame,
          object_name: selectedDetection.class_name,
          material: currentMaterial,
          question: currentQuestion,
        }),
      });

      if (!response.ok) {
        throw new Error('AI request failed');
      }

      const data = await response.json();
      setAiAnswer(data.answer || 'Unable to determine this from the current image.');
    } catch (error) {
      setAiAnswer('Unable to determine this from the current image.');
      console.error('AI request error:', error);
    }
  };

  const overlayBoxes = detections.length > 0 ? detections.map((item, index) => {
    const { x1, y1, x2, y2 } = item.bbox || {};
    const width = (x2 || 0) - (x1 || 0);
    const height = (y2 || 0) - (y1 || 0);

    if (!x1 || !y1 || width <= 0 || height <= 0) {
      return null;
    }

    const y = Number(y1 || 0);
    const x = Number(x1 || 0);

    return (
      <div key={`${item.class_name}-${index}`} className="detection-box-wrap" style={{ left: `${x}px`, top: `${y}px`, width: `${width}px`, height: `${height}px` }}>
        <div className="detection-box" />
        <div className="label-tag">
          <span>{normalizeName(item.class_name)}</span>
          <strong>{((item.confidence || 0) * 100).toFixed(1)}%</strong>
        </div>
      </div>
    );
  }) : null;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">AI VISION SYSTEM</p>
          <h1>Real-Time AI Vision</h1>
        </div>
        <div className="status-pill">
          <span className="status-dot" />
          {backendStatus}
        </div>
      </header>

      <main className="dashboard-layout">
        <section className="camera-panel panel">
          <div className="camera-header">
            <span>LIVE ● CAMERA</span>
            <div className="controls">
              <button type="button" onClick={startCamera}>Start</button>
              <button type="button" className="secondary" onClick={stopCamera}>Pause</button>
            </div>
          </div>

          <div className="camera-feed">
            <video ref={videoRef} className="camera-video" autoPlay muted playsInline />
            {!streamRef.current && <div className="camera-placeholder">Camera preview will appear here.</div>}
            <div className="overlay-layer">{overlayBoxes}</div>
            <div className="scan-lines" />
            <div className="camera-overlay">
              <div className="object-badge">{currentLabel}</div>
            </div>
          </div>

          <div className="camera-status-bar">
            <span>{cameraStatus}</span>
            <span>{websocketStatus}</span>
            <span>{aiStatus}</span>
          </div>
        </section>

        <aside className="info-panel panel">
          <div className="info-block">
            <p className="section-label">Detected Object</p>
            <h2>{currentLabel}</h2>
          </div>

          <div className="metrics-grid">
            <div className="metric-card">
              <span>Confidence</span>
              <strong>{currentConfidence}</strong>
            </div>
            <div className="metric-card">
              <span>Material</span>
              <strong>{currentMaterial}</strong>
            </div>
          </div>

          <div className="question-card">
            <p className="section-label">Ask AI</p>
            <textarea
              rows="4"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />
            <button type="button" className="primary-btn" onClick={askAi}>Ask Question</button>
          </div>

          <div className="answer-card">
            <p className="section-label">AI Response</p>
            <p>{aiAnswer}</p>
          </div>

          <div className="detection-list">
            <p className="section-label">Detected Objects</p>
            {detections.length === 0 ? (
              <p className="muted">NO OBJECT DETECTED</p>
            ) : (
              <ul>
                {detections.map((item, index) => (
                  <li key={`${item.class_name}-${index}`}>
                    <button type="button" className={selectedDetection && selectedDetection.class_name === item.class_name ? 'active' : ''} onClick={() => setSelectedObject(item)}>
                      {normalizeName(item.class_name)} {((item.confidence || 0) * 100).toFixed(1)}%
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </aside>
      </main>

      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </div>
  );
}

export default App;
