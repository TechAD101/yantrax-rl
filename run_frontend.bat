@echo off
REM ---- Move to the frontend directory ----
cd /d "%~dp0frontend"

REM ---- Add Node.js portable path (if not already set for this session) ----
set PATH=C:\Users\ABhati\Documents\yantrax_node\node-v20.12.2-win-x64;%PATH%

echo.
echo 📦 Installing dependencies...
call npm install

echo.
echo 🚀 Starting Yantra X frontend with Vite...
call npx vite

pause
