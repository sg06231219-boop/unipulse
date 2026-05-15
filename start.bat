@echo off
chcp 65001 >nul
title UniPulse - 高校风向标

echo.
echo ╔════════════════════════════════════════╗
echo ║       UniPulse - 高校风向标            ║
echo ║       一键启动脚本                     ║
echo ╚════════════════════════════════════════╝
echo.

cd /d "%~dp0"

:: Check if dist exists
if not exist "dist\index.html" (
    echo [1/3] 构建前端...
    call npx vite build
    if errorlevel 1 (
        echo ❌ 构建失败！请检查 Node.js 是否安装。
        pause
        exit /b 1
    )
) else (
    echo [1/3] 前端已构建 ✓
)

:: Check if DB exists
if not exist "unipulse.db" (
    echo [2/3] 初始化数据库...
) else (
    echo [2/3] 数据库已存在 ✓
)

echo [3/3] 启动服务器...
echo.
echo ─────────────────────────────────────────
echo   🌐 访问地址: http://localhost:8000
echo   📊 API 文档: http://localhost:8000/docs
echo   ⏹️  停止服务: Ctrl+C
echo ─────────────────────────────────────────
echo.

:: Open browser after 2 seconds
start "" cmd /c "timeout /t 2 >nul && start http://localhost:8000"

:: Start server
C:\Users\LYS\AppData\Local\Python\bin\python.exe server.py

pause
