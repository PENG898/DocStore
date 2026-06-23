@echo off
chcp 65001 >nul 2>nul
title 文存仓 DocStore
cd /d "%~dp0"

echo  ============================================
echo        文存仓 DocStore 正在启动中...
echo  ============================================
echo.

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
    echo  [i] 正在释放端口 8080 (PID: %%a^)...
    taskkill /F /PID %%a >nul 2>nul
)

echo  启动后请在浏览器中使用
echo  访问地址: http://localhost:8080/
echo.
"C:\\Program Files\\Python312\\python.exe" main.py
echo.
echo  文存仓已关闭或启动失败。
echo.
pause
