import React, { useState, useEffect, useCallback } from 'react';
import MetricCard from '../../components/MetricCard/MetricCard';
import TimeframeSelector from '../../components/TimeframeSelector/TimeframeSelector';
import RSSIChart from '../../components/RSSIChart/RSSIChart';
import DevicesTable from '../../components/DevicesTable/DevicesTable';
import { getDeviceTimeseries, getDevicesCount, getDevices, getStatsSummary } from '../../services/api';
import './Dashboard.css';

const ROUTERS_KEY = 'myd_routers';

const periodLabels = { '1h': '1 час', '6h': '6 часов', '12h': '12 часов', '1d': '1 день', '30d': '30 дней' };

const loadRouters = () => {
  try {
    const stored = JSON.parse(localStorage.getItem(ROUTERS_KEY));
    if (stored && stored.length > 0) return stored;
    return [{ id: 'router-default', name: 'Роутер 1 (Основной)', isPrimary: true }];
  } catch {
    return [{ id: 'router-default', name: 'Роутер 1 (Основной)', isPrimary: true }];
  }
};

const Dashboard = () => {
  const [routers] = useState(loadRouters);
  const [selectedRouterId, setSelectedRouterId] = useState(() => {
    const list = loadRouters();
    const primary = list.find((r) => r.isPrimary);
    return primary ? primary.id : list[0]?.id || '';
  });

  const [timeframe, setTimeframe] = useState('1h');
  const [timeseries, setTimeseries] = useState(null);
  const [devicesCount, setDevicesCount] = useState(null);
  const [devices, setDevices] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const selectedRouter = routers.find((r) => r.id === selectedRouterId) || routers[0];
  const isActiveRouter = selectedRouter?.isPrimary;

  const fetchData = useCallback(async () => {
    if (!isActiveRouter) {
      setLoading(false);
      setTimeseries(null);
      setDevicesCount(null);
      setDevices([]);
      setSummary(null);
      return;
    }

    try {
      setError(null);

      const [timeseriesResponse, countResponse, devicesResponse, summaryResponse] = await Promise.all([
        getDeviceTimeseries(timeframe).catch((err) => {
          console.warn('Timeseries error:', err);
          return null;
        }),
        getDevicesCount(timeframe).catch((err) => {
          console.warn('Devices count error:', err);
          return null;
        }),
        getDevices().catch((err) => {
          console.warn('Devices error:', err);
          return { devices: [] };
        }),
        getStatsSummary().catch((err) => {
          console.warn('Summary error:', err);
          return null;
        }),
      ]);

      if (timeseriesResponse) setTimeseries(timeseriesResponse);
      if (countResponse) setDevicesCount(countResponse);

      if (devicesResponse) {
        const devicesList = Array.isArray(devicesResponse)
          ? devicesResponse
          : devicesResponse.devices || devicesResponse.data || [];
        setDevices(devicesList);
      }

      if (summaryResponse) setSummary(summaryResponse);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Ошибка загрузки данных');
      setLoading(false);
    }
  }, [timeframe, isActiveRouter]);

  useEffect(() => {
    setLoading(true);
    fetchData();
    const intervalId = setInterval(fetchData, 600000);
    return () => clearInterval(intervalId);
  }, [fetchData]);

  const peakAllTime = summary?.peak_all_time ?? 0;
  const activeDevicesPeriod = devicesCount?.count ?? 0;
  const lastSnapshotCount = summary?.last_snapshot ?? 0;
  const chartPoints = (timeseries && Array.isArray(timeseries.points) ? timeseries.points : []) || [];
  const periodLabel = periodLabels[timeframe] || timeframe;

  return (
    <div className="dashboard">
      {/* Селектор роутера */}
      <div className="dashboard-router-selector">
        <div className="dashboard-router-selector__info">
          <svg className="dashboard-router-selector__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 12.55a11 11 0 0 1 14.08 0" />
            <path d="M1.42 9a16 16 0 0 1 21.16 0" />
            <path d="M8.53 16.11a6 6 0 0 1 6.95 0" />
            <circle cx="12" cy="20" r="1" fill="currentColor" />
          </svg>
          <span className="dashboard-router-selector__label">Источник данных:</span>
        </div>
        <select
          className="dashboard-router-selector__select"
          value={selectedRouterId}
          onChange={(e) => setSelectedRouterId(e.target.value)}
        >
          {routers.map((r) => (
            <option key={r.id} value={r.id}>
              {r.name}{r.location && r.location !== 'Не задана' ? ` — ${r.location}` : ''}
            </option>
          ))}
        </select>
      </div>

      {!isActiveRouter && (
        <div className="dashboard-notice">
          <p>Роутер «{selectedRouter?.name}» ещё не подключён к системе. Данные будут доступны после настройки MQTT на устройстве.</p>
        </div>
      )}

      {error && (
        <div className="dashboard-error">
          <p>{error}</p>
        </div>
      )}

      {loading && devices.length === 0 && isActiveRouter && (
        <div className="dashboard-loading">
          <p>Загрузка данных...</p>
        </div>
      )}

      {isActiveRouter && (
        <>
          <section className="dashboard-metrics">
            <MetricCard
              title="Пик за всё время"
              value={peakAllTime}
              subtitle="Макс. устройств в одном замере"
            />
            <MetricCard
              title="За выбранный период"
              value={activeDevicesPeriod}
              subtitle={`Уникальных за: ${periodLabel}`}
            />
            <MetricCard
              title="Последний замер"
              value={lastSnapshotCount}
              subtitle="Устройств в последнем снимке"
            />
          </section>

          <section className="dashboard-chart-section">
            <div className="chart-section-header">
              <TimeframeSelector
                selectedTimeframe={timeframe}
                onTimeframeChange={setTimeframe}
              />
            </div>
            <RSSIChart data={chartPoints} timeframe={timeframe} />
          </section>

          <section className="dashboard-table-section">
            <DevicesTable devices={devices} />
          </section>
        </>
      )}
    </div>
  );
};

export default Dashboard;
