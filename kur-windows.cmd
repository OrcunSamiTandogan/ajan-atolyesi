@echo off
setlocal DisableDelayedExpansion
where wsl.exe >nul 2>&1
if errorlevel 1 goto no_wslg
wsl.exe -d Ubuntu-24.04 --exec /usr/bin/test -d /mnt/wslg
if errorlevel 1 goto no_wslg
pushd "%~dp0" || goto failed
wsl.exe -d Ubuntu-24.04 -- bash ./masaustune-kur.sh
set "AA_RESULT=%ERRORLEVEL%"
if not "%AA_RESULT%"=="0" goto failed_in_source
echo Ajan Atolyesi kuruldu. Pencere aciliyor...
echo Yeniden acmak icin bu klasordeki ac-windows.cmd dosyasini kullan.
call .\ac-windows.cmd
set "AA_RESULT=%ERRORLEVEL%"
popd
exit /b %AA_RESULT%

:failed_in_source
popd
goto failed

:no_wslg
echo Ubuntu-24.04 veya WSLg hazir degil. docs\windows.md rehberini ac.
pause
exit /b 1

:failed
echo Kurulum olmadi. docs\windows.md rehberini ac.
pause
exit /b 1
