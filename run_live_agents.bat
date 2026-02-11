@echo off
echo ===================================================
echo 🚀 Starting LIVE AI Agents (Targeting Production)
echo ===================================================
echo.
echo ⚠️  Ensure backend/.env has your API Keys!
echo.

:: Set the Production API URL
set API_BASE_URL=https://synapse-api-khoz.onrender.com/api/v1

:: Run the agents
python run_agents.py

pause
