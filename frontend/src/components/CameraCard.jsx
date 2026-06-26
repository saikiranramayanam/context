import React from 'react';
import { Edit2, Trash2, Camera } from 'lucide-react';

const CameraCard = ({ camera, onToggleActive, onEdit, onDelete }) => {
  return (
    <div className="camera-config-card">
      <div className="camera-card-details">
        <span className="camera-card-name" title={camera.name}>
          <Camera size={14} style={{ inlineSize: 'auto', marginRight: '6px', color: 'var(--primary)', verticalAlign: 'middle' }} />
          {camera.name}
        </span>
        <span className="camera-card-source" title={camera.source}>
          SRC: {camera.source}
        </span>
      </div>
      <div className="camera-card-actions">
        {/* Toggle Switch */}
        <label className="switch" title="Toggle active status">
          <input 
            type="checkbox" 
            checked={camera.is_active} 
            onChange={() => onToggleActive(camera)}
          />
          <span className="slider"></span>
        </label>
        
        {/* Edit Button */}
        <button 
          className="btn-icon" 
          onClick={() => onEdit(camera)}
          title="Edit Camera"
          style={{ color: 'var(--text-muted)' }}
        >
          <Edit2 size={14} />
        </button>
        
        {/* Delete Button */}
        <button 
          className="btn-icon" 
          onClick={() => onDelete(camera.id)}
          title="Delete Camera"
          style={{ color: 'var(--text-muted)' }}
        >
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  );
};

export default CameraCard;
