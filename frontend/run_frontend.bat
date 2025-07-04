@echo off
echo.
echo 📦 Installing dependencies...
call "C:\Users\ABhati\Documents\yantrax_node\node-v20.12.2-win-x64\npm.cmd" install

echo.
echo 🚀 Starting Yantra X frontend with Vite...

REM Set local Node path
set PATH=C:\Users\ABhati\Documents\yantrax_node\node-v20.12.2-win-x64;%PATH%

REM Run dev server
call "C:\Users\ABhati\Documents\yantrax_node\node-v20.12.2-win-x64\npx.cmd" vite

pause
