@echo off
setlocal

:: Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Please run installation steps first.
    echo See README.md for details.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate

:: Run the application
echo Starting Unit Extraction Tool...
streamlit run app.py

pause
