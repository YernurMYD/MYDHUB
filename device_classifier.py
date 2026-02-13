"""
Классификация устройств по MAC адресу (OUI)
"""
from typing import Dict, Optional


# Таблица OUI (Organizationally Unique Identifier) -> Vendor
# Первые 3 октета MAC адреса
OUI_VENDOR_MAP = {
    # Smartphones
    "00:1e:c2": "Apple",      # Apple iPhone/iPad
    "00:23:df": "Apple",
    "00:25:00": "Apple",
    "00:26:08": "Apple",
    "00:26:4a": "Apple",
    "00:26:bb": "Apple",
    "00:50:56": "Apple",
    "04:0c:ce": "Apple",
    "04:15:52": "Apple",
    "04:1e:64": "Apple",
    "04:26:65": "Apple",
    "04:4b:ed": "Apple",
    "04:52:f7": "Apple",
    "04:54:53": "Apple",
    "04:69:f8": "Apple",
    "04:db:56": "Apple",
    "08:00:07": "Apple",
    "08:66:98": "Apple",
    "08:74:02": "Apple",
    "0c:3e:9f": "Apple",
    "0c:4d:e9": "Apple",
    "0c:74:c2": "Apple",
    "0c:bc:9f": "Apple",
    "0c:d0:f8": "Apple",
    "10:1c:0c": "Apple",
    "10:93:e9": "Apple",
    "10:dd:b1": "Apple",
    "14:10:9f": "Apple",
    "14:7d:da": "Apple",
    "14:88:e6": "Apple",
    "14:99:e2": "Apple",
    "18:20:32": "Apple",
    "18:65:90": "Apple",
    "18:9e:fc": "Apple",
    "1c:1a:c0": "Apple",
    "1c:ab:a7": "Apple",
    "20:78:f0": "Apple",
    "20:ab:37": "Apple",
    "20:c9:d0": "Apple",
    "24:a0:74": "Apple",
    "24:ab:81": "Apple",
    "24:e3:14": "Apple",
    "28:37:37": "Apple",
    "28:6a:ba": "Apple",
    "28:cf:da": "Apple",
    "28:cf:e9": "Apple",
    "2c:1f:23": "Apple",
    "2c:33:7a": "Apple",
    "2c:be:08": "Apple",
    "30:90:ab": "Apple",
    "34:15:9e": "Apple",
    "34:4d:f7": "Apple",
    "34:a3:95": "Apple",
    "38:ca:da": "Apple",
    "3c:07:54": "Apple",
    "3c:15:c2": "Apple",
    "3c:ab:8e": "Apple",
    "40:33:1a": "Apple",
    "40:4e:36": "Apple",
    "44:4c:0c": "Apple",
    "44:fb:42": "Apple",
    "48:43:7c": "Apple",
    "48:bf:6b": "Apple",
    "4c:7c:5f": "Apple",
    "4c:8d:79": "Apple",
    "50:ea:d6": "Apple",
    "54:26:96": "Apple",
    "54:72:4f": "Apple",
    "58:55:ca": "Apple",
    "5c:59:48": "Apple",
    "5c:95:ae": "Apple",
    "60:33:4b": "Apple",
    "60:c5:47": "Apple",
    "64:9a:be": "Apple",
    "68:96:7b": "Apple",
    "68:ab:1e": "Apple",
    "6c:40:08": "Apple",
    "6c:72:20": "Apple",
    "6c:8d:c1": "Apple",
    "70:48:0f": "Apple",
    "70:56:81": "Apple",
    "74:e2:f5": "Apple",
    "78:31:c1": "Apple",
    "78:4f:43": "Apple",
    "78:ca:39": "Apple",
    "7c:6d:62": "Apple",
    "7c:d1:c3": "Apple",
    "80:be:05": "Apple",
    "80:e6:50": "Apple",
    "84:38:35": "Apple",
    "84:fc:fe": "Apple",
    "88:63:df": "Apple",
    "8c:7c:92": "Apple",
    "8c:85:90": "Apple",
    "90:72:40": "Apple",
    "94:e9:6a": "Apple",
    "98:01:a7": "Apple",
    "98:ca:33": "Apple",
    "9c:84:bf": "Apple",
    "9c:e0:63": "Apple",
    "a0:99:9b": "Apple",
    "a4:5e:60": "Apple",
    "a4:c3:61": "Apple",
    "a8:60:b6": "Apple",
    "a8:96:8a": "Apple",
    "ac:1f:74": "Apple",
    "ac:bc:32": "Apple",
    "b0:65:bd": "Apple",
    "b4:f0:ab": "Apple",
    "b8:09:8a": "Apple",
    "b8:53:ac": "Apple",
    "bc:3b:af": "Apple",
    "bc:52:b7": "Apple",
    "c0:25:e9": "Apple",
    "c4:2c:03": "Apple",
    "c8:1e:e7": "Apple",
    "c8:33:4b": "Apple",
    "cc:08:e0": "Apple",
    "cc:29:f5": "Apple",
    "d0:03:4b": "Apple",
    "d0:23:db": "Apple",
    "d4:9a:20": "Apple",
    "d8:30:62": "Apple",
    "d8:a2:5e": "Apple",
    "dc:2b:61": "Apple",
    "dc:a9:04": "Apple",
    "e0:ac:cb": "Apple",
    "e4:ce:8f": "Apple",
    "e8:40:40": "Apple",
    "ec:35:86": "Apple",
    "f0:18:98": "Apple",
    "f0:db:e2": "Apple",
    "f4:f1:5a": "Apple",
    "f8:1e:df": "Apple",
    "fc:25:3f": "Apple",
    "fc:db:b3": "Apple",
    
    # Samsung
    "00:12:fb": "Samsung",
    "00:15:99": "Samsung",
    "00:16:32": "Samsung",
    "00:16:6b": "Samsung",
    "00:16:db": "Samsung",
    "00:17:c9": "Samsung",
    "00:18:af": "Samsung",
    "00:1d:25": "Samsung",
    "00:1e:7d": "Samsung",
    "00:1f:cc": "Samsung",
    "00:21:4c": "Samsung",
    "00:23:39": "Samsung",
    "00:23:76": "Samsung",
    "00:24:54": "Samsung",
    "00:25:66": "Samsung",
    "00:26:5d": "Samsung",
    "00:26:e8": "Samsung",
    "00:50:f1": "Samsung",
    "04:1b:ba": "Samsung",
    "04:25:c5": "Samsung",
    "04:37:ea": "Samsung",
    "04:52:f3": "Samsung",
    "04:fe:a1": "Samsung",
    "08:00:28": "Samsung",
    "08:00:43": "Samsung",
    "0c:14:20": "Samsung",
    "0c:48:85": "Samsung",
    "10:30:47": "Samsung",
    "10:68:3f": "Samsung",
    "14:10:9f": "Samsung",
    "18:16:c9": "Samsung",
    "1c:66:aa": "Samsung",
    "1c:99:4c": "Samsung",
    "20:54:fa": "Samsung",
    "24:92:cc": "Samsung",
    "28:39:5e": "Samsung",
    "2c:44:fd": "Samsung",
    "30:19:66": "Samsung",
    "34:23:87": "Samsung",
    "38:16:d1": "Samsung",
    "3c:5a:37": "Samsung",
    "40:b3:95": "Samsung",
    "44:80:eb": "Samsung",
    "48:13:7e": "Samsung",
    "4c:66:41": "Samsung",
    "50:cc:f8": "Samsung",
    "54:92:09": "Samsung",
    "58:55:ca": "Samsung",
    "5c:0a:5b": "Samsung",
    "5c:51:88": "Samsung",
    "60:21:c0": "Samsung",
    "64:77:91": "Samsung",
    "68:27:37": "Samsung",
    "6c:8d:c1": "Samsung",
    "70:48:0f": "Samsung",
    "74:45:ce": "Samsung",
    "78:52:1b": "Samsung",
    "7c:1e:52": "Samsung",
    "80:00:6e": "Samsung",
    "84:25:db": "Samsung",
    "88:83:22": "Samsung",
    "8c:3a:e3": "Samsung",
    "90:18:7c": "Samsung",
    "94:51:03": "Samsung",
    "98:0c:82": "Samsung",
    "9c:99:a0": "Samsung",
    "a0:82:1f": "Samsung",
    "a4:50:46": "Samsung",
    "a8:1b:5a": "Samsung",
    "ac:5a:14": "Samsung",
    "b0:47:bf": "Samsung",
    "b4:3e:8b": "Samsung",
    "b8:57:d8": "Samsung",
    "bc:14:85": "Samsung",
    "c0:65:99": "Samsung",
    "c4:57:6e": "Samsung",
    "c8:14:79": "Samsung",
    "cc:07:ab": "Samsung",
    "d0:22:be": "Samsung",
    "d4:6e:5c": "Samsung",
    "d8:55:eb": "Samsung",
    "dc:66:72": "Samsung",
    "e0:50:8b": "Samsung",
    "e4:58:e7": "Samsung",
    "e8:50:8b": "Samsung",
    "ec:9b:f3": "Samsung",
    "f0:25:b7": "Samsung",
    "f4:09:d8": "Samsung",
    "f8:04:2e": "Samsung",
    "fc:64:ba": "Samsung",
    
    # Laptops
    "00:1b:21": "Intel",      # Intel Corporation
    "00:1e:67": "Intel",
    "00:1f:3c": "Intel",
    "00:21:5c": "Intel",
    "00:22:fa": "Intel",
    "00:24:d7": "Intel",
    "00:26:c7": "Intel",
    "00:aa:02": "Intel",
    "04:7d:7b": "Intel",
    "08:00:27": "Intel",
    "0c:54:15": "Intel",
    "10:7b:44": "Intel",
    "14:4f:8a": "Intel",
    "18:03:73": "Intel",
    "1c:1b:0d": "Intel",
    "20:7d:74": "Intel",
    "24:77:03": "Intel",
    "28:18:78": "Intel",
    "2c:44:fd": "Intel",
    "30:52:cb": "Intel",
    "34:e6:ad": "Intel",
    "38:00:25": "Intel",
    "3c:07:54": "Intel",
    "40:8d:5c": "Intel",
    "44:8a:5b": "Intel",
    "48:45:20": "Intel",
    "4c:34:88": "Intel",
    "50:46:5d": "Intel",
    "54:e1:ad": "Intel",
    "58:55:ca": "Intel",
    "5c:26:0a": "Intel",
    "60:67:20": "Intel",
    "64:6e:6c": "Intel",
    "68:5d:43": "Intel",
    "6c:88:14": "Intel",
    "70:85:c2": "Intel",
    "74:e5:0b": "Intel",
    "78:44:76": "Intel",
    "7c:67:a2": "Intel",
    "80:86:f2": "Intel",
    "84:a4:23": "Intel",
    "88:c6:26": "Intel",
    "8c:70:5a": "Intel",
    "90:48:9a": "Intel",
    "94:57:a5": "Intel",
    "98:4b:e1": "Intel",
    "9c:b6:d0": "Intel",
    "a0:88:b4": "Intel",
    "a4:4c:c8": "Intel",
    "a8:60:b6": "Intel",
    "ac:de:48": "Intel",
    "b0:7f:b9": "Intel",
    "b4:6d:83": "Intel",
    "b8:81:98": "Intel",
    "bc:77:37": "Intel",
    "c0:25:e9": "Intel",
    "c4:34:6b": "Intel",
    "c8:5b:76": "Intel",
    "cc:46:d6": "Intel",
    "d0:50:99": "Intel",
    "d4:6e:5c": "Intel",
    "d8:30:62": "Intel",
    "dc:53:60": "Intel",
    "e0:94:67": "Intel",
    "e4:ce:8f": "Intel",
    "e8:40:40": "Intel",
    "ec:9b:f3": "Intel",
    "f0:18:98": "Intel",
    "f4:8e:38": "Intel",
    "f8:46:1c": "Intel",
    "fc:aa:14": "Intel",
    
    "00:1a:a0": "Dell",       # Dell Inc.
    "00:1e:c9": "Dell",
    "00:21:70": "Dell",
    "00:24:e8": "Dell",
    "00:26:b9": "Dell",
    "00:50:56": "Dell",
    "04:7d:7b": "Dell",
    "08:74:02": "Dell",
    "0c:4d:e9": "Dell",
    "10:1c:0c": "Dell",
    "14:fe:b5": "Dell",
    "18:03:73": "Dell",
    "1c:1a:c0": "Dell",
    "20:47:da": "Dell",
    "24:b6:fd": "Dell",
    "28:92:4a": "Dell",
    "2c:44:fd": "Dell",
    "30:9c:23": "Dell",
    "34:17:eb": "Dell",
    "38:0e:4d": "Dell",
    "3c:07:54": "Dell",
    "40:b4:cd": "Dell",
    "44:a8:42": "Dell",
    "48:0e:ec": "Dell",
    "4c:76:25": "Dell",
    "50:46:5d": "Dell",
    "54:9f:13": "Dell",
    "58:55:ca": "Dell",
    "5c:26:0a": "Dell",
    "60:6c:66": "Dell",
    "64:51:06": "Dell",
    "68:f7:28": "Dell",
    "6c:88:14": "Dell",
    "70:85:c2": "Dell",
    "74:86:7a": "Dell",
    "78:2b:cb": "Dell",
    "7c:1e:52": "Dell",
    "80:18:a7": "Dell",
    "84:2b:2b": "Dell",
    "88:51:fb": "Dell",
    "8c:89:a5": "Dell",
    "90:b1:1c": "Dell",
    "94:db:56": "Dell",
    "98:4b:e1": "Dell",
    "9c:8e:cd": "Dell",
    "a0:36:9f": "Dell",
    "a4:4c:c8": "Dell",
    "a8:60:b6": "Dell",
    "ac:1f:74": "Dell",
    "b0:83:fe": "Dell",
    "b4:2c:09": "Dell",
    "b8:27:eb": "Dell",
    "bc:30:5b": "Dell",
    "c0:25:e9": "Dell",
    "c4:34:6b": "Dell",
    "c8:1e:e7": "Dell",
    "cc:46:d6": "Dell",
    "d0:67:e5": "Dell",
    "d4:ae:52": "Dell",
    "d8:9d:67": "Dell",
    "dc:53:60": "Dell",
    "e0:db:55": "Dell",
    "e4:ce:8f": "Dell",
    "e8:40:40": "Dell",
    "ec:9b:f3": "Dell",
    "f0:1f:af": "Dell",
    "f4:8e:38": "Dell",
    "f8:bc:12": "Dell",
    "fc:aa:14": "Dell",
    
    "00:1e:68": "HP",         # Hewlett-Packard
    "00:1f:29": "HP",
    "00:21:5a": "HP",
    "00:23:5a": "HP",
    "00:24:81": "HP",
    "00:26:55": "HP",
    "00:50:56": "HP",
    "04:0c:ce": "HP",
    "08:00:09": "HP",
    "0c:4d:e9": "HP",
    "10:1c:0c": "HP",
    "14:fe:b5": "HP",
    "18:03:73": "HP",
    "1c:1a:c0": "HP",
    "20:6a:8a": "HP",
    "24:be:05": "HP",
    "28:92:4a": "HP",
    "2c:27:d7": "HP",
    "30:9c:23": "HP",
    "34:17:eb": "HP",
    "38:0e:4d": "HP",
    "3c:52:82": "HP",
    "40:b4:cd": "HP",
    "44:a8:42": "HP",
    "48:0e:ec": "HP",
    "4c:76:25": "HP",
    "50:46:5d": "HP",
    "54:9f:13": "HP",
    "58:55:ca": "HP",
    "5c:b3:95": "HP",
    "60:6c:66": "HP",
    "64:51:06": "HP",
    "68:f7:28": "HP",
    "6c:88:14": "HP",
    "70:85:c2": "HP",
    "74:86:7a": "HP",
    "78:2b:cb": "HP",
    "7c:1e:52": "HP",
    "80:18:a7": "HP",
    "84:2b:2b": "HP",
    "88:51:fb": "HP",
    "8c:89:a5": "HP",
    "90:b1:1c": "HP",
    "94:db:56": "HP",
    "98:4b:e1": "HP",
    "9c:8e:cd": "HP",
    "a0:36:9f": "HP",
    "a4:4c:c8": "HP",
    "a8:60:b6": "HP",
    "ac:1f:74": "HP",
    "b0:83:fe": "HP",
    "b4:2c:09": "HP",
    "b8:27:eb": "HP",
    "bc:30:5b": "HP",
    "c0:25:e9": "HP",
    "c4:34:6b": "HP",
    "c8:1e:e7": "HP",
    "cc:46:d6": "HP",
    "d0:67:e5": "HP",
    "d4:ae:52": "HP",
    "d8:9d:67": "HP",
    "dc:53:60": "HP",
    "e0:db:55": "HP",
    "e4:ce:8f": "HP",
    "e8:40:40": "HP",
    "ec:9b:f3": "HP",
    "f0:1f:af": "HP",
    "f4:8e:38": "HP",
    "f8:bc:12": "HP",
    "fc:aa:14": "HP",
    
    "00:1b:24": "Lenovo",    # Lenovo
    "00:21:cc": "Lenovo",
    "00:23:8b": "Lenovo",
    "00:25:64": "Lenovo",
    "00:26:18": "Lenovo",
    "00:50:56": "Lenovo",
    "04:0c:ce": "Lenovo",
    "08:00:09": "Lenovo",
    "0c:4d:e9": "Lenovo",
    "10:1c:0c": "Lenovo",
    "14:fe:b5": "Lenovo",
    "18:03:73": "Lenovo",
    "1c:1a:c0": "Lenovo",
    "20:47:da": "Lenovo",
    "24:b6:fd": "Lenovo",
    "28:92:4a": "Lenovo",
    "2c:44:fd": "Lenovo",
    "30:9c:23": "Lenovo",
    "34:17:eb": "Lenovo",
    "38:0e:4d": "Lenovo",
    "3c:07:54": "Lenovo",
    "40:b4:cd": "Lenovo",
    "44:a8:42": "Lenovo",
    "48:0e:ec": "Lenovo",
    "4c:76:25": "Lenovo",
    "50:46:5d": "Lenovo",
    "54:9f:13": "Lenovo",
    "58:55:ca": "Lenovo",
    "5c:26:0a": "Lenovo",
    "60:6c:66": "Lenovo",
    "64:51:06": "Lenovo",
    "68:f7:28": "Lenovo",
    "6c:88:14": "Lenovo",
    "70:85:c2": "Lenovo",
    "74:86:7a": "Lenovo",
    "78:2b:cb": "Lenovo",
    "7c:1e:52": "Lenovo",
    "80:18:a7": "Lenovo",
    "84:2b:2b": "Lenovo",
    "88:51:fb": "Lenovo",
    "8c:89:a5": "Lenovo",
    "90:b1:1c": "Lenovo",
    "94:db:56": "Lenovo",
    "98:4b:e1": "Lenovo",
    "9c:8e:cd": "Lenovo",
    "a0:36:9f": "Lenovo",
    "a4:4c:c8": "Lenovo",
    "a8:60:b6": "Lenovo",
    "ac:1f:74": "Lenovo",
    "b0:83:fe": "Lenovo",
    "b4:2c:09": "Lenovo",
    "b8:27:eb": "Lenovo",
    "bc:30:5b": "Lenovo",
    "c0:25:e9": "Lenovo",
    "c4:34:6b": "Lenovo",
    "c8:1e:e7": "Lenovo",
    "cc:46:d6": "Lenovo",
    "d0:67:e5": "Lenovo",
    "d4:ae:52": "Lenovo",
    "d8:9d:67": "Lenovo",
    "dc:53:60": "Lenovo",
    "e0:db:55": "Lenovo",
    "e4:ce:8f": "Lenovo",
    "e8:40:40": "Lenovo",
    "ec:9b:f3": "Lenovo",
    "f0:1f:af": "Lenovo",
    "f4:8e:38": "Lenovo",
    "f8:bc:12": "Lenovo",
    "fc:aa:14": "Lenovo",
}


def normalize_mac(mac: str) -> str:
    """
    Нормализация MAC адреса к нижнему регистру с двоеточиями
    
    Args:
        mac: MAC адрес в любом формате
        
    Returns:
        Нормализованный MAC адрес (lowercase, с двоеточиями)
    """
    if not mac:
        return ""
    
    # Удаляем все разделители и приводим к нижнему регистру
    mac_clean = mac.replace(":", "").replace("-", "").replace(".", "").lower()
    
    # Проверяем валидность (12 hex символов)
    if len(mac_clean) != 12:
        return ""
    
    # Форматируем с двоеточиями
    return ":".join([mac_clean[i:i+2] for i in range(0, 12, 2)])


def is_randomized(mac: str, flag_r: Optional[int] = None) -> bool:
    """
    Определение, является ли MAC адрес рандомизированным
    
    Args:
        mac: MAC адрес
        flag_r: Флаг рандомизации из данных (0/1 или None)
        
    Returns:
        True если MAC рандомизирован, False иначе
    """
    # Если флаг передан, используем его
    if flag_r is not None:
        return bool(flag_r)
    
    # Иначе вычисляем по LAA bit (Local Administered Address)
    # LAA bit = второй младший бит первого октета
    # Если установлен (0x02), то MAC рандомизирован
    mac_normalized = normalize_mac(mac)
    if not mac_normalized:
        return False
    
    try:
        first_octet = int(mac_normalized.split(":")[0], 16)
        # Проверяем бит 0x02 (второй младший)
        return bool(first_octet & 0x02)
    except (ValueError, IndexError):
        return False


def vendor_by_oui(mac: str) -> Optional[str]:
    """
    Определение производителя по OUI (первые 3 октета MAC адреса)
    
    Args:
        mac: MAC адрес
        
    Returns:
        Название производителя или None
    """
    mac_normalized = normalize_mac(mac)
    if not mac_normalized:
        return None
    
    # Извлекаем первые 3 октета (OUI)
    oui = ":".join(mac_normalized.split(":")[:3]).lower()
    
    return OUI_VENDOR_MAP.get(oui)


def classify(mac: str, rssi: int, flag_r: Optional[int] = None) -> Dict:
    """
    Классификация устройства по MAC адресу
    
    Args:
        mac: MAC адрес
        rssi: Сила сигнала
        flag_r: Флаг рандомизации (0/1 или None)
        
    Returns:
        Словарь с классификацией:
        {
            "mac": "...",
            "rssi": ...,
            "randomized": true/false,
            "vendor": "...",
            "device_type": "smartphone" | "laptop" | "other",
            "device_brand": "apple"|"samsung"|null
        }
    """
    mac_normalized = normalize_mac(mac)
    if not mac_normalized:
        return {
            "mac": mac,
            "rssi": rssi,
            "randomized": False,
            "vendor": None,
            "device_type": "other",
            "device_brand": None
        }
    
    randomized = is_randomized(mac_normalized, flag_r)
    vendor = vendor_by_oui(mac_normalized)
    
    # Определение типа устройства
    device_type = "other"
    device_brand = None
    
    # Smartphone: Apple или Samsung (независимо от randomized)
    if vendor == "Apple":
        device_type = "smartphone"
        device_brand = "apple"
    elif vendor == "Samsung":
        device_type = "smartphone"
        device_brand = "samsung"
    
    # Laptop: Intel, Dell, HP, Lenovo, Apple (но только если НЕ randomized)
    elif vendor in {"Intel", "Dell", "HP", "Lenovo"} and not randomized:
        device_type = "laptop"
    elif vendor == "Apple" and not randomized:
        # Apple ноутбук (MacBook) - не рандомизированный MAC
        device_type = "laptop"
    
    return {
        "mac": mac_normalized,
        "rssi": rssi,
        "randomized": randomized,
        "vendor": vendor,
        "device_type": device_type,
        "device_brand": device_brand
    }


if __name__ == "__main__":
    # Self-test
    print("=== Device Classifier Self-Test ===\n")
    
    test_cases = [
        # (MAC, RSSI, flag_r, expected_type, expected_brand)
        ("00:1e:c2:aa:bb:cc", -63, None, "smartphone", "apple"),  # Apple iPhone
        ("00:12:fb:aa:bb:cc", -70, None, "smartphone", "samsung"),  # Samsung phone
        ("00:1b:21:aa:bb:cc", -55, 0, "laptop", None),  # Intel laptop (not randomized)
        ("00:1a:a0:aa:bb:cc", -60, 0, "laptop", None),  # Dell laptop
        ("00:1e:68:aa:bb:cc", -65, 0, "laptop", None),  # HP laptop
        ("00:1b:24:aa:bb:cc", -58, 0, "laptop", None),  # Lenovo laptop
        ("00:1e:c2:aa:bb:cc", -63, 1, "smartphone", "apple"),  # Apple iPhone (randomized, но все равно smartphone)
        ("00:1b:21:aa:bb:cc", -55, 1, "other", None),  # Intel но randomized -> other
        ("aa:bb:cc:dd:ee:ff", -70, None, "other", None),  # Unknown vendor
        ("02:00:00:aa:bb:cc", -65, None, "other", None),  # Randomized unknown (LAA bit set)
    ]
    
    for mac, rssi, flag_r, expected_type, expected_brand in test_cases:
        result = classify(mac, rssi, flag_r)
        status = "OK" if result["device_type"] == expected_type and result["device_brand"] == expected_brand else "FAIL"
        
        print(f"{status} MAC: {mac}")
        print(f"   RSSI: {rssi}, flag_r: {flag_r}")
        print(f"   Vendor: {result['vendor']}")
        print(f"   Randomized: {result['randomized']}")
        print(f"   Type: {result['device_type']} (expected: {expected_type})")
        print(f"   Brand: {result['device_brand']} (expected: {expected_brand})")
        print()
