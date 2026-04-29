@echo off
echo Starting Network Traffic Monitor and Manager...
echo Checking administrative privileges...

net session >nul 2>&1
if %errorLevel% == 0 (
    echo Success: Administrative privileges confirmed.
) else (
    echo WARNING: This application requires Administrative privileges to block or limit traffic.
    echo Please restart this script as Administrator for full functionality.
    pause
)

if exist venv\Scripts\python.exe (
    .\venv\Scripts\python.exe main.py
) else (
    echo Error: Virtual environment (venv) not found.
    echo Please run the following command first:
    echo python -m venv venv
    echo .\venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
)
pause
