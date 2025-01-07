@echo off
:: Check if Git is installed
echo Checking for Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git is not installed. Installing Git...

    :: Check if winget is available to install Git
    winget --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo winget is not available. Please install Git manually from https://git-scm.com/download/win
        exit /b 1
    ) else (
        echo Installing Git using winget...
        winget install --id Git.Git -e --source winget
    )

    :: Verify Git installation
    git --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Git installation failed. Exiting...
        exit /b 1
    )
)

:: Define variables for repository URL and directory names
set REPO_URL=https://github.com/HaXrDEV/Modpack-CLI-Tool
set REPO_DIR=Modpack-CLI-Tool

:: Check if the repository directory already exists
if exist %REPO_DIR% (
    echo Directory %REPO_DIR% already exists. Deleting it...
    rmdir /s /q %REPO_DIR%
)

:: Clone the repository
echo Cloning repository...
git clone %REPO_URL%

:: Check if cloning was successful
if not exist %REPO_DIR% (
    echo Repository clone failed. Exiting...
    exit /b 1
)

:: Change to the repository directory
cd %REPO_DIR%

:: Run the Python script
echo Running Modpack-Export.py...
python Modpack-Export.py

:: Check if Python executed successfully
if %errorlevel% neq 0 (
    echo Python script failed. Exiting...
    exit /b 1
)

:: Exit the script
echo Script execution completed successfully.
exit /b 0
