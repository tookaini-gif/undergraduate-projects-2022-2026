@echo off
setlocal
cd /d "%~dp0"
title iCure Windows
where py >nul 2>nul
if errorlevel 1 goto use_python
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
if errorlevel 1 goto use_python
py -3 server.py
goto finished
:use_python
python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
if errorlevel 1 goto no_python
python server.py
goto finished
:no_python
echo Python 3.10 or newer is required. Qt is NOT required.
echo This PC already has Python. If moved to another PC, install Python first.
:finished
echo.
echo iCure has stopped. Any error details are shown above.
pause
