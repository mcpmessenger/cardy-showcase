@echo off
REM Install AWS CLI and EB CLI via Batch Script
REM Run: install-aws-tools.bat

echo.
echo === Installing AWS Tools ===
echo.

REM Check Python
echo 1. Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.11+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python found

REM Check pip
echo.
echo 2. Checking pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip not found!
    pause
    exit /b 1
)
echo [OK] pip found

REM Check AWS CLI
echo.
echo 3. Checking AWS CLI...
aws --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] AWS CLI not found. Installing...
    echo Downloading AWS CLI installer...
    powershell -Command "Invoke-WebRequest -Uri 'https://awscli.amazonaws.com/AWSCLIV2.msi' -OutFile '%TEMP%\AWSCLIV2.msi'"
    echo Installing AWS CLI...
    start /wait msiexec.exe /i "%TEMP%\AWSCLIV2.msi" /quiet
    echo [OK] AWS CLI installed (may need to restart terminal)
) else (
    echo [OK] AWS CLI already installed
)

REM Install EB CLI
echo.
echo 4. Installing Elastic Beanstalk CLI...
pip install awsebcli --upgrade
if errorlevel 1 (
    echo [WARNING] Installation failed, trying user installation...
    python -m pip install --user awsebcli
)
echo [OK] EB CLI installation complete

REM Verify
echo.
echo 5. Verifying installation...
eb --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] EB CLI may not be in PATH. Try restarting terminal.
) else (
    echo [OK] EB CLI is ready
)

echo.
echo === Installation Complete ===
echo.
echo Next steps:
echo 1. Configure AWS: aws configure
echo 2. Initialize EB: cd backend && eb init
echo.
pause

