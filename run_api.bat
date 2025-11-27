@echo off
REM Film Öneri API — Windows Başlangıç Script'i

echo ==========================================
echo Film Oneri API - Baslatici Script
echo ==========================================
echo.

REM Ortam degiskenleri kontrol et
echo Ortam degiskenleri kontrol ediliyor...
if "%DB_USER%"=="" (
    echo [HATA] DB_USER ortam degiskeni ayarlanmamis!
    echo.
    echo Lutfen asagidaki komutlari calistir (CMD admin):
    echo setx DB_USER "postgres"
    echo setx DB_PASSWORD "senin_sifren"
    echo setx DB_HOST "localhost"
    echo setx DB_PORT "5432"
    echo setx DB_NAME "film_oneri"
    echo setx SECRET_KEY "film-oneri-secret-key-12345"
    pause
    exit /b 1
)
echo [OK] Ortam degiskenleri yapilandi.
echo.

REM Python kontrol et
echo Python kontrol ediliyor...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python kurulu degil!
    echo Lutfen Python 3.10+ yukle: https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python bulundu.
echo.

REM Baglantilari yukle
echo Baglantilari yukleniyor...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [HATA] Baglantilari yukleme basarisiz!
    pause
    exit /b 1
)
echo [OK] Baglantilari yuklendi.
echo.

REM Uvicorn basla
echo.
echo ==========================================
echo API Sunucusu Baslatiliyor...
echo ==========================================
echo.
echo Tarayicida acarsan: http://localhost:8000
echo Swagger UI: http://localhost:8000/docs
echo.
echo (Cikis icin CTRL+C'ye basin)
echo.

uvicorn app:app --reload --host 0.0.0.0 --port 8000

pause
