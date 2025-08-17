@echo off
REM Auto Test Script for CBP - Windows Batch
REM Run automatic test for Cyclic Bandwidth Problem

echo ========================================
echo   CBP Auto Test Script (Windows)
echo ========================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  Python not found! Please install Python.
    pause
    exit /b 1
)

echo  Python is ready

REM Check required files
if not exist "auto_test.py" (
    echo  auto_test.py not found
    pause
    exit /b 1
)

if not exist "dataset_loader.py" (
    echo  dataset_loader.py not found
    pause
    exit /b 1
)

if not exist "ver_2.py" (
    echo  ver_2.py not found
    pause
    exit /b 1
)

echo  All required files are ready

REM Check Dataset directory
if not exist "Dataset" (
    echo  Dataset directory not found
    echo  Please create Dataset directory and place .mtx files there
    pause
    exit /b 1
)

REM Check .mtx files in Dataset
set mtx_count=0
for %%f in (Dataset\*.mtx Dataset\*.mtx.gz) do set /a mtx_count+=1

if %mtx_count%==0 (
    echo  No .mtx or .mtx.gz files found in Dataset directory
    echo  Please place data files in Dataset directory
    pause
    exit /b 1
)

echo  Found %mtx_count% data files

REM Run test
echo.
echo  Starting auto test...
echo  This process may take several minutes...
echo.

python auto_test.py

REM Check results
if errorlevel 1 (
    echo.
    echo  Test encountered an error!
) else (
    echo.
    echo  Test completed successfully!
    echo  Check CSV result file in current directory
)

echo.
echo  Opening results directory...
explorer .

echo.
pause
