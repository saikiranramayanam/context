import React, { useState } from 'react';
import { Settings, Plus, Camera } from 'lucide-react';
import CameraCard from '../CameraCard';

const API_BASE = 'http://localhost:8000/api';

const SystemSettingsTab = ({ cameras, fetchCameras, fetchStats, onToggleActive, onDeleteCamera }) => {
  // Form states
  const [camName, setCamName] = useState('');
  const [camSource, setCamSource] = useState('');
  const [camIsActive, setCamIsActive] = useState(true);
  const [camThreshold, setCamThreshold] = useState(70);
  const [camMinX, setCamMinX] = useState(0.0);
  const [camMinY, setCamMinY] = useState(0.0);
  const [camMaxX, setCamMaxX] = useState(1.0);
  const [camMaxY, setCamMaxY] = useState(1.0);
  const [editingCameraId, setEditingCameraId] = useState(null);

  // Set camera for editing
  const handleEditCamera = (camera) => {
    setCamName(camera.name);
    setCamSource(camera.source);
    setCamIsActive(camera.is_active);
    setCamThreshold(camera.threshold !== undefined ? camera.threshold : 70);
    setCamMinX(camera.zone_min_x !== undefined ? camera.zone_min_x : 0.0);
    setCamMinY(camera.zone_min_y !== undefined ? camera.zone_min_y : 0.0);
    setCamMaxX(camera.zone_max_x !== undefined ? camera.zone_max_x : 1.0);
    setCamMaxY(camera.zone_max_y !== undefined ? camera.zone_max_y : 1.0);
    setEditingCameraId(camera.id);
  };

  // Cancel edit mode
  const handleCancelEdit = () => {
    setCamName('');
    setCamSource('');
    setCamIsActive(true);
    setCamThreshold(70);
    setCamMinX(0.0);
    setCamMinY(0.0);
    setCamMaxX(1.0);
    setCamMaxY(1.0);
    setEditingCameraId(null);
  };

  // Form submission (Add/Update camera)
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!camName || !camSource) return;

    const payload = {
      name: camName,
      source: camSource,
      is_active: camIsActive,
      threshold: parseFloat(camThreshold),
      zone_min_x: parseFloat(camMinX),
      zone_min_y: parseFloat(camMinY),
      zone_max_x: parseFloat(camMaxX),
      zone_max_y: parseFloat(camMaxY)
    };

    try {
      let res;
      if (editingCameraId) {
        res = await fetch(`${API_BASE}/cameras/${editingCameraId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } else {
        res = await fetch(`${API_BASE}/cameras`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      }

      if (res.ok) {
        // Reset form
        handleCancelEdit();
        fetchCameras();
        fetchStats();
      }
    } catch (e) {
      console.error('Error saving camera feed config:', e);
    }
  };

  return (
    <div className="settings-layout">
      {/* Form column */}
      <div className="settings-card">
        <h3 className="form-title">
          <Settings size={18} style={{ color: 'var(--primary-light)' }} />
          {editingCameraId ? 'Modify Calibration Parameters' : 'Register Stream Node'}
        </h3>
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className="form-group">
            <label>Node Identification (Name)</label>
            <input 
              type="text" 
              className="cyber-input" 
              placeholder="e.g. Forklift Lane West" 
              value={camName}
              onChange={(e) => setCamName(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Video Connection Source (Webcam ID / RTSP / MP4 Path)</label>
            <input 
              type="text" 
              className="cyber-input" 
              placeholder="e.g. 0 or rtsp://ip/stream or data/video.mp4" 
              value={camSource}
              onChange={(e) => setCamSource(e.target.value)}
            />
          </div>

          {/* Threshold sensitivity */}
          <div className="slider-group">
            <div className="slider-header">
              <span className="slider-title">Threat Threshold Sensitivity</span>
              <span className="slider-value">{camThreshold}%</span>
            </div>
            <input 
              type="range" 
              min="40" 
              max="90" 
              step="5"
              className="slider-control"
              value={camThreshold}
              onChange={(e) => setCamThreshold(parseInt(e.target.value))}
            />
            <div className="slider-footer">
              <span>High Sensitivity (40%)</span>
              <span>Low Sensitivity (90%)</span>
            </div>
          </div>

          {/* Active zone boundary sliders */}
          <div className="form-group">
            <label>Active Monitoring Zone Boundary (Hot Zone)</label>
            <div className="zone-calibrator">
              <div className="zone-sliders">
                <div className="zone-slider-item">
                  <span className="zone-slider-label">MIN X: {camMinX.toFixed(2)}</span>
                  <input 
                    type="range" min="0.0" max="0.5" step="0.05" className="slider-control"
                    value={camMinX} onChange={(e) => setCamMinX(parseFloat(e.target.value))}
                  />
                </div>
                <div className="zone-slider-item">
                  <span className="zone-slider-label">MAX X: {camMaxX.toFixed(2)}</span>
                  <input 
                    type="range" min="0.5" max="1.0" step="0.05" className="slider-control"
                    value={camMaxX} onChange={(e) => setCamMaxX(parseFloat(e.target.value))}
                  />
                </div>
                <div className="zone-slider-item">
                  <span className="zone-slider-label">MIN Y: {camMinY.toFixed(2)}</span>
                  <input 
                    type="range" min="0.0" max="0.5" step="0.05" className="slider-control"
                    value={camMinY} onChange={(e) => setCamMinY(parseFloat(e.target.value))}
                  />
                </div>
                <div className="zone-slider-item">
                  <span className="zone-slider-label">MAX Y: {camMaxY.toFixed(2)}</span>
                  <input 
                    type="range" min="0.5" max="1.0" step="0.05" className="slider-control"
                    value={camMaxY} onChange={(e) => setCamMaxY(parseFloat(e.target.value))}
                  />
                </div>
              </div>

              {/* Hot zone active preview visualizer */}
              <div className="zone-preview-box">
                <div 
                  className="zone-active-overlay"
                  style={{
                    left: `${camMinX * 100}%`,
                    top: `${camMinY * 100}%`,
                    width: `${(camMaxX - camMinX) * 100}%`,
                    height: `${(camMaxY - camMinY) * 100}%`
                  }}
                ></div>
                <span className="zone-preview-text">MONITOR AREA</span>
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', cursor: 'pointer' }}>
              <input 
                type="checkbox" 
                checked={camIsActive}
                onChange={(e) => setCamIsActive(e.target.checked)}
                style={{ accentColor: 'var(--primary)' }}
              />
              Initialize active
            </label>
            
            <div style={{ display: 'flex', gap: '8px' }}>
              {editingCameraId && (
                <button 
                  type="button" 
                  className="btn-cyber danger" 
                  style={{ padding: '6px 12px' }}
                  onClick={handleCancelEdit}
                >
                  Cancel
                </button>
              )}
              <button 
                type="submit" 
                className="btn-cyber" 
                style={{ padding: '6px 12px' }}
              >
                <Plus size={14} />
                {editingCameraId ? 'Apply Calibration' : 'Register Node'}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Directory listing column */}
      <div className="settings-card">
        <h3 className="form-title">
          <Camera size={18} style={{ color: 'var(--primary-light)' }} />
          Operational Nodes Directory
        </h3>
        <div className="camera-card-list" style={{ overflowY: 'auto', maxHeight: '60vh', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {cameras.map(cam => (
            <CameraCard 
              key={cam.id} 
              camera={cam}
              onToggleActive={onToggleActive}
              onEdit={handleEditCamera}
              onDelete={onDeleteCamera}
            />
          ))}
          {cameras.length === 0 && (
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center', marginTop: '20px' }}>
              No registered camera nodes.
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default SystemSettingsTab;
