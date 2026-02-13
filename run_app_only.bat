@echo off
SET PYTHON_PATH="C:\Users\Sandeep Kumar\AppData\Local\Programs\Python\Python312\python.exe"

echo Launching Dashboard (Skipping install/gen)...
%PYTHON_PATH% -m streamlit run crime-dashboard/app.py
pause
