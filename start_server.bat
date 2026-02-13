@echo off
REM Скрипт запуска сервера Wi-Fi мониторинга на Windows
REM Запустите этот файл для старта MQTT Consumer и API

echo ========================================
echo Запуск сервера Wi-Fi мониторинга
echo ========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo Установите Python 3.7 или выше
    pause
    exit /b 1
)

REM Проверка зависимостей
echo Проверка зависимостей...
python -m pip show paho-mqtt >nul 2>&1
if errorlevel 1 (
    echo Установка зависимостей...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ОШИБКА: Не удалось установить зависимости
        pause
        exit /b 1
    )
)

echo.
echo Запуск сервера...
echo.
echo Сервер будет доступен на:
echo   - API: http://localhost:5000
echo   - MQTT: localhost:1883
echo.
echo Для остановки нажмите Ctrl+C
echo.

python main.py

pause
