@echo off
title UniPulse Backend
cd /d "%~dp0"
echo Starting UniPulse Backend... > server.log
C:\Users\LYS\AppData\Local\Python\bin\python.exe -m uvicorn server:app --reload --port 8000 --host 127.0.0.1 >> server.log 2>&1