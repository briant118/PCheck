@echo off
echo ========================================
echo Configuring Ngrok with Auth Token
echo ========================================
echo.

REM Check if ngrok is in the current directory
if exist "ngrok.exe" (
    echo Found ngrok.exe in current directory
    ngrok.exe config add-authtoken 35ZI7RgaYdaKYG5iTotWLwUPRre_i5vaQ7UVVkQFSGpGjWBB
) else (
    REM Try to use ngrok from PATH
    where ngrok >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo Using ngrok from PATH
        ngrok config add-authtoken 35ZI7RgaYdaKYG5iTotWLwUPRre_i5vaQ7UVVkQFSGpGjWBB
    ) else (
        echo ERROR: ngrok.exe not found!
        echo.
        echo Please either:
        echo 1. Place ngrok.exe in this directory, OR
        echo 2. Add ngrok to your PATH environment variable
        echo.
        echo Download ngrok from: https://ngrok.com/download
        pause
        exit /b 1
    )
)

echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================
    echo Ngrok configured successfully!
    echo ========================================
    echo.
    echo You can now start ngrok using:
    echo   START-NGROK.bat
    echo.
) else (
    echo ========================================
    echo ERROR: Failed to configure ngrok
    echo ========================================
    echo.
    echo Please check:
    echo 1. Ngrok is installed correctly
    echo 2. You have internet connection
    echo 3. The authtoken is valid
    echo.
)

pause

