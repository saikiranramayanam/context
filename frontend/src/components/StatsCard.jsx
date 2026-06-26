import React from 'react';

const StatsCard = ({ label, value, icon: Icon, className = '' }) => {
  return (
    <div className={`stat-card glass-panel ${className}`}>
      <div className="stat-card-info">
        <span className="stat-label">{label}</span>
        <span className="stat-value">{value}</span>
      </div>
      {Icon && (
        <div className="stat-icon">
          <Icon size={24} />
        </div>
      )}
    </div>
  );
};

export default StatsCard;
