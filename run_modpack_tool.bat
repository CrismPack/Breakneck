@echo off

:: Change to the repository directory
cd Modpack-CLI-Tool

:: Activate the existing virtual environment located one level up
call "..\venv\Scripts\activate.bat"

:: Run the Python script
python Modpack-Export.py
if %errorlevel% neq 0 (
    echo Python script failed. Exiting...
    pause
    exit /b 1
)

pause
