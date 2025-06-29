@echo off
set "NODEJS_PATH=%CD%\frontend\nodejs\node-v22.17.0-win-x64"
set "PATH=%NODEJS_PATH%;%PATH%"
cd /d "%CD%\frontend"
npm run dev -- --force
pause
