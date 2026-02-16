import React, { useState, useMemo } from 'react';
import { formatMAC, formatLastSeen, getDeviceTypeLabel, getDeviceTypeClass, getRSSIClass } from '../../utils/formatters';
import './DevicesTable.css';

const PAGE_SIZE_OPTIONS = [10, 20, 50];

const DevicesTable = ({ devices }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const totalItems = devices?.length || 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));

  const safeCurrentPage = Math.min(currentPage, totalPages);

  const paginatedDevices = useMemo(() => {
    if (!devices || devices.length === 0) return [];
    const start = (safeCurrentPage - 1) * pageSize;
    return devices.slice(start, start + pageSize);
  }, [devices, safeCurrentPage, pageSize]);

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const handlePageSizeChange = (e) => {
    const newSize = Number(e.target.value);
    setPageSize(newSize);
    setCurrentPage(1);
  };

  const getPageNumbers = () => {
    const pages = [];
    const maxVisible = 5;

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      let start = Math.max(1, safeCurrentPage - 2);
      let end = Math.min(totalPages, start + maxVisible - 1);
      if (end - start < maxVisible - 1) {
        start = Math.max(1, end - maxVisible + 1);
      }
      for (let i = start; i <= end; i++) pages.push(i);
    }

    return pages;
  };

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
        <div className="devices-table-count">{totalItems} устройств</div>
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
            {paginatedDevices.map((device, index) => (
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

      {/* Пагинация */}
      <div className="devices-table-pagination">
        <div className="pagination__total">
          Всего {totalItems} записей
        </div>

        <div className="pagination__controls">
          <button
            className="pagination__btn pagination__btn--arrow"
            onClick={() => handlePageChange(safeCurrentPage - 1)}
            disabled={safeCurrentPage <= 1}
            title="Предыдущая"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="14" height="14">
              <polyline points="15 18 9 12 15 6" />
            </svg>
          </button>

          {getPageNumbers().map((page) => (
            <button
              key={page}
              className={`pagination__btn ${page === safeCurrentPage ? 'pagination__btn--active' : ''}`}
              onClick={() => handlePageChange(page)}
            >
              {page}
            </button>
          ))}

          <button
            className="pagination__btn pagination__btn--arrow"
            onClick={() => handlePageChange(safeCurrentPage + 1)}
            disabled={safeCurrentPage >= totalPages}
            title="Следующая"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="14" height="14">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>
        </div>

        <div className="pagination__size">
          <select
            className="pagination__size-select"
            value={pageSize}
            onChange={handlePageSizeChange}
          >
            {PAGE_SIZE_OPTIONS.map((size) => (
              <option key={size} value={size}>
                {size} / стр.
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

export default DevicesTable;
