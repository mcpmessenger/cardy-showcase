# Install EB CLI and AWS CLI via Script
# Run: .\install-eb-cli.ps1

Write-Host "`n=== Installing AWS Tools ===" -ForegroundColor Green

# Check if Python is installed
Write-Host "`n1. Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found! Please install Python 3.11+ first." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ $pythonVersion" -ForegroundColor Green

# Check if pip is installed
Write-Host "`n2. Checking pip installation..." -ForegroundColor Yellow
$pipVersion = pip --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ pip not found! Installing pip..." -ForegroundColor Red
    python -m ensurepip --upgrade
}
Write-Host "✅ $pipVersion" -ForegroundColor Green

# Check if AWS CLI is installed
Write-Host "`n3. Checking AWS CLI installation..." -ForegroundColor Yellow
$awsVersion = aws --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  AWS CLI not found. Installing..." -ForegroundColor Yellow
    
    # Install AWS CLI via MSI installer
    Write-Host "Downloading AWS CLI installer..." -ForegroundColor Cyan
    $installerUrl = "https://awscli.amazonaws.com/AWSCLIV2.msi"
    $installerPath = "$env:TEMP\AWSCLIV2.msi"
    
    try {
        Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
        Write-Host "Installing AWS CLI..." -ForegroundColor Cyan
        Start-Process msiexec.exe -ArgumentList "/i `"$installerPath`" /quiet" -Wait
        Write-Host "✅ AWS CLI installed!" -ForegroundColor Green
        Write-Host "⚠️  You may need to restart your terminal for AWS CLI to be available." -ForegroundColor Yellow
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } catch {
        Write-Host "❌ Failed to install AWS CLI automatically." -ForegroundColor Red
        Write-Host "Please download and install manually:" -ForegroundColor Yellow
        Write-Host "https://aws.amazon.com/cli/" -ForegroundColor Cyan
    }
} else {
    Write-Host "✅ AWS CLI already installed: $awsVersion" -ForegroundColor Green
}

# Install EB CLI
Write-Host "`n4. Installing Elastic Beanstalk CLI..." -ForegroundColor Yellow
try {
    pip install awsebcli --upgrade
    Write-Host "✅ EB CLI installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install EB CLI via pip." -ForegroundColor Red
    Write-Host "Trying alternative method..." -ForegroundColor Yellow
    
    # Alternative: Install via pip with user flag
    python -m pip install --user awsebcli
    Write-Host "✅ EB CLI installed (user installation)!" -ForegroundColor Green
    Write-Host "⚠️  You may need to add Python user scripts to PATH." -ForegroundColor Yellow
}

# Verify EB CLI installation
Write-Host "`n5. Verifying EB CLI installation..." -ForegroundColor Yellow
$ebVersion = eb --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ EB CLI is ready: $ebVersion" -ForegroundColor Green
} else {
    Write-Host "⚠️  EB CLI may not be in PATH yet." -ForegroundColor Yellow
    Write-Host "Try restarting your terminal or run: refreshenv" -ForegroundColor Cyan
}

# Configure AWS credentials check
Write-Host "`n6. Checking AWS credentials..." -ForegroundColor Yellow
$awsConfig = aws configure list 2>&1
if ($awsConfig -match "Not configured") {
    Write-Host "⚠️  AWS credentials not configured." -ForegroundColor Yellow
    Write-Host "Run: aws configure" -ForegroundColor Cyan
    Write-Host "You'll need:" -ForegroundColor Yellow
    Write-Host "  - AWS Access Key ID" -ForegroundColor White
    Write-Host "  - AWS Secret Access Key" -ForegroundColor White
    Write-Host "  - Default region (e.g., us-east-1)" -ForegroundColor White
    Write-Host "  - Default output format (json)" -ForegroundColor White
} else {
    Write-Host "✅ AWS credentials configured" -ForegroundColor Green
}

Write-Host "`n=== Installation Complete ===" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Configure AWS: aws configure" -ForegroundColor White
Write-Host "2. Initialize EB: cd backend && eb init" -ForegroundColor White
Write-Host "`n" -ForegroundColor White

