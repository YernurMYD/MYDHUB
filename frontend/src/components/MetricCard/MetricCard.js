import React from 'react';
import './MetricCard.css';

const MetricCard = ({ title, value, subtitle, icon }) => {
  return (
    <div className="metric-card">
      <div className="metric-card-content">
        <div className="metric-card-header">
          <h3 className="metric-card-title">{title}</h3>
          {icon && <div className="metric-card-icon">{icon}</div>}
        </div>
        <div className="metric-card-value">{value !== null ? value : '—'}</div>
        {subtitle && <div className="metric-card-subtitle">{subtitle}</div>}
      </div>
    </div>
  );
};

export default MetricCard;
