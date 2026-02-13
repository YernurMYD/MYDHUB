import React, { useState, useEffect, useCallback } from 'react';
import Header from '../../components/Header/Header';
import MetricCard from '../../components/MetricCard/MetricCard';
import TimeframeSelector from '../../components/TimeframeSelector/TimeframeSelector';
import RSSIChart from '../../components/RSSIChart/RSSIChart';
import DevicesTable from '../../components/DevicesTable/DevicesTable';
import { getDeviceTimeseries, getDevicesCount, getDevices, getStatsSummary } from '../../services/api';
import './Dashboard.css';

const periodLabels = { '1h': '1 час', '6h': '6 часов', '12h': '12 часов', '1d': '1 день', '30d': '30 дней' };

const Dashboard = () => {
  const [timeframe, setTimeframe] = useState('1h');
  const [timeseries, setTimeseries] = useState(null);
  const [devicesCount, setDevicesCount] = useState(null);
  const [devices, setDevices] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Загрузка всех данных
   */
  const fetchData = useCallback(async () => {
    try {
      setError(null);
      
      // Параллельная загрузка данных
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

      if (timeseriesResponse) {
        setTimeseries(timeseriesResponse);
      }

      if (countResponse) {
        setDevicesCount(countResponse);
      }

      if (devicesResponse) {
        // Обработка разных форматов ответа
        const devicesList = Array.isArray(devicesResponse)
          ? devicesResponse
          : devicesResponse.devices || devicesResponse.data || [];
        setDevices(devicesList);
      }

      if (summaryResponse) {
        setSummary(summaryResponse);
      }

      setLoading(false);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Ошибка загрузки данных');
      setLoading(false);
    }
  }, [timeframe]);

  /**
   * Эффект для начальной загрузки и периодического обновления
   */
  useEffect(() => {
    // Первая загрузка
    fetchData();

    // Обновление каждые 10 мин (интервал отправки роутера)
    const intervalId = setInterval(() => {
      fetchData();
    }, 600000);

    // Очистка интервала при размонтировании
    return () => clearInterval(intervalId);
  }, [fetchData]);

  /**
   * Вычисление метрик
   */
  const peakAllTime = summary?.peak_all_time ?? 0;
  const activeDevicesPeriod = devicesCount?.count ?? 0;
  const lastSnapshotCount = summary?.last_snapshot ?? 0;

  const chartPoints = (timeseries && Array.isArray(timeseries.points) ? timeseries.points : []) || [];
  const periodLabel = periodLabels[timeframe] || timeframe;

  return (
    <div className="dashboard">
      <Header />
      <main className="dashboard-main">
        <div className="dashboard-container">
          {error && (
            <div className="dashboard-error">
              <p>{error}</p>
            </div>
          )}

          {loading && devices.length === 0 && (
            <div className="dashboard-loading">
              <p>Загрузка данных...</p>
            </div>
          )}

          {/* Метрики */}
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

          {/* Таймфрейм селектор и график RSSI */}
          <section className="dashboard-chart-section">
            <div className="chart-section-header">
              <TimeframeSelector
                selectedTimeframe={timeframe}
                onTimeframeChange={setTimeframe}
              />
            </div>
            <RSSIChart data={chartPoints} timeframe={timeframe} />
          </section>

          {/* Таблица устройств */}
          <section className="dashboard-table-section">
            <DevicesTable devices={devices} />
          </section>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
