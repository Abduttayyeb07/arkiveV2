:: This method is not recommended, and we recommend you use the `start.sh` file with WSL instead.
@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: Get the directory of the current script
SET "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%" || exit /b

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

:: Check if ARKIVE_SECRET_KEY and ARKIVE_JWT_SECRET_KEY are not set
IF "%ARKIVE_SECRET_KEY% %ARKIVE_JWT_SECRET_KEY%" == " " (
    echo Loading ARKIVE_SECRET_KEY from file, not provided as an environment variable.

    IF NOT EXIST "%KEY_FILE%" (
        echo Generating ARKIVE_SECRET_KEY
        :: Generate a random value to use as a ARKIVE_SECRET_KEY in case the user didn't provide one
        SET /p ARKIVE_SECRET_KEY=<nul
        FOR /L %%i IN (1,1,12) DO SET /p ARKIVE_SECRET_KEY=<!random!>>%KEY_FILE%
        echo ARKIVE_SECRET_KEY generated
    )

    echo Loading ARKIVE_SECRET_KEY from %KEY_FILE%
    SET /p ARKIVE_SECRET_KEY=<%KEY_FILE%
)

:: Execute uvicorn
SET "ARKIVE_SECRET_KEY=%ARKIVE_SECRET_KEY%"
IF "%UVICORN_WORKERS%"=="" SET UVICORN_WORKERS=1
uvicorn arkive.main:app --host "%HOST%" --port "%PORT%" --forwarded-allow-ips "%FORWARDED_ALLOW_IPS%" --workers %UVICORN_WORKERS% --ws auto
:: For ssl user uvicorn arkive.main:app --host "%HOST%" --port "%PORT%" --forwarded-allow-ips '*' --ssl-keyfile "key.pem" --ssl-certfile "cert.pem" --ws auto
