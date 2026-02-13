@echo off
SET PYTHON_PATH="C:\Users\Sandeep Kumar\AppData\Local\Programs\Python\Python312\python.exe"

echo Using Python at: %PYTHON_PATH%

echo Installing dependencies...
%PYTHON_PATH% -m pip install -r crime-dashboard/requirements.txt

echo Generating data...
%PYTHON_PATH% crime-dashboard/generate_data.py

echo Launching Dashboard...
%PYTHON_PATH% -m streamlit run crime-dashboard/app.py
pause
