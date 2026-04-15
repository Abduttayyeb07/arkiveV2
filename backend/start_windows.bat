:: This method is not recommended, and we recommend you use the `start.sh` file with WSL instead.
@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: Get the directory of the current script
SET "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%" || exit /b

SET "PYTHON_CMD="
IF NOT "%VIRTUAL_ENV%"=="" IF EXIST "%VIRTUAL_ENV%\Scripts\python.exe" SET "PYTHON_CMD=%VIRTUAL_ENV%\Scripts\python.exe"
IF "%PYTHON_CMD%"=="" IF EXIST "%SCRIPT_DIR%..\.venv\Scripts\python.exe" SET "PYTHON_CMD=%SCRIPT_DIR%..\.venv\Scripts\python.exe"
IF "%PYTHON_CMD%"=="" (
    WHERE python >nul 2>&1 && SET "PYTHON_CMD=python"
)
IF "%PYTHON_CMD%"=="" (
    echo Python was not found in PATH.
    exit /b 1
)

:: Add conditional Playwright browser installation
IF /I "%WEB_LOADER_ENGINE%" == "playwright" (
    IF "%PLAYWRIGHT_WS_URL%" == "" (
        echo Installing Playwright browsers...
        playwright install chromium
        playwright install-deps chromium
    )

    python -c "import nltk; nltk.download('punkt_tab')"
)

SET "KEY_FILE=.arkive_secret_key"
IF NOT "%ARKIVE_SECRET_KEY_FILE%" == "" (
    SET "KEY_FILE=%ARKIVE_SECRET_KEY_FILE%"
)

IF "%PORT%"=="" SET PORT=8080
IF "%HOST%"=="" SET HOST=0.0.0.0
IF "%FORWARDED_ALLOW_IPS%"=="" SET "FORWARDED_ALLOW_IPS=*"
SET "ARKIVE_SECRET_KEY=%ARKIVE_SECRET_KEY%"
SET "ARKIVE_JWT_SECRET_KEY=%ARKIVE_JWT_SECRET_KEY%"

IF "%DATA_DIR%"=="" SET "DATA_DIR=%SCRIPT_DIR%data"
IF NOT EXIST "%DATA_DIR%" mkdir "%DATA_DIR%"

:: Check if ARKIVE_SECRET_KEY and ARKIVE_JWT_SECRET_KEY are not set
IF "%ARKIVE_SECRET_KEY% %ARKIVE_JWT_SECRET_KEY%" == " " (
    echo Loading ARKIVE_SECRET_KEY from file, not provided as an environment variable.

    IF NOT EXIST "%KEY_FILE%" (
        echo Generating ARKIVE_SECRET_KEY
        "%PYTHON_CMD%" -c "import secrets; print(secrets.token_urlsafe(32))" > "%KEY_FILE%"
        echo ARKIVE_SECRET_KEY generated
    )

    echo Loading ARKIVE_SECRET_KEY from %KEY_FILE%
    SET /p ARKIVE_SECRET_KEY=<"%KEY_FILE%"
)

:: Execute uvicorn
SET "ARKIVE_SECRET_KEY=%ARKIVE_SECRET_KEY%"
IF "%UVICORN_WORKERS%"=="" SET UVICORN_WORKERS=1
"%PYTHON_CMD%" -m uvicorn arkive.main:app --host "%HOST%" --port "%PORT%" --workers %UVICORN_WORKERS% --ws auto
:: For ssl user uvicorn arkive.main:app --host "%HOST%" --port "%PORT%" --forwarded-allow-ips '*' --ssl-keyfile "key.pem" --ssl-certfile "cert.pem" --ws auto
