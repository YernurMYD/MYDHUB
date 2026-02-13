import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Получение данных реального времени (последние 60 секунд)
 * @returns {Promise<Object>} Данные реального времени
 */
export const getRealtimeStats = async () => {
  try {
    const response = await apiClient.get('/stats/realtime');
    return response.data;
  } catch (error) {
    console.error('Error fetching realtime stats:', error);
    throw error;
  }
};

/**
 * Временной ряд: уникальные устройства во времени (по last_seen по бакетам)
 * @param {string} timeframe - 10m|30m|1h|1d|30d
 * @returns {Promise<Object>} { timeframe, start_ts, end_ts, bucket_sec, points: [{t, count}] }
 */
export const getDeviceTimeseries = async (timeframe = '1h') => {
  try {
    const response = await apiClient.get('/stats/devices_timeseries', {
      params: { timeframe },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching device timeseries:', error);
    throw error;
  }
};

/**
 * Уникальные устройства за период (last_seen в диапазоне)
 * @param {string} timeframe - 10m|30m|1h|1d|30d
 * @returns {Promise<Object>} { timeframe, count, start_ts, end_ts }
 */
export const getDevicesCount = async (timeframe = '1h') => {
  try {
    const response = await apiClient.get('/stats/count', {
      params: { timeframe },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching devices count:', error);
    throw error;
  }
};

/**
 * Сводка метрик: пик за всё время, последний замер, всего уникальных
 * @returns {Promise<Object>} { peak_all_time, last_snapshot, total_unique }
 */
export const getStatsSummary = async () => {
  try {
    const response = await apiClient.get('/stats/summary');
    return response.data;
  } catch (error) {
    console.error('Error fetching stats summary:', error);
    throw error;
  }
};

/**
 * Получение списка устройств
 * @returns {Promise<Array>} Список устройств
 */
export const getDevices = async () => {
  try {
    const response = await apiClient.get('/devices');
    // Обработка разных форматов ответа
    if (Array.isArray(response.data)) {
      return response.data;
    }
    return response.data.devices || response.data.data || [];
  } catch (error) {
    console.error('Error fetching devices:', error);
    throw error;
  }
};

export default apiClient;
