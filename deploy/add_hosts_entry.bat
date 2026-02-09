@echo off
:: Add ilab.psu.palawan.edu.ph -> 127.0.0.1 to hosts file. RUN AS ADMINISTRATOR (right-click -> Run as administrator)
set HOSTSFILE=%SystemRoot%\System32\drivers\etc\hosts
findstr /C:"ilab.psu.palawan.edu.ph" "%HOSTSFILE%" >nul 2>&1 && (
    echo Entry for ilab.psu.palawan.edu.ph already exists in hosts.
) || (
    echo 127.0.0.1 ilab.psu.palawan.edu.ph>> "%HOSTSFILE%"
    echo Added: 127.0.0.1 ilab.psu.palawan.edu.ph
)
pause
