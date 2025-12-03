@echo off
:: ------------------------------------------------------------
:: Friday Screen Time Tracker - Auto Start Script
:: ------------------------------------------------------------
:: This script launches the screen_time_tracker.py file silently
:: using the Python interpreter from your FRI-D.A.Y environment.
:: ------------------------------------------------------------

REM === Full path to your Python interpreter ===
set PYTHONW="C:\Users\User\anaconda3\envs\FRI-D.A.Y\pythonw.exe"

REM === Full path to your Python script ===
set SCRIPT_PATH="C:\Users\User\Desktop\FRI-D.A.Y\resources\screentime\screen_time_tracker.py"

REM === Optional delay to let system finish loading ===
timeout /t 10 /nobreak >nul

REM === Run the tracker silently ===
start "" %PYTHONW% %SCRIPT_PATH%

REM === Log the run time (optional, can help debugging) ===
echo [%date% %time%] Screen Time Tracker launched >> "C:\Users\User\Desktop\FRI-D.A.Y\resources\screentime\tracker_status.log"

REM === Exit cleanly ===
exit
