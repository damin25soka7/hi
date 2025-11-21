@echo off
setlocal enabledelayedexpansion
REM SearXNG MCP Server - Simple Startup Script
REM Double-click this file to start the server!

echo.
echo ===============================================
echo   SearXNG MCP Server - Enhanced Edition
echo ===============================================
echo.

REM Check if Node.js is installed
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed
    echo.
    echo Please install Node.js from: https://nodejs.org
    echo.
    pause
    exit /b 1
)

REM Get the script directory
cd /d "%~dp0"

REM Check if .env file exists, if not create it with defaults
if not exist ".env" (
    echo Creating default configuration...
    (
        echo # SearXNG MCP Server Configuration
        echo SEARXNG_BASE_URL=http://localhost:32768
        echo HOST=127.0.0.1
        echo PORT=32769
        echo DESIRED_TIMEZONE=UTC
        echo CONTENT_MAX_LENGTH=10000
        echo SEARCH_RESULT_LIMIT=10
    ) > .env
    echo [OK] Configuration file created: .env
    echo.
)

REM Load environment variables from .env file (safe method)
for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
    set "line=%%a"
    set "line=!line: =!"
    if not "!line:~0,1!"=="#" (
        if not "!line!"=="" (
            set "%%a=%%b"
        )
    )
)

echo Configuration:
echo   SearXNG URL: %SEARXNG_BASE_URL%
echo   Server will run at: http://%HOST%:%PORT%
echo.

echo Starting server...
echo.

npx .

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Server failed to start
    echo.
    pause
)

endlocal
