@echo off
setlocal enabledelayedexpansion

:: ----------------------------------------
:: Configuration
:: ----------------------------------------
set "REPO_URL=https://github.com/HaXrDEV/Modpack-CLI-Tool"
set "REPO_DIR=Modpack-CLI-Tool"
set "UPDATE_DEPS=0"

set "WORKDIR=%cd%"
set "REPO_ABS=%WORKDIR%\%REPO_DIR%"
set "VENV_DIR=%REPO_ABS%\venv"

:: ----------------------------------------
:: Check for Git
:: ----------------------------------------
echo Checking for Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git is not installed. Installing Git...
    if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\winget.exe" (
        echo Installing Git using winget...
        "%LOCALAPPDATA%\Microsoft\WindowsApps\winget.exe" install --id Git.Git -e --source winget
    ) else (
        echo winget is not available. Please install Git manually...
        pause
        exit /b 1
    )
    git --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Git installation failed. Exiting...
        pause
        exit /b 1
    )
)

:: ----------------------------------------
:: Check for Java (any version; ask before installing)
:: ----------------------------------------
echo Checking for Java...
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo Java not found.
    set /p INSTALL_JAVA=Install Microsoft OpenJDK 17 via winget now? [Y/N]: 
    if /i "!INSTALL_JAVA!"=="Y" (
        if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\winget.exe" (
            "%LOCALAPPDATA%\Microsoft\WindowsApps\winget.exe" install --id Microsoft.OpenJDK.17 -e --source winget
        ) else (
            echo winget is not available. Please install Java manually and re-run.
            pause
            exit /b 1
        )
        rem Re-check after install
        java -version >nul 2>&1
        if %errorlevel% neq 0 (
            echo Java installation appears to have failed. Exiting...
            pause
            exit /b 1
        )
    ) else (
        echo Aborting per user choice. Java is required to bootstrap Packwiz.
        pause
        exit /b 1
    )
)

:: ----------------------------------------
:: Print detected Java version (no findstr needed)
:: This grabs the 3rd token from the first line of `java -version`
:: e.g. 'openjdk version "17.0.10"' -> token 3 is "17.0.10"
set "JAVA_VERSION="
for /f "tokens=3" %%v in ('java -version 2^>^&1') do (
    set "JAVA_VERSION=%%~v"
    goto :got_java_version
)
:got_java_version
set "JAVA_VERSION=%JAVA_VERSION:"=%"
if not defined JAVA_VERSION set "JAVA_VERSION=unknown"
echo Using Java %JAVA_VERSION%

:: ----------------------------------------
:: Find Python 3.11
:: ----------------------------------------
echo Searching for Python 3.11...
set "PYTHON_CMD="
set "PREFERRED_VERS=3.11"

where py >nul 2>&1
if %errorlevel%==0 (
    for /f "delims=" %%v in ('py -3.11 -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_CMD=%%v"
)

if not defined PYTHON_CMD (
    for %%P in (
        "%LocalAppData%\Microsoft\WindowsApps\python3.11.exe"
        "%ProgramFiles%\Python311\python.exe"
        "%ProgramFiles(x86)%\Python311\python.exe"
        "%UserProfile%\AppData\Local\Programs\Python\Python311\python.exe"
    ) do (
        if exist "%%~P" (
            set "PYTHON_CMD=%%~P"
            goto :FOUND_PYTHON
        )
    )
)

if not defined PYTHON_CMD (
    for /f "delims=" %%F in ('where python 2^>nul') do (
        for /f "delims=" %%V in ('"%%F" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2^>nul') do (
            if "%%V"=="%PREFERRED_VERS%" (
                set "PYTHON_CMD=%%~F"
                goto :FOUND_PYTHON
            )
        )
    )
)

:FOUND_PYTHON
if not defined PYTHON_CMD (
    echo Python %PREFERRED_VERS% not found.
    echo Please install Python 3.11 from: https://www.python.org/downloads/release/python-3110/
    pause
    exit /b 1
)

"%PYTHON_CMD%" -c "import sys; print(f'Using Python {sys.version_info.major}.{sys.version_info.minor} at {sys.executable}')"

:: ----------------------------------------
:: Clone or update repository
:: ----------------------------------------
for /f "tokens=1" %%i in ('git ls-remote "%REPO_URL%" HEAD') do set "REMOTE_HASH=%%i"

if exist "%REPO_ABS%" (
    pushd "%REPO_ABS%" >nul
    if exist ".git" (
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
            rmdir /s /q "%REPO_ABS%"
            set "UPDATE_DEPS=1"
        )
    ) else (
        echo Directory exists but is not a Git repository. Deleting...
        popd >nul
        rmdir /s /q "%REPO_ABS%"
        set "UPDATE_DEPS=1"
    )
) else (
    set "UPDATE_DEPS=1"
)

if "%UPDATE_DEPS%"=="1" (
    echo Cloning repository...
    git clone "%REPO_URL%" "%REPO_ABS%"
    if not exist "%REPO_ABS%" (
        echo Repository clone failed. Exiting...
        pause
        exit /b 1
    )
)

:: ----------------------------------------
:: Set up virtual environment (ABSOLUTE PATHS)
:: ----------------------------------------
:SETUP_ENV
if not exist "%VENV_DIR%" (
    echo Creating Python virtual environment in "%VENV_DIR%"...
    "%PYTHON_CMD%" -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment. Exiting...
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists.
)

set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
if not exist "%VENV_PYTHON%" (
    echo Virtual environment Python executable not found at:
    echo   "%VENV_PYTHON%"
    echo Consider installing Python from https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

:: ----------------------------------------
:: Move into the repo directory safely
:: ----------------------------------------
pushd "%REPO_ABS%" >nul

:: ----------------------------------------
:: Install dependencies
:: ----------------------------------------
if "%UPDATE_DEPS%"=="1" (
    if exist "requirements.txt" (
        echo Installing dependencies from requirements.txt...
        "%VENV_PYTHON%" -m pip install --upgrade pip >nul 2>&1
        "%VENV_PYTHON%" -m pip install -r requirements.txt
        if %errorlevel% neq 0 (
            echo Failed to install dependencies. Exiting...
            popd >nul
            pause
            exit /b 1
        )
    ) else (
        echo No requirements.txt found. Skipping dependency installation.
    )
) else (
    echo Dependencies update not needed; skipping installation.
)

:: ----------------------------------------
:: Run the main script
:: ----------------------------------------
echo Running Modpack-Export.py...
"%VENV_PYTHON%" "%REPO_ABS%\Modpack-Export.py"
if %errorlevel% neq 0 (
    echo Python script failed. Exiting...
    popd >nul
    pause
    exit /b 1
)

echo Script execution completed successfully.
popd >nul
pause
exit /b 0
