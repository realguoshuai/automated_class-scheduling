@echo off
rem Pure ASCII to avoid encoding issues
echo [*] Launching Python-based Build Tool...
python build_process.py
if %ERRORLEVEL% NEQ 0 (
    echo [-] Python is not found or build failed. Please install Python.
)
pause
