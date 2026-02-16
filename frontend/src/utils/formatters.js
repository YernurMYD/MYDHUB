/**
 * Форматирование MAC адреса
 * @param {string} mac - MAC адрес
 * @returns {string} MAC адрес или заглушка
 */
export const formatMAC = (mac) => {
  if (!mac) return '—';
  return mac;
};

/**
 * Форматирование времени последнего обнаружения
 * @param {string|number} timestamp - Unix timestamp (секунды) или миллисекунды
 * @returns {string} Человеко-читаемое время
 */
export const formatLastSeen = (timestamp) => {
  if (timestamp === null || timestamp === undefined) return '—';

  try {
    let ts = Number(timestamp);
    if (ts <= 0 || isNaN(ts)) return '—';
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
 * Нормализация Unix timestamp в миллисекунды
 * @param {string|number} timestamp
 * @returns {number|null}
 */
export const normalizeTimestamp = (timestamp) => {
  if (timestamp === null || timestamp === undefined) return null;
  let ts = Number(timestamp);
  if (ts <= 0 || isNaN(ts)) return null;
  if (ts < 1e12) ts = ts * 1000;
  return ts;
};

/**
 * Человекочитаемые названия типов устройств
 */
export const DEVICE_TYPE_LABELS = {
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
export const getDeviceTypeLabel = (type) => DEVICE_TYPE_LABELS[type] || type || '—';

/**
 * CSS-класс для бейджа типа устройства
 */
export const getDeviceTypeClass = (type) => {
  if (!type) return 'other';
  return type;
};

/**
 * Определение класса для RSSI (для цветовой индикации)
 */
export const getRSSIClass = (rssi) => {
  if (rssi === null || rssi === undefined) return 'unknown';
  if (rssi >= -50) return 'excellent';
  if (rssi >= -60) return 'good';
  if (rssi >= -70) return 'fair';
  return 'poor';
};

/**
 * Проверка, онлайн ли устройство (видели менее 10 минут назад)
 * @param {number} lastSeen - Unix timestamp последнего обнаружения
 * @returns {boolean}
 */
export const isDeviceOnline = (lastSeen) => {
  const ts = normalizeTimestamp(lastSeen);
  if (!ts) return false;
  const diffMs = Date.now() - ts;
  return diffMs < 10 * 60 * 1000;
};
