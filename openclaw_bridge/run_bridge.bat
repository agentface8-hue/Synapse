@echo off
echo ========================================
echo  OpenClaw - Synapse Bridge Launcher
echo ========================================
echo.

cd /d "%~dp0"

if not exist .env (
    echo [!] No .env file found. Running registration first...
    echo.
    python register_agent.py
    echo.
    echo [!] Now add your CLAUDE_API_KEY to .env and run this again.
    pause
    exit /b
)

echo Select mode:
echo   1. Autonomous Loop (default - posts + engages automatically)
echo   2. Webhook Server (OpenClaw triggers via HTTP)  
echo   3. One-off Post
echo   4. One-off Engage
echo.
set /p MODE="Enter choice (1-4): "

if "%MODE%"=="2" (
    echo Starting webhook server...
    python bridge.py --webhook
) else if "%MODE%"=="3" (
    set /p TOPIC="Enter topic: "
    python bridge.py --topic "%TOPIC%"
) else if "%MODE%"=="4" (
    python bridge.py --engage
) else (
    echo Starting autonomous loop...
    python bridge.py
)

pause
