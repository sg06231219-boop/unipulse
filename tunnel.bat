@echo off
cd /d "%~dp0"
C:\Users\LYS\.qclaw\workspace\tools\cloudflared.exe tunnel --url http://localhost:8000 --no-autoupdate > tunnel.log 2>&1