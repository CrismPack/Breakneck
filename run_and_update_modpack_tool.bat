@echo off
setlocal enabledelayedexpansion

:: Define virtual environment directory outside the repo
set VENV_DIR=venv

:: Check if Git is installed
echo Checking for Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git is not installed. Installing Git...
    winget --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo winget is not available. Please install Git manually from https://git-scm.com/download/win
        pause
        exit /b 1
    ) else (
        echo Installing Git using winget...
        winget install --id Git.Git -e --source winget
    )

    git --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Git installation failed. Exiting...
        pause
        exit /b 1
    )
)

:: Check if Python is installed
echo Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install it from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Define repository variables
set REPO_URL=https://github.com/HaXrDEV/Modpack-CLI-Tool
set REPO_DIR=Modpack-CLI-Tool

:: Get remote HEAD commit hash (only the hash)
for /f "tokens=1" %%i in ('git ls-remote %REPO_URL% HEAD') do set "REMOTE_HASH=%%i"

:: Check if the repository directory exists
if exist %REPO_DIR% (
    pushd %REPO_DIR% >nul

    :: Check if it's a git repo
    if exist .git (
        for /f "delims=" %%j in ('git rev-parse HEAD') do set "LOCAL_HASH=%%j"

        echo Remote: [!REMOTE_HASH!]
        echo Local : [!LOCAL_HASH!]

        if /i "!LOCAL_HASH!"=="!REMOTE_HASH!" (
            echo Repository is up to date. Skipping clone.
            popd >nul
            goto SETUP_ENV
        ) else (
            echo Repository is outdated. Re-cloning...
            popd >nul
            rmdir /s /q %REPO_DIR%
        )
    ) else (
        echo Directory exists but is not a Git repository. Deleting...
        popd >nul
        rmdir /s /q %REPO_DIR%
    )
)

:: Clone the repository
echo Cloning repository...
git clone %REPO_URL%

if not exist %REPO_DIR% (
    echo Repository clone failed. Exiting...
    pause
    exit /b 1
)

:SETUP_ENV
:: Create virtual environment in the main directory
if not exist %VENV_DIR% (
    echo Creating Python virtual environment in "%cd%\%VENV_DIR%"...
    python -m venv %VENV_DIR%
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment. Exiting...
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists.
)

:: Activate the virtual environment
call %VENV_DIR%\Scripts\activate.bat

:: Navigate into the cloned repo
cd %REPO_DIR%

:: Install dependencies from requirements.txt if it exists
if exist requirements.txt (
    echo Installing dependencies from requirements.txt...
    python -m pip install --upgrade pip >nul
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install dependencies. Exiting...
        pause
        exit /b 1
    )
) else (
    echo No requirements.txt found. Skipping dependency installation.
)

:: Run the Python script using the virtual environment
echo Running Modpack-Export.py...
python Modpack-Export.py
if %errorlevel% neq 0 (
    echo Python script failed. Exiting...
    pause
    exit /b 1
)

echo Script execution completed successfully.
pause
exit /b 0
