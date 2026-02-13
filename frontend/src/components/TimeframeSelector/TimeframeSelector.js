import React from 'react';
import './TimeframeSelector.css';

const TimeframeSelector = ({ selectedTimeframe, onTimeframeChange }) => {
  const timeframes = [
    { value: '1h', label: '1 час' },
    { value: '6h', label: '6 часов' },
    { value: '12h', label: '12 часов' },
    { value: '1d', label: '1 день' },
    { value: '30d', label: '30 дней' },
  ];

  return (
    <div className="timeframe-selector">
      <label className="timeframe-label">Период:</label>
      <div className="timeframe-buttons">
        {timeframes.map((timeframe) => (
          <button
            key={timeframe.value}
            className={`timeframe-button ${
              selectedTimeframe === timeframe.value ? 'active' : ''
            }`}
            onClick={() => onTimeframeChange(timeframe.value)}
          >
            {timeframe.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default TimeframeSelector;
