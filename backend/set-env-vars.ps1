# Set EB Environment Variables (interactive helper)
# Ensures no secrets are stored in source control.

param(
    [string]$BackendPath = (Join-Path $PSScriptRoot ".")
)

Set-Location $BackendPath

function Read-Or-Env {
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

Write-Host "Setting Elastic Beanstalk environment variables..." -ForegroundColor Cyan
Write-Host "(AWS credentials must already be configured via 'aws configure'.)" -ForegroundColor Yellow

$openAiKey = Read-Or-Env -Name "OPENAI_API_KEY" -Prompt "Enter OPENAI_API_KEY"
$elevenLabsKey = Read-Or-Env -Name "ELEVEN_LABS_API_KEY" -Prompt "Enter ELEVEN_LABS_API_KEY"
$elevenLabsVoiceId = Read-Or-Env -Name "ELEVEN_LABS_VOICE_ID" -Prompt "Enter ELEVEN_LABS_VOICE_ID"
$corsOrigins = Read-Or-Env -Name "CORS_ORIGINS" -Prompt "Enter CORS_ORIGINS (comma separated URLs)"

eb setenv `
  OPENAI_API_KEY=$openAiKey `
  ELEVEN_LABS_API_KEY=$elevenLabsKey `
  ELEVEN_LABS_VOICE_ID=$elevenLabsVoiceId `
  CORS_ORIGINS=$corsOrigins

Write-Host "Environment variables set successfully!" -ForegroundColor Green
