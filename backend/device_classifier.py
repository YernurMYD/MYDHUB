"""
Классификация устройств по MAC адресу.

Использует полную базу IEEE OUI (через mac-vendor-lookup) + правила маппинга
OEM-производителей Wi-Fi чипов к типу устройства + эвристику для рандомных MAC.

Типы устройств: smartphone, tablet, laptop, smartwatch, iot, other
"""
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────
# Инициализация mac-vendor-lookup (полная база IEEE OUI)
# ──────────────────────────────────────────────────────────────────────

_mac_lookup = None

def _get_mac_lookup():
    """Ленивая инициализация MacLookup (singleton)."""
    global _mac_lookup
    if _mac_lookup is None:
        try:
            from mac_vendor_lookup import MacLookup
            _mac_lookup = MacLookup()
            logger.info("mac-vendor-lookup инициализирован (полная IEEE OUI база)")
        except ImportError:
            logger.warning("mac-vendor-lookup не установлен — OUI поиск будет ограничен")
            _mac_lookup = False  # не пытаться повторно
        except Exception as e:
            logger.warning(f"Ошибка инициализации mac-vendor-lookup: {e}")
            _mac_lookup = False
    return _mac_lookup if _mac_lookup else None


# ──────────────────────────────────────────────────────────────────────
# Маппинг: ключевые слова в названии vendor → (тип, бренд)
#
# Порядок важен: первое совпадение побеждает.
# Проверяется вхождение ключа (lowercase) в vendor-строку (lowercase).
# ──────────────────────────────────────────────────────────────────────

_VENDOR_KEYWORDS: list[Tuple[str, str, Optional[str]]] = [
    # ── Смартфоны ─────────────────────────────────────────────────────
    # (ключевое слово,          device_type,   device_brand)
    ("apple",                   "smartphone",  "apple"),
    ("samsung electronics",     "smartphone",  "samsung"),
    ("samsung electro-mechanics","smartphone", "samsung"),
    ("xiaomi",                  "smartphone",  "xiaomi"),
    ("huawei",                  "smartphone",  "huawei"),
    ("honor device",            "smartphone",  "honor"),
    ("honor",                   "smartphone",  "honor"),
    ("google",                  "smartphone",  "google"),
    ("oneplus",                 "smartphone",  "oneplus"),
    ("oppo",                    "smartphone",  "oppo"),
    ("realme",                  "smartphone",  "realme"),
    ("vivo mobile",             "smartphone",  "vivo"),
    ("vivo",                    "smartphone",  "vivo"),
    ("motorola",                "smartphone",  "motorola"),
    ("lenovo",                  "smartphone",  "lenovo"),  # Lenovo делает и телефоны
    ("sony mobile",             "smartphone",  "sony"),
    ("sony",                    "smartphone",  "sony"),
    ("lg electronics",          "smartphone",  "lg"),
    ("lg innotek",              "smartphone",  "lg"),
    ("zte",                     "smartphone",  "zte"),
    ("meizu",                   "smartphone",  "meizu"),
    ("nokia",                   "smartphone",  "nokia"),
    ("hmd global",              "smartphone",  "nokia"),
    ("asus",                    "smartphone",  "asus"),
    ("tcl",                     "smartphone",  "tcl"),
    ("nothing technology",      "smartphone",  "nothing"),

    # ── Планшеты ──────────────────────────────────────────────────────
    ("amazon",                  "tablet",      "amazon"),

    # ── Ноутбуки (OEM Wi-Fi чипы, встречаются преимущественно в ноутбуках) ─
    ("intel corporate",         "laptop",      None),
    ("intel",                   "laptop",      None),
    ("azurewave",               "laptop",      None),
    ("liteon",                  "laptop",      None),
    ("rivet networks",          "laptop",      None),
    ("qualcomm",                "laptop",      None),
    ("mediatek",                "laptop",      None),
    ("dell",                    "laptop",      "dell"),
    ("hewlett packard",         "laptop",      "hp"),
    ("hp inc",                  "laptop",      "hp"),
    ("microsoft",               "laptop",      "microsoft"),

    # Foxconn / Cloud Network — делают Wi-Fi модули для ноутбуков
    ("cloud network technology","laptop",      None),
    ("hon hai",                 "laptop",      None),
    ("foxconn",                 "laptop",      None),
    ("wistron",                 "laptop",      None),
    ("compal",                  "laptop",      None),
    ("quanta",                  "laptop",      None),
    ("pegatron",                "laptop",      None),
    ("fibocom",                 "laptop",      None),

    # ── Умные часы / трекеры ──────────────────────────────────────────
    ("fitbit",                  "smartwatch",  "fitbit"),
    ("garmin",                  "smartwatch",  "garmin"),

    # ── IoT / камеры / роутеры ────────────────────────────────────────
    ("espressif",               "iot",         None),
    ("raspberry pi",            "iot",         None),
    ("hikvision",               "iot",         None),
    ("dahua",                   "iot",         None),
    ("tuya",                    "iot",         None),
    ("shenzhen ogemray",        "iot",         None),
    ("tp-link",                 "iot",         None),
    ("ubiquiti",                "iot",         None),
]


# ──────────────────────────────────────────────────────────────────────
# Функции
# ──────────────────────────────────────────────────────────────────────

def normalize_mac(mac: str) -> str:
    """
    Нормализация MAC адреса к нижнему регистру с двоеточиями.

    Args:
        mac: MAC адрес в любом формате

    Returns:
        Нормализованный MAC адрес (lowercase, с двоеточиями) или ""
    """
    if not mac:
        return ""

    mac_clean = mac.replace(":", "").replace("-", "").replace(".", "").lower()

    if len(mac_clean) != 12:
        return ""

    return ":".join([mac_clean[i:i+2] for i in range(0, 12, 2)])


def is_randomized(mac: str, flag_r: Optional[int] = None) -> bool:
    """
    Определение, является ли MAC адрес рандомизированным.

    Проверяет LAA-бит (Locally Administered Address — бит 1 первого октета).

    Args:
        mac: MAC адрес
        flag_r: Флаг рандомизации из данных сканера (0/1 или None)

    Returns:
        True если MAC рандомизирован, False иначе
    """
    if flag_r is not None:
        return bool(flag_r)

    mac_normalized = normalize_mac(mac)
    if not mac_normalized:
        return False

    try:
        first_octet = int(mac_normalized.split(":")[0], 16)
        return bool(first_octet & 0x02)
    except (ValueError, IndexError):
        return False


def vendor_by_oui(mac: str) -> Optional[str]:
    """
    Определение производителя по OUI через полную базу IEEE.

    Args:
        mac: MAC адрес

    Returns:
        Название производителя или None
    """
    mac_normalized = normalize_mac(mac)
    if not mac_normalized:
        return None

    lookup = _get_mac_lookup()
    if lookup is None:
        return None

    try:
        return lookup.lookup(mac_normalized)
    except Exception:
        return None


def _classify_by_vendor(vendor_raw: str) -> Tuple[str, Optional[str]]:
    """
    Определение типа устройства и бренда по строке vendor.

    Проверяет ключевые слова в названии вендора.

    Args:
        vendor_raw: Полное название вендора из IEEE базы

    Returns:
        (device_type, device_brand)
    """
    vendor_lower = vendor_raw.lower()

    for keyword, device_type, device_brand in _VENDOR_KEYWORDS:
        if keyword in vendor_lower:
            return device_type, device_brand

    return "other", None


def classify(mac: str, rssi: int, flag_r: Optional[int] = None) -> Dict:
    """
    Классификация устройства по MAC адресу.

    Логика:
    1. Определить vendor по полной IEEE OUI базе
    2. По vendor-строке определить тип и бренд (через keyword matching)
    3. Для laptop-вендоров: тип "laptop" только при не-рандомном MAC
    4. Для рандомных MAC без vendor: эвристика → "smartphone"

    Args:
        mac: MAC адрес
        rssi: Сила сигнала
        flag_r: Флаг рандомизации (0/1 или None)

    Returns:
        Словарь с классификацией
    """
    mac_normalized = normalize_mac(mac)
    if not mac_normalized:
        return {
            "mac": mac,
            "rssi": rssi,
            "randomized": False,
            "vendor": None,
            "device_type": "other",
            "device_brand": None,
        }

    randomized = is_randomized(mac_normalized, flag_r)
    vendor_raw = vendor_by_oui(mac_normalized)

    device_type = "other"
    device_brand = None

    if vendor_raw:
        device_type, device_brand = _classify_by_vendor(vendor_raw)

        # Laptop-OEM (Intel, AzureWave, Foxconn и т.д.) — тип "laptop"
        # только если MAC реальный. Рандомный MAC с OUI чипмейкера → "other".
        if device_type == "laptop" and randomized:
            device_type = "other"
            device_brand = None
    else:
        # Vendor не определён
        if randomized:
            # Подавляющее большинство рандомных probe request —
            # от смартфонов (iOS 14+, Android 10+).
            device_type = "smartphone"

    # Формируем короткое имя вендора для отображения
    vendor_display = _short_vendor_name(vendor_raw) if vendor_raw else None

    return {
        "mac": mac_normalized,
        "rssi": rssi,
        "randomized": randomized,
        "vendor": vendor_display,
        "device_type": device_type,
        "device_brand": device_brand,
    }


def _short_vendor_name(vendor_raw: str) -> str:
    """
    Сокращение длинного юридического названия вендора до короткого.

    'CLOUD NETWORK TECHNOLOGY SINGAPORE PTE. LTD.' → 'Cloud Network Tech.'
    'Samsung Electronics Co.,Ltd' → 'Samsung'
    'Apple, Inc.' → 'Apple'
    """
    # Маппинг известных длинных → коротких
    _SHORT_NAMES = {
        "apple": "Apple",
        "samsung electronics": "Samsung",
        "samsung electro-mechanics": "Samsung",
        "xiaomi": "Xiaomi",
        "beijing xiaomi": "Xiaomi",
        "huawei": "Huawei",
        "honor device": "Honor",
        "google": "Google",
        "oneplus": "OnePlus",
        "oppo": "OPPO",
        "realme": "Realme",
        "vivo mobile": "Vivo",
        "vivo": "Vivo",
        "motorola": "Motorola",
        "lenovo": "Lenovo",
        "sony": "Sony",
        "lg electronics": "LG",
        "lg innotek": "LG",
        "zte": "ZTE",
        "meizu": "Meizu",
        "nokia": "Nokia",
        "hmd global": "Nokia",
        "asus": "ASUS",
        "tcl": "TCL",
        "nothing technology": "Nothing",
        "intel corporate": "Intel",
        "intel": "Intel",
        "azurewave": "AzureWave",
        "liteon": "Liteon",
        "qualcomm": "Qualcomm",
        "mediatek": "MediaTek",
        "dell": "Dell",
        "hewlett packard": "HP",
        "hp inc": "HP",
        "microsoft": "Microsoft",
        "cloud network technology": "Foxconn",
        "cloud network tech": "Foxconn",
        "hon hai": "Foxconn",
        "foxconn": "Foxconn",
        "fibocom": "Fibocom",
        "amazon": "Amazon",
        "fitbit": "Fitbit",
        "garmin": "Garmin",
        "espressif": "Espressif",
        "raspberry pi": "Raspberry Pi",
        "hikvision": "Hikvision",
        "dahua": "Dahua",
        "tp-link": "TP-Link",
        "ubiquiti": "Ubiquiti",
    }

    vendor_lower = vendor_raw.lower()
    for key, short in _SHORT_NAMES.items():
        if key in vendor_lower:
            return short

    # Если не нашли в маппинге — обрезаем юридические суффиксы
    import re
    # Заменяем unicode-пробелы на обычные
    name = re.sub(r'\s+', ' ', vendor_raw)
    for suffix in [" Co.,Ltd", " Co., Ltd.", " Inc.", " Corp.", " Corporation",
                   " PTE. LTD.", " Pte. Ltd.", " Ltd.", " Ltd", " LLC",
                   " GmbH", " AG", " S.A.", " Limited"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break

    return name.strip()


if __name__ == "__main__":
    # Self-test
    print("=== Device Classifier Self-Test ===\n")

    test_cases = [
        # (MAC, RSSI, flag_r, expected_type, description)
        ("aa:bb:cc:dd:ee:ff", -70, None, "smartphone", "Random MAC, unknown vendor -> smartphone"),
        ("02:00:00:aa:bb:cc", -65, None, "smartphone", "Random MAC (LAA bit) -> smartphone"),
        ("aa:bb:cc:dd:ee:ff", -70, 0, "other", "Non-random, unknown vendor -> other"),
    ]

    passed = 0
    failed = 0

    for mac, rssi, flag_r, expected_type, desc in test_cases:
        result = classify(mac, rssi, flag_r)
        ok = result["device_type"] == expected_type
        status = "OK" if ok else "FAIL"
        passed += ok
        failed += (not ok)

        print(f"{status} {desc}")
        print(f"   MAC={mac}, flag_r={flag_r}")
        print(f"   vendor={result['vendor']}, type={result['device_type']}, "
              f"brand={result['device_brand']}, rand={result['randomized']}")
        print()

    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
