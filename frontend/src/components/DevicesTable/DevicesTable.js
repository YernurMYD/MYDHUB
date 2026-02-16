import React from 'react';
import './DevicesTable.css';

/**
 * Форматирование MAC адреса
 * @param {string} mac - MAC адрес
 * @returns {string} MAC адрес без маскирования
 */
const formatMAC = (mac) => {
  if (!mac) return '—';
  return mac;
};

/**
 * Форматирование времени последнего обнаружения
 * @param {string|number} timestamp - Unix timestamp (секунды) или миллисекунды
 * @returns {string} Человеко-читаемое время
 */
const formatLastSeen = (timestamp) => {
  if (timestamp === null || timestamp === undefined) return '—';
  
  try {
    let ts = Number(timestamp);
    if (ts <= 0 || isNaN(ts)) return '—';
    // JavaScript Date ожидает миллисекунды; backend присылает Unix timestamp в секундах
    if (ts < 1e12) ts = ts * 1000;
    const date = new Date(ts);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);

    if (diffSec < 60) {
      return `${diffSec} сек назад`;
    } else if (diffMin < 60) {
      return `${diffMin} мин назад`;
    } else if (diffHour < 24) {
      return `${diffHour} ч назад`;
    } else {
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    }
  } catch (error) {
    return '—';
  }
};

/**
 * Человекочитаемые названия типов устройств
 */
const DEVICE_TYPE_LABELS = {
  smartphone: 'Смартфон',
  tablet: 'Планшет',
  laptop: 'Ноутбук',
  smartwatch: 'Часы',
  iot: 'IoT',
  other: 'Другое',
};

/**
 * Получить подпись для device_type
 */
const getDeviceTypeLabel = (type) => DEVICE_TYPE_LABELS[type] || type || '—';

/**
 * CSS-класс для бейджа типа устройства
 */
const getDeviceTypeClass = (type) => {
  if (!type) return 'other';
  return type;
};

const DevicesTable = ({ devices }) => {
  if (!devices || devices.length === 0) {
    return (
      <div className="devices-table-container">
        <div className="devices-table-empty">Нет устройств для отображения</div>
      </div>
    );
  }

  return (
    <div className="devices-table-container">
      <div className="devices-table-header">
        <h3 className="devices-table-title">Обнаруженные устройства</h3>
        <div className="devices-table-count">{devices.length} устройств</div>
      </div>
      <div className="devices-table-wrapper">
        <table className="devices-table">
          <thead>
            <tr>
              <th>MAC адрес</th>
              <th>RSSI</th>
              <th>Производитель</th>
              <th>Тип</th>
              <th>Бренд</th>
              <th>Последнее обнаружение</th>
              <th>Random MAC</th>
            </tr>
          </thead>
          <tbody>
            {devices.map((device, index) => (
              <tr key={device.mac || index}>
                <td className="mac-cell">{formatMAC(device.mac)}</td>
                <td className="rssi-cell">
                  <span className={`rssi-badge rssi-${getRSSIClass(device.rssi)}`}>
                    {device.rssi !== null && device.rssi !== undefined
                      ? `${device.rssi} dBm`
                      : '—'}
                  </span>
                </td>
                <td className="vendor-cell">
                  {device.vendor || '—'}
                </td>
                <td className="device-type-cell">
                  <span className={`type-badge type-${getDeviceTypeClass(device.device_type)}`}>
                    {getDeviceTypeLabel(device.device_type)}
                  </span>
                </td>
                <td className="device-brand-cell">
                  {device.device_brand || '—'}
                </td>
                <td className="last-seen-cell">
                  {formatLastSeen(device.last_seen || device.timestamp)}
                </td>
                <td className="random-mac-cell">
                  {(device.is_random !== undefined || device.randomized !== undefined) ? (
                    <span className={`flag-badge ${(device.is_random ?? device.randomized) ? 'random' : 'static'}`}>
                      {(device.is_random ?? device.randomized) ? 'Да' : 'Нет'}
                    </span>
                  ) : (
                    '—'
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

/**
 * Определение класса для RSSI (для цветовой индикации)
 */
const getRSSIClass = (rssi) => {
  if (rssi === null || rssi === undefined) return 'unknown';
  if (rssi >= -50) return 'excellent';
  if (rssi >= -60) return 'good';
  if (rssi >= -70) return 'fair';
  return 'poor';
};

export default DevicesTable;
