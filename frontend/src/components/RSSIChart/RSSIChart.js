import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import './RSSIChart.css';

/**
 * Форматирует unix-timestamp (секунды) в читаемую метку для оси X.
 */
function formatTickLabel(unixSec, timeframe) {
  const d = new Date(unixSec * 1000);
  if (timeframe === '1h' || timeframe === '6h' || timeframe === '12h' || timeframe === '1d') {
    return d.toLocaleTimeString('ru-RU', { hour12: false, hour: '2-digit', minute: '2-digit' });
  }
  // 30d — показываем дату
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
}

/**
 * Форматирует unix-timestamp для тултипа (более подробно).
 */
function formatTooltipLabel(unixSec, timeframe) {
  const d = new Date(unixSec * 1000);
  if (timeframe === '30d') {
    return d.toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
  }
  return d.toLocaleTimeString('ru-RU', { hour12: false, hour: '2-digit', minute: '2-digit' });
}

/**
 * Описание интервала для подзаголовка.
 */
const bucketLabels = {
  '1h': 'Каждый снимок роутера (~10 мин)',
  '6h': 'Каждый снимок роутера (~10 мин)',
  '12h': 'Каждый снимок роутера (~10 мин)',
  '1d': 'Каждый снимок роутера (~10 мин)',
  '30d': 'Максимум за день',
};

const RSSIChart = ({ data, timeframe = '1h' }) => {
  if (!data || data.length === 0) {
    return (
      <div className="rssi-chart-container">
        <div className="rssi-chart-empty">Нет данных для отображения</div>
      </div>
    );
  }

  const chartData = data
    .filter((p) => p && typeof p.t === 'number')
    .map((p) => ({
      t: p.t,
      count: p.count || 0,
    }))
    .sort((a, b) => a.t - b.t);

  // Кастомный tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const point = payload[0].payload;
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">{formatTooltipLabel(point.t, timeframe)}</p>
          <p className="tooltip-value">
            Устройства: <strong>{payload[0].value}</strong>
          </p>
        </div>
      );
    }
    return null;
  };

  const subtitle = bucketLabels[timeframe] || 'По интервалам';

  return (
    <div className="rssi-chart-container">
      <div className="rssi-chart-header">
        <h3 className="rssi-chart-title">Уникальные устройства во времени</h3>
        <p className="rssi-chart-subtitle">{subtitle}</p>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="t"
            type="number"
            scale="time"
            domain={['dataMin', 'dataMax']}
            tickFormatter={(unixSec) => formatTickLabel(unixSec, timeframe)}
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
            height={40}
          />
          <YAxis
            allowDecimals={false}
            label={{ value: 'Устройства', angle: -90, position: 'insideLeft' }}
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
          />
          <Tooltip content={<CustomTooltip />} />
          <Line type="monotone" dataKey="count" stroke="#009FD7" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RSSIChart;
