import React, { useState } from 'react';
import { Trash2, AlertTriangle, Eye, X } from 'lucide-react';

const API_BASE = `http://${window.location.hostname}:8000`;

const AlertPanel = ({ events, onDeleteAlert, onClearAll }) => {
  const [selectedImage, setSelectedImage] = useState(null);

  const formatTimestamp = (dateStr) => {
    try {
      const date = new Date(dateStr);
      // Format to HH:MM:SS
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch (e) {
      return dateStr;
    }
  };

  return (
    <div className="alert-panel glass-panel">
      <div className="alert-panel-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={18} style={{ color: 'var(--accent-red)' }} />
          <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.1rem', letterSpacing: '0.5px' }}>
            INCIDENT LOG
          </span>
        </div>
        {events.length > 0 && (
          <button 
            className="btn-cyber danger" 
            style={{ padding: '4px 10px', fontSize: '0.75rem' }}
            onClick={onClearAll}
          >
            Clear All
          </button>
        )}
      </div>

      <div className="alert-list">
        {events.length === 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '12px', color: 'var(--text-muted)' }}>
            <span style={{ fontSize: '0.85rem', letterSpacing: '0.5px' }}>NO ANOMALIES DETECTED</span>
          </div>
        ) : (
          events.map((event) => {
            const isCritical = event.score >= 70.0;
            const cardClass = isCritical ? 'critical' : 'warning';
            const badgeClass = isCritical ? 'badge-critical' : 'badge-warning';
            
            // Image URL points to the FastAPI backend static media server
            const imageUrl = event.image_url ? `${API_BASE}${event.image_url}` : null;

            return (
              <div key={event.id} className={`alert-card ${cardClass}`}>
                {imageUrl && (
                  <img 
                    src={imageUrl} 
                    alt="Anomaly snapshot" 
                    className="alert-thumbnail"
                    onClick={() => setSelectedImage({ url: imageUrl, event })}
                  />
                )}
                
                <div className="alert-info">
                  <div className="alert-meta">
                    <span className="alert-cam-name">{event.camera_name || 'Camera'}</span>
                    <span className="alert-time">{formatTimestamp(event.timestamp)}</span>
                  </div>
                  <span className="alert-desc">{event.description || 'Threat threshold breached.'}</span>
                  <span className={`alert-badge ${badgeClass}`}>
                    THREAT INDEX: {event.score.toFixed(0)}%
                  </span>
                </div>

                <div className="alert-card-right">
                  <button 
                    className="btn-icon" 
                    onClick={() => onDeleteAlert(event.id)}
                    title="Dismiss alert"
                    style={{ margin: '-4px -4px 0 0' }}
                  >
                    <Trash2 size={14} />
                  </button>
                  {imageUrl && (
                    <button 
                      className="btn-icon"
                      onClick={() => setSelectedImage({ url: imageUrl, event })}
                      title="Inspect Snapshot"
                      style={{ color: 'var(--primary)', opacity: 0.8 }}
                    >
                      <Eye size={14} />
                    </button>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Expanded Snapshot Modal */}
      {selectedImage && (
        <div className="modal-backdrop" onClick={() => setSelectedImage(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1rem', color: 'var(--primary)' }}>
                INSPECT SNAPSHOT - {selectedImage.event.camera_name}
              </span>
              <button className="modal-close" onClick={() => setSelectedImage(null)}>
                <X size={20} />
              </button>
            </div>
            
            <img 
              src={selectedImage.url} 
              alt="Expanded event overlay" 
              className="modal-image"
            />
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-main)', fontWeight: 500 }}>
                {selectedImage.event.description}
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Recorded at: {new Date(selectedImage.event.timestamp).toLocaleString()} | Threat: {selectedImage.event.score.toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertPanel;
