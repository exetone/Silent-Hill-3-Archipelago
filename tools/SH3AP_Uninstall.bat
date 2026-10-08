@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "TOGGLE=%~dp0SH3AP_Mode_Toggle.bat"
if not exist "%TOGGLE%" (
  echo ERROR: SH3AP_Mode_Toggle.bat is missing beside this file.
  pause
  exit /b 1
)

echo ============================================================
echo   SH3AP NON-DESTRUCTIVE UNINSTALL
echo ============================================================
echo.
echo This puts the game into SH3AP-OFF / vanilla mode.
echo AP saves and AP state files are PRESERVED for a later reinstall.
echo PC Fix, controller trigger support, ASI loader and other non-SH3AP mods are untouched.
echo XInputPlus files are never removed, renamed, disabled, or rewritten by this uninstaller.
echo Current key.ini and disp.ini options are carried into Vanilla instead of being swapped.
echo.
echo If SH3AP is currently ON, the mode switch will disable it now.
echo If it is already OFF, nothing needs to be changed.
echo.

call "%TOGGLE%" Vanilla
exit /b %ERRORLEVEL%
