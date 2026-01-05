@echo off
setlocal EnableDelayedExpansion

REM ===== Config =====
set DEVICE_FILE=device.txt
set WAIT_MS=1200
REM ==================

REM Read device id from device.txt (ONE LINE)
if not exist "%DEVICE_FILE%" (
  echo [ERROR] Missing %DEVICE_FILE%
  echo Create %DEVICE_FILE% with ONE LINE device id, e.g.:
  echo 26111JEGR11210
  exit /b 1
)

set /p DEVICE=<"%DEVICE_FILE%"
set DEVICE=%DEVICE: =%

if "%DEVICE%"=="" (
  echo [ERROR] %DEVICE_FILE% is empty.
  exit /b 1
)

set N=%~1
if "%N%"=="" (
  echo Usage: %~nx0 ^<number^>
  exit /b 1
)

REM Validate number (digits only)
for /f "delims=0123456789" %%A in ("%N%") do (
  echo [ERROR] number must be digits only. Example: %~nx0 1
  exit /b 1
)

REM Format to 2-digit: 01,02,...,99
set NAME=00%N%
set NAME=!NAME:~-2!

echo ==== DEVICE=%DEVICE%  SHOT=%NAME%.png ====

REM Optional small wait for UI to settle
powershell -NoProfile -Command "Start-Sleep -Milliseconds %WAIT_MS%"

REM Screenshot to current folder
adb -s %DEVICE% exec-out screencap -p > "%NAME%.png"

if exist "%NAME%.png" (
  echo Done. %NAME%.png
) else (
  echo [ERROR] Screenshot not created.
  exit /b 1
)

endlocal
