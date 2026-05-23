@echo off
REM SMT Line 003 Production Intelligence Dashboard
REM Streamlit App Launcher

cd /d "%~dp0"

echo.
echo ============================================================
echo   STATIC//VOID - SMT Line 003 Production Intelligence
echo ============================================================
echo.
echo Starting Streamlit app...
echo Dashboard will open at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server.
echo.

streamlit run app.py

pause
