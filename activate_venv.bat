@echo off
REM Batch file to activate virtual environment (no execution policy needed)
call venv\Scripts\activate.bat
echo Virtual environment activated!
python -c "import sys; print('Python:', sys.executable)"

