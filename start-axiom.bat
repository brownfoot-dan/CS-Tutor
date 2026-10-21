@echo off
title Axiom CS Tutor
echo.
echo  ============================================
echo   Axiom CS Tutor
echo  ============================================
echo.

:: Check if Ollama is already running
tasklist /fi "imagename eq ollama.exe" 2>nul | find /i "ollama.exe" >nul
if %errorlevel%==0 (
    echo  [OK] Ollama is already running.
) else (
    echo  [..] Starting Ollama...
    start "" /min "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
    timeout /t 3 /nobreak >nul
    echo  [OK] Ollama started.
)

echo  [..] Starting web server on http://localhost:5000
echo.

:: Open browser after a short delay
start "" "http://localhost:5000"

:: Run Python server (this keeps the window alive)
set PYTHONUTF8=1
py "%~dp0serve.py"

echo.
echo  Server stopped.
pause
