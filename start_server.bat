@echo off
echo Starting PCheck (self-hosted - Daphne)...
cd /d %~dp0
if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
set DJANGO_SETTINGS_MODULE=PCheckMain.settings
python -m daphne -b 0.0.0.0 -p 8000 PCheckMain.asgi:application
pause

