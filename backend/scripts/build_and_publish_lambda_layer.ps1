# Rebuild the AWS Lambda dependency layer with Linux-compatible wheels
# and optionally publish it via the AWS CLI.
#
# Example:
#   pwsh ./scripts/build_and_publish_lambda_layer.ps1 `
#       -PythonExe "python" `
#       -LayerName "tubbyai-backend-layer" `
#       -FunctionName "tubbyai-backend-dev-api" `
#       -Region "us-east-1" `
#       -Publish
#
param(
    [string]$PythonExe = "python",
    [string]$RequirementsFile = "requirements.txt",
    [string]$LayerDirectory = "lambda_layer",
    [string]$LayerZip = "lambda_layer.zip",
    [string]$Region = "us-east-1",
    [string]$LayerName = "tubbyai-backend-layer",
    [string]$FunctionName = "",
    [switch]$Publish
)

set-psdebug -strict
$ErrorActionPreference = "Stop"

# Resolve paths relative to backend directory
$backendRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $backendRoot

if (-not (Test-Path $RequirementsFile)) {
    throw "Requirements file '$RequirementsFile' not found. Expected to run from backend directory."
}

$layerPath = Resolve-Path -Path "."
$targetDir = Join-Path $layerPath $LayerDirectory
$pythonTarget = Join-Path $targetDir "python"

Write-Host "Preparing lambda layer directory: $pythonTarget" -ForegroundColor Cyan
if (Test-Path $targetDir) {
    Remove-Item -Recurse -Force $targetDir
}
New-Item -ItemType Directory -Path $pythonTarget | Out-Null

$pipArgs = @(
    "-m", "pip",
    "install",
    "-r", $RequirementsFile,
    "-t", $pythonTarget,
    "--upgrade",
    "--platform", "manylinux2014_x86_64",
    "--implementation", "cp",
    "--python-version", "3.11",
    "--abi", "cp311",
    "--only-binary=:all:"
)

Write-Host "Installing dependencies for Linux (manylinux2014_x86_64)..." -ForegroundColor Cyan
& $PythonExe $pipArgs

if ($LASTEXITCODE -ne 0) {
    throw "pip install failed with exit code $LASTEXITCODE"
}

if (Test-Path $LayerZip) {
    Remove-Item -Force $LayerZip
}

Write-Host "Creating zip archive: $LayerZip" -ForegroundColor Cyan
Compress-Archive -Path (Join-Path $LayerDirectory "*") -DestinationPath $LayerZip

Write-Host "Layer package ready at $(Join-Path $layerPath $LayerZip)" -ForegroundColor Green

if (-not $Publish.IsPresent) {
    Write-Host "`nTo publish the layer run this script with -Publish or execute the following AWS CLI command:" -ForegroundColor Yellow
    Write-Host "aws lambda publish-layer-version --layer-name $LayerName --zip-file fileb://$LayerZip --compatible-runtimes python3.11 --region $Region" -ForegroundColor Gray
    if ($FunctionName) {
        Write-Host "`nThen attach the new layer ARN to the function:" -ForegroundColor Yellow
        Write-Host "aws lambda update-function-configuration --function-name $FunctionName --layers <NEW_LAYER_ARN> --region $Region" -ForegroundColor Gray
    }
    exit 0
}

if (-not (Get-Command "aws" -ErrorAction SilentlyContinue)) {
    throw "AWS CLI not found in PATH. Install it from https://aws.amazon.com/cli/ and re-run with -Publish."
}

Write-Host "Publishing layer '$LayerName' to AWS Lambda..." -ForegroundColor Cyan
$publishArgs = @(
    "lambda", "publish-layer-version",
    "--layer-name", $LayerName,
    "--zip-file", "fileb://$LayerZip",
    "--compatible-runtimes", "python3.11",
    "--region", $Region,
    "--query", "LayerVersionArn",
    "--output", "text"
)

$layerVersionArn = aws @publishArgs
$layerVersionArn = $layerVersionArn.Trim()

if (-not $layerVersionArn) {
    throw "Failed to publish layer. No ARN returned."
}

Write-Host "Published new layer version: $layerVersionArn" -ForegroundColor Green

if ($FunctionName) {
    Write-Host "Updating Lambda function '$FunctionName' to use the new layer..." -ForegroundColor Cyan
    $updateArgs = @(
        "lambda", "update-function-configuration",
        "--function-name", $FunctionName,
        "--layers", $layerVersionArn,
        "--region", $Region
    )
    aws @updateArgs | Out-Null
    Write-Host "Lambda function updated." -ForegroundColor Green
} else {
    Write-Host "Attach the layer manually using:" -ForegroundColor Yellow
    Write-Host "aws lambda update-function-configuration --function-name FUNCTION_NAME --layers $layerVersionArn --region $Region" -ForegroundColor Gray
}

Write-Host ""
Write-Host "All done." -ForegroundColor Green

