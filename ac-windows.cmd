@echo off
setlocal DisableDelayedExpansion
wsl.exe -d Ubuntu-24.04 --cd ~ --exec /bin/sh -c "exec \"${XDG_DATA_HOME:-$HOME/.local/share}/ajan-atolyesi/ac\""
set "AA_RESULT=%ERRORLEVEL%"
if "%AA_RESULT%"=="0" exit /b 0
echo Ajan Atolyesi acilmadi. Once kur-windows.cmd ve docs\windows.md rehberini kontrol et.
pause
exit /b %AA_RESULT%
