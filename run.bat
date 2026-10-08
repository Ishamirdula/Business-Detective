@echo off
cd /d "%~dp0"
set PY=python
%PY% --version >nul 2>nul || set PY=py
%PY% --version >nul 2>nul || (echo Python was not found. Install it from python.org and tick "Add python.exe to PATH", then run this file again. & pause & exit /b 1)
%PY% -c "import streamlit, duckdb, plotly, reportlab" >nul 2>nul || (echo Installing packages - this only happens the first time... & %PY% -m pip install -r requirements.txt)
if not exist data\support_tickets.csv %PY% -m analysis.generate_data
echo Starting Business Detective - close this window to stop the app.
%PY% -m streamlit run app.py
pause
