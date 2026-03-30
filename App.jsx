import React, { useState, useEffect, useRef } from 'react';
import './App.css';

export default function ArloDashboard() {
  const [cameras, setCameras] = useState([]);
  const [selectedCamera, setSelectedCamera] = useState(null);
  const [streamUrl, setStreamUrl] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [library, setLibrary] = useState([]);
  const [storageInfo, setStorageInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [alertSettings, setAlertSettings] = useState({
    enabled: true,
    phoneNumber: ''
  });
  const ws = useRef(null);

  const API_BASE = 'http://localhost:8000/api';

  // Initialize dashboard
  useEffect(() => {
    initializeDashboard();
    const interval = setInterval(refreshStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  // Fetch system status
  const initializeDashboard = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/status`);
      const data = await response.json();
      setSystemStatus(data);
      setCameras(data.cameras);
      
      if (data.cameras.length > 0) {
        setSelectedCamera(data.cameras[0]);
      }
      
      await refreshLibrary();
      await refreshStorageInfo();
    } catch (err) {
      setError(`Failed to initialize: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Refresh camera status
  const refreshStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/cameras`);
      const data = await response.json();
      setCameras(data);
      
      if (selectedCamera) {
        const updated = data.find(c => c.id === selectedCamera.id);
        if (updated) setSelectedCamera(updated);
      }
    } catch (err) {
      console.error('Error refreshing status:', err);
    }
  };

  // Get live stream
  const getStream = async (cameraId) => {
    try {
      const response = await fetch(`${API_BASE}/cameras/${cameraId}/stream`);
      const data = await response.json();
      setStreamUrl(data.stream_url);
      
      // Connect to WebSocket
      connectWebSocket(cameraId);
    } catch (err) {
      setError(`Failed to get stream: ${err.message}`);
    }
  };

  // WebSocket connection for real-time updates
  const connectWebSocket = (cameraId) => {
    try {
      ws.current = new WebSocket(`ws://localhost:8000/ws/stream/${cameraId}`);
      
      ws.current.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === 'status_update') {
          setSelectedCamera(prev => ({
            ...prev,
            ...message.data
          }));
        }
      };
      
      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (err) {
      console.error('WebSocket connection failed:', err);
    }
  };

  // Get recorded videos
  const refreshLibrary = async () => {
    try {
      const response = await fetch(`${API_BASE}/library`);
      const data = await response.json();
      setLibrary(data.videos || []);
    } catch (err) {
      console.error('Error getting library:', err);
    }
  };

  // Get storage information
  const refreshStorageInfo = async () => {
    try {
      const response = await fetch(`${API_BASE}/storage-info`);
      const data = await response.json();
      setStorageInfo(data);
    } catch (err) {
      console.error('Error getting storage info:', err);
    }
  };

  // Send test SMS alert
  const sendTestAlert = async () => {
    try {
      const response = await fetch(`${API_BASE}/test-alert?camera_name=${selectedCamera?.name || 'Test'}`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        alert('Test alert SMS sent successfully!');
      } else {
        alert('Failed to send test alert');
      }
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  if (loading) {
    return <div className="loading">Initializing Arlo Dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>🎥 Arlo Camera Management System</h1>
        <div className="header-info">
          <span className="status-badge online">● Connected</span>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="dashboard-grid">
        {/* Left Sidebar - Camera List */}
        <aside className="sidebar">
          <h2>Cameras</h2>
          <div className="camera-list">
            {cameras.map(camera => (
              <div
                key={camera.id}
                className={`camera-item ${selectedCamera?.id === camera.id ? 'active' : ''}`}
                onClick={() => {
                  setSelectedCamera(camera);
                  getStream(camera.id);
                }}
              >
                <div className="camera-name">{camera.name}</div>
                <div className="camera-status">
                  <span className={`status-dot ${camera.status}`}></span>
                  {camera.status}
                </div>
                {camera.battery_level && (
                  <div className="battery">
                    🔋 {camera.battery_level}%
                  </div>
                )}
                {camera.signal_strength && (
                  <div className="signal">
                    📶 {camera.signal_strength} dBm
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Storage Info */}
          <div className="storage-card">
            <h3>💾 Storage</h3>
            {storageInfo && (
              <div className="storage-stats">
                <p><strong>{storageInfo.total_files}</strong> files</p>
                <p><strong>{storageInfo.total_size_gb}</strong> GB</p>
                <p className="path">{storageInfo.path}</p>
              </div>
            )}
          </div>
        </aside>

        {/* Main Content */}
        <main className="main-content">
          {selectedCamera && (
            <>
              {/* Live Stream Section */}
              <section className="live-stream-section">
                <h2>{selectedCamera.name} - Live Stream</h2>
                <div className="stream-container">
                  {streamUrl ? (
                    <iframe
                      src={streamUrl}
                      className="stream-frame"
                      allow="autoplay; fullscreen"
                      title={`${selectedCamera.name} live stream`}
                    ></iframe>
                  ) : (
                    <div className="stream-placeholder">
                      <button onClick={() => getStream(selectedCamera.id)}>
                        ▶ Start Stream
                      </button>
                    </div>
                  )}
                </div>
              </section>

              {/* Camera Info & Controls */}
              <section className="camera-controls">
                <div className="info-grid">
                  <div className="info-card">
                    <h3>📊 Status</h3>
                    <p><strong>Model:</strong> {selectedCamera.model}</p>
                    <p><strong>Status:</strong> {selectedCamera.status}</p>
                    {selectedCamera.battery_level && (
                      <p><strong>Battery:</strong> {selectedCamera.battery_level}%</p>
                    )}
                  </div>

                  <div className="info-card">
                    <h3>🔔 Alerts</h3>
                    <div className="alert-toggle">
                      <label>
                        <input
                          type="checkbox"
                          defaultChecked={alertSettings.enabled}
                          onChange={(e) =>
                            setAlertSettings({ ...alertSettings, enabled: e.target.checked })
                          }
                        />
                        Enable Motion Alerts
                      </label>
                    </div>
                    <button className="btn-primary" onClick={sendTestAlert}>
                      📱 Send Test Alert
                    </button>
                  </div>

                  <div className="info-card">
                    <h3>⚙️ Actions</h3>
                    <button className="btn-secondary" onClick={() => refreshStatus()}>
                      🔄 Refresh Status
                    </button>
                    <button className="btn-secondary" onClick={() => refreshLibrary()}>
                      🎬 Refresh Library
                    </button>
                  </div>
                </div>
              </section>

              {/* Video Library Section */}
              <section className="library-section">
                <h2>📹 Video Library</h2>
                <div className="library-grid">
                  {library.length > 0 ? (
                    library.slice(0, 12).map((video, idx) => (
                      <div key={idx} className="video-item">
                        <div className="video-thumbnail">
                          {video.thumbnail && (
                            <img src={video.thumbnail} alt="Video thumbnail" />
                          )}
                        </div>
                        <div className="video-info">
                          <p className="video-date">
                            {new Date(video.createdAt).toLocaleDateString()}
                          </p>
                          <p className="video-duration">
                            {video.duration ? `${video.duration}s` : 'Unknown'}
                          </p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="no-videos">No recorded videos yet</p>
                  )}
                </div>
              </section>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
