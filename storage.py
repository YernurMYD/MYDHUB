"""
In-memory хранилище для данных Wi-Fi мониторинга
"""
import time
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional
import threading


class WiFiDataStorage:
    """Потокобезопасное хранилище данных Wi-Fi мониторинга"""
    
    def __init__(self, max_devices: int = 10000, max_timestamps: int = 1000):
        """
        Инициализация хранилища
        
        Args:
            max_devices: Максимальное количество уникальных устройств
            max_timestamps: Максимальное количество временных меток
        """
        self.max_devices = max_devices
        self.max_timestamps = max_timestamps
        self._lock = threading.Lock()
        
        # Структуры данных:
        # devices: {mac: {latest_rssi, latest_timestamp, first_seen, last_seen, count}}
        self.devices: Dict[str, Dict] = {}
        
        # timestamps: deque с последними временными метками и данными
        self.timestamps: deque = deque(maxlen=max_timestamps)
        
        # statistics: общая статистика
        self.statistics = {
            "total_messages": 0,
            "total_devices": 0,
            "first_message_time": None,
            "last_message_time": None
        }
        
        # Пиковое количество уникальных устройств в одном снимке (за всё время)
        self.peak_snapshot_count: int = 0
        # Количество уникальных устройств в последнем снимке
        self.last_snapshot_count: int = 0
    
    def add_data(self, data: List[Dict]) -> None:
        """
        Добавление данных в хранилище
        
        Args:
            data: Список словарей с ключами m (MAC), r (RSSI), t (timestamp)
        """
        with self._lock:
            current_time = datetime.utcnow()
            
            # Обновление статистики
            self.statistics["total_messages"] += 1
            if not self.statistics["first_message_time"]:
                self.statistics["first_message_time"] = current_time
            self.statistics["last_message_time"] = current_time
            
            # Обработка каждого устройства
            timestamp_data = {}
            now_ts = int(time.time())
            for item in data:
                mac = item.get("m", "").lower()
                rssi = item.get("r", 0)
                timestamp = int(item.get("t", 0) or 0)
                if timestamp <= 0:
                    timestamp = now_ts

                if not mac:
                    continue
                
                # Извлекаем дополнительные поля классификации (если есть)
                vendor = item.get("vendor")
                device_type = item.get("device_type")
                device_brand = item.get("device_brand")
                randomized = item.get("randomized", False)
                
                # Обновление информации об устройстве
                if mac not in self.devices:
                    if len(self.devices) >= self.max_devices:
                        # Удаляем самое старое устройство
                        oldest_mac = min(
                            self.devices.keys(),
                            key=lambda m: self.devices[m].get("last_seen", 0)
                        )
                        del self.devices[oldest_mac]
                    
                    self.devices[mac] = {
                        "first_seen": timestamp,
                        "last_seen": timestamp,
                        "count": 0,
                        "best_rssi": rssi,
                        "latest_rssi": rssi,
                        "vendor": vendor,
                        "device_type": device_type,
                        "device_brand": device_brand,
                        "randomized": randomized
                    }
                    self.statistics["total_devices"] = len(self.devices)
                else:
                    self.devices[mac]["last_seen"] = max(
                        self.devices[mac]["last_seen"],
                        timestamp
                    )
                    self.devices[mac]["best_rssi"] = max(
                        self.devices[mac]["best_rssi"],
                        rssi
                    )
                    self.devices[mac]["latest_rssi"] = rssi
                    # Обновляем поля классификации (если изменились)
                    if vendor:
                        self.devices[mac]["vendor"] = vendor
                    if device_type:
                        self.devices[mac]["device_type"] = device_type
                    if device_brand is not None:
                        self.devices[mac]["device_brand"] = device_brand
                    self.devices[mac]["randomized"] = randomized
                
                self.devices[mac]["count"] += 1
                
                # Сохранение данных для временной метки
                if timestamp not in timestamp_data:
                    timestamp_data[timestamp] = []
                timestamp_data[timestamp].append({
                    "m": mac,
                    "r": rssi
                })
            
            # Добавление временных меток
            for ts, devices_in_ts in timestamp_data.items():
                self.timestamps.append({
                    "t": ts,
                    "d": devices_in_ts,
                    "count": len(devices_in_ts)
                })
            
            # Подсчёт уникальных MAC в этом батче (дедупликация)
            unique_macs_in_batch = set()
            for item in data:
                mac = (item.get("m") or "").lower()
                if mac:
                    unique_macs_in_batch.add(mac)
            
            batch_unique_count = len(unique_macs_in_batch)
            self.last_snapshot_count = batch_unique_count
            if batch_unique_count > self.peak_snapshot_count:
                self.peak_snapshot_count = batch_unique_count
    
    def get_devices(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Получение списка устройств
        
        Args:
            limit: Максимальное количество устройств для возврата
            
        Returns:
            Список устройств с информацией
        """
        with self._lock:
            devices_list = []
            for mac, info in self.devices.items():
                device_dict = {
                    "mac": mac,
                    "first_seen": info["first_seen"],
                    "last_seen": info["last_seen"],
                    "count": info["count"],
                    "best_rssi": info["best_rssi"],
                    "latest_rssi": info["latest_rssi"]
                }
                # Добавляем поля классификации (если есть)
                if "vendor" in info:
                    device_dict["vendor"] = info["vendor"]
                if "device_type" in info:
                    device_dict["device_type"] = info["device_type"]
                if "device_brand" in info:
                    device_dict["device_brand"] = info["device_brand"]
                if "randomized" in info:
                    device_dict["randomized"] = info["randomized"]
                devices_list.append(device_dict)
            
            # Сортировка по последнему времени обнаружения
            devices_list.sort(key=lambda x: x["last_seen"], reverse=True)
            
            if limit:
                devices_list = devices_list[:limit]
            
            return devices_list
    
    def get_statistics(self) -> Dict:
        """Получение статистики"""
        with self._lock:
            return {
                **self.statistics,
                "current_devices": len(self.devices),
                "timestamps_count": len(self.timestamps),
                "peak_snapshot_count": self.peak_snapshot_count,
                "last_snapshot_count": self.last_snapshot_count,
            }
    
    def get_snapshot_summary(self) -> Dict:
        """
        Возвращает сводку по снимкам:
        - peak_all_time: макс. уникальных устройств в одном батче за всё время
        - last_snapshot: кол-во уникальных устройств в последнем батче
        - total_unique: общее кол-во уникальных MAC за всё время
        """
        with self._lock:
            return {
                "peak_all_time": self.peak_snapshot_count,
                "last_snapshot": self.last_snapshot_count,
                "total_unique": len(self.devices),
            }
    
    def get_recent_data(self, limit: int = 100) -> List[Dict]:
        """
        Получение последних данных
        
        Args:
            limit: Максимальное количество записей
            
        Returns:
            Список последних временных меток с данными
        """
        with self._lock:
            return list(self.timestamps)[-limit:]
    
    def get_unique_devices_count(self) -> int:
        """Получение количества уникальных устройств"""
        with self._lock:
            return len(self.devices)
    
    def get_recent_window(self, seconds: int) -> List[Dict]:
        """
        Получение данных за последние N секунд
        
        Args:
            seconds: Количество секунд для выборки
            
        Returns:
            Список записей с временными метками за указанный период
        """
        with self._lock:
            import time
            current_time = int(time.time())
            cutoff_time = current_time - seconds
            
            result = []
            for ts_entry in self.timestamps:
                ts = ts_entry.get("t", 0)
                if ts >= cutoff_time:
                    result.append(ts_entry)
            
            return result
    
    def count_unique_in_window(self, seconds: int) -> int:
        """
        Подсчет количества уникальных устройств за последние N секунд
        
        Args:
            seconds: Количество секунд для выборки
            
        Returns:
            Количество уникальных MAC адресов за период
        """
        with self._lock:
            import time
            current_time = int(time.time())
            cutoff_time = current_time - seconds
            
            unique_macs = set()
            for ts_entry in self.timestamps:
                ts = ts_entry.get("t", 0)
                if ts >= cutoff_time:
                    devices = ts_entry.get("d", [])
                    for device in devices:
                        mac = device.get("m", "").lower()
                        if mac:
                            unique_macs.add(mac)
            
            return len(unique_macs)
    
    def clear(self) -> None:
        """Очистка всех данных"""
        with self._lock:
            self.devices.clear()
            self.timestamps.clear()
            self.statistics = {
                "total_messages": 0,
                "total_devices": 0,
                "first_message_time": None,
                "last_message_time": None
            }
            self.peak_snapshot_count = 0
            self.last_snapshot_count = 0
