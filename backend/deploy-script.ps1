# Complete Deployment Script (Elastic Beanstalk)
# Secrets are collected interactively to avoid persisting credentials in source control.

param(
    [string]$BackendPath = (Join-Path $PSScriptRoot ".")
)

Set-Location $BackendPath

function Require-EnvVar {
    param(
        [Parameter(Mandatory)]
        [string]$Name,
        [string]$Prompt
    )

    $value = $env:$Name
    if (-not $value) {
        $value = Read-Host $Prompt
    }

    if (-not $value) {
        throw "Environment variable '$Name' is required."
    }

    return $value
}

Write-Host "Checking environment status..." -ForegroundColor Cyan
eb status

Write-Host "`nSetting environment variables..." -ForegroundColor Cyan
$openAiKey = Require-EnvVar -Name "OPENAI_API_KEY" -Prompt "Enter OPENAI_API_KEY"
$elevenLabsKey = Require-EnvVar -Name "ELEVEN_LABS_API_KEY" -Prompt "Enter ELEVEN_LABS_API_KEY"
$elevenLabsVoiceId = Require-EnvVar -Name "ELEVEN_LABS_VOICE_ID" -Prompt "Enter ELEVEN_LABS_VOICE_ID"
$corsOrigins = Require-EnvVar -Name "CORS_ORIGINS" -Prompt "Enter CORS_ORIGINS (comma separated URLs)"

eb setenv `
  OPENAI_API_KEY=$openAiKey `
  ELEVEN_LABS_API_KEY=$elevenLabsKey `
  ELEVEN_LABS_VOICE_ID=$elevenLabsVoiceId `
  CORS_ORIGINS=$corsOrigins

Write-Host "`nDeploying application..." -ForegroundColor Cyan
eb deploy

Write-Host "`nGetting backend URL..." -ForegroundColor Cyan
eb status | Select-String "CNAME"

Write-Host "`n✅ Deployment complete! Test the health endpoint:" -ForegroundColor Green
$status = eb status
$cname = ($status | Select-String "CNAME:").ToString().Split(":")[1].Trim()
Write-Host "http://$cname/health" -ForegroundColor Yellow
