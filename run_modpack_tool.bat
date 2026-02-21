@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_DIR="

if exist "%SCRIPT_DIR%Modpack-Export.py" set "REPO_DIR=%SCRIPT_DIR%"
if not defined REPO_DIR if exist "%SCRIPT_DIR%Modpack-CLI-Tool\Modpack-Export.py" set "REPO_DIR=%SCRIPT_DIR%Modpack-CLI-Tool"
if not defined REPO_DIR if exist "%SCRIPT_DIR%..\Modpack-Export.py" set "REPO_DIR=%SCRIPT_DIR%.."
if not defined REPO_DIR if exist "%SCRIPT_DIR%..\Modpack-CLI-Tool\Modpack-Export.py" set "REPO_DIR=%SCRIPT_DIR%..\Modpack-CLI-Tool"

if not defined REPO_DIR (
    echo Could not locate Modpack-CLI-Tool directory.
    echo Expected to find Modpack-Export.py near:
    echo   %SCRIPT_DIR%
    pause
    exit /b 1
)

pushd "%REPO_DIR%" >nul

set "VENV_PY=%CD%\venv\Scripts\python.exe"
if not exist "%VENV_PY%" (
    echo Virtual environment not found. Creating one...
    set "PYTHON_CMD="

    where py >nul 2>&1
    if %errorlevel%==0 (
        for /f "delims=" %%P in ('py -3.11 -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_CMD=%%P"
        if not defined PYTHON_CMD (
            for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_CMD=%%P"
        )
    )

    if not defined PYTHON_CMD (
        for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_CMD=%%P"
    )

    if not defined PYTHON_CMD (
        echo No usable Python interpreter found to create venv.
        popd >nul
        pause
        exit /b 1
    )

    "%PYTHON_CMD%" -m venv "%CD%\venv"
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        popd >nul
        pause
        exit /b 1
    )
)

if not exist "%VENV_PY%" (
    echo Virtual environment Python not found at:
    echo   %VENV_PY%
    popd >nul
    pause
    exit /b 1
)

if exist "requirements.txt" (
    echo Installing dependencies from requirements.txt...
    "%VENV_PY%" -m pip install --upgrade pip
    if %errorlevel% neq 0 (
        echo Failed to upgrade pip.
        popd >nul
        pause
        exit /b 1
    )

    "%VENV_PY%" -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Dependency installation failed.
        popd >nul
        pause
        exit /b 1
    )
) else (
    echo requirements.txt not found. Skipping dependency installation.
)

echo Running Modpack-Export.py...
"%VENV_PY%" "%CD%\Modpack-Export.py"
if %errorlevel% neq 0 (
    echo Python script failed.
    popd >nul
    pause
    exit /b 1
)

popd >nul
pause
exit /b 0
