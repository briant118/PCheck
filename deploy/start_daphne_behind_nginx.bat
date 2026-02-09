@echo off
echo Starting PCheck (Daphne) for use behind Nginx - listening on 127.0.0.1:8000
cd /d "%~dp0.."
if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
set DJANGO_SETTINGS_MODULE=PCheckMain.settings
python -m daphne -b 127.0.0.1 -p 8000 PCheckMain.asgi:application
pause
