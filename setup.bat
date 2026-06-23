@echo off
chcp 65001 >nul 2>nul
setlocal
title 文存仓 DocStore - 安装配置向导

echo.
echo  ============================================
echo    文存仓 DocStore - 安装配置
echo  ============================================
echo.

set "PY="
for %%C in (py -3 python python3) do (
    %%C --version >nul 2>&1
    if not errorlevel 1 (set "PY=%%C" & goto :found)
)

for %%V in (313 312 311 310) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" (
        set "PY=%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
        goto :found
    )
)

echo  [!] 未检测到 Python 环境
echo.
echo  --------------------------------------------
echo   请先安装 Python 3.10+:
echo   下载地址: https://www.python.org/downloads/
echo  --------------------------------------------
echo.
echo   [重要] 安装时务必勾选 "Add Python to PATH"
echo   否则本工具将无法正常运行!
echo.
echo   安装完成后重新运行此脚本
echo.
echo  按任意键打开下载页面...
pause >nul
start https://www.python.org/downloads/
exit /b 1

:found
echo  [√] Python: %PY%
echo.
cd /d "%~dp0"
%PY% setup.py
if errorlevel 1 (
    echo.
    echo  [!] 安装配置失败，请检查上方错误信息
)
echo.
pause