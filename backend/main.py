"""
Главный файл для запуска MQTT Consumer и API
"""
import logging
import signal
import sys
import threading
from typing import Optional

from storage import WiFiDataStorage
from mqtt_consumer import MQTTConsumer
from dashboard_api import app, init_api
from config import API_HOST, API_PORT

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WiFiMonitoringService:
    """Основной сервис мониторинга Wi-Fi"""
    
    def __init__(self):
        """Инициализация сервиса"""
        self.storage = WiFiDataStorage()
        self.consumer: Optional[MQTTConsumer] = None
        self.api_thread: Optional[threading.Thread] = None
        self.running = False
    
    def start(self):
        """Запуск сервиса"""
        logger.info("Запуск сервиса Wi-Fi мониторинга...")
        
        # Инициализация API
        init_api(self.storage)
        
        # Запуск MQTT consumer
        self.consumer = MQTTConsumer(self.storage)
        self.consumer.start()
        
        # Запуск API в отдельном потоке
        self.api_thread = threading.Thread(
            target=lambda: app.run(host=API_HOST, port=API_PORT, debug=False),
            daemon=True
        )
        self.api_thread.start()
        logger.info(f"API запущен на http://{API_HOST}:{API_PORT}")
        
        self.running = True
        logger.info("Сервис Wi-Fi мониторинга запущен")
    
    def stop(self):
        """Остановка сервиса"""
        logger.info("Остановка сервиса Wi-Fi мониторинга...")
        self.running = False
        
        if self.consumer:
            self.consumer.stop()
        
        logger.info("Сервис Wi-Fi мониторинга остановлен")


def main():
    """Главная функция"""
    service = WiFiMonitoringService()
    
    # Обработка сигналов для корректного завершения
    def signal_handler(sig, frame):
        logger.info("Получен сигнал завершения")
        service.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        service.start()
        
        # Ожидание завершения
        while service.running:
            import time
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Прервано пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        service.stop()


if __name__ == "__main__":
    main()
