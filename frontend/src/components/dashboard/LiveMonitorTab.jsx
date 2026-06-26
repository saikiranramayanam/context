import React from 'react';
import { Camera, AlertTriangle } from 'lucide-react';
import CameraGrid from '../CameraGrid';

const LiveMonitorTab = ({ cameras, selectedCameraId, setSelectedCameraId, events }) => {
  const activeCameras = cameras.filter(c => c.is_active);

  return (
    <div className="live-monitor-layout">
      {/* Live Stream Viewscreen Panel */}
      <div className="live-feed-panel">
        {cameras.length > 0 ? (
          <CameraGrid 
            cameras={cameras} 
            selectedCameraId={selectedCameraId}
            setSelectedCameraId={setSelectedCameraId}
          />
        ) : (
          <div className="glass-panel" style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', gap: '16px', color: 'var(--text-muted)' }}>
            <Camera size={48} className="glow-text" style={{ color: 'var(--primary)' }} />
            <p style={{ letterSpacing: '0.5px' }}>NO CAMERAS CONFIGURED. REGISTER A STREAM IN SYSTEM SETTINGS TAB.</p>
          </div>
        )}
      </div>

      {/* Sidebar with Real-time Alert Ticker */}
      <div className="live-ticker-panel">
        <div className="ticker-header">
          <AlertTriangle size={18} style={{ color: 'var(--accent-red)' }} />
          <span className="ticker-title">Real-Time Alert Ticker</span>
        </div>
        <div className="ticker-list">
          {events.length === 0 ? (
            <div className="ticker-placeholder">
              <span>SYSTEM SECURE - NO RECENT ALERTS</span>
            </div>
          ) : (
            events.slice(0, 5).map(event => {
              const isCritical = event.score >= 70.0;
              return (
                <div key={event.id} className={`alert-card ${isCritical ? 'critical' : 'warning'}`} style={{ padding: '12px', fontSize: '0.8rem' }}>
                  <div className="alert-info" style={{ gap: '2px' }}>
                    <div className="alert-meta">
                      <span className="alert-cam-name" style={{ fontSize: '0.75rem' }}>{event.camera_name}</span>
                      <span className="alert-time" style={{ fontSize: '0.7rem' }}>
                        {new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                      </span>
                    </div>
                    <span className="alert-desc" style={{ fontSize: '0.8rem', WebkitLineClamp: 1, marginTop: '2px' }}>
                      {event.description}
                    </span>
                    <span style={{ fontSize: '0.7rem', color: isCritical ? 'var(--accent-red)' : 'var(--accent-yellow)', fontWeight: 700, marginTop: '4px' }}>
                      THREAT INDEX: {event.score.toFixed(0)}%
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

export default LiveMonitorTab;
