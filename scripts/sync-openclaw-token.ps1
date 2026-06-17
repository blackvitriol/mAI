param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"

$envFile = Join-Path $RepoRoot "docker\.env"
$configFile = Join-Path $RepoRoot "docker\openclaw\config\openclaw.json"
$templateFile = Join-Path $PSScriptRoot "openclaw.template.json"

if (-not (Test-Path $envFile)) {
    throw ".env not found. Run init.cmd first."
}

$envLines = Get-Content $envFile
$tokenLine = $envLines | Where-Object { $_ -match '^\s*OPENCLAW_GATEWAY_TOKEN\s*=' } | Select-Object -First 1
$modelLine = $envLines | Where-Object { $_ -match '^\s*OLLAMA_MODEL\s*=' } | Select-Object -First 1

if (-not $tokenLine) {
    throw "OPENCLAW_GATEWAY_TOKEN missing from .env"
}

$token = ($tokenLine -split '=', 2)[1].Trim()
$model = if ($modelLine) { ($modelLine -split '=', 2)[1].Trim() } else { "qwen3.5:9b" }

if ([string]::IsNullOrWhiteSpace($token) -or $token -eq "change-me-to-a-random-token") {
    throw "OPENCLAW_GATEWAY_TOKEN is still the placeholder. Run init.cmd to generate one."
}

$configDir = Split-Path $configFile -Parent
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

$created = $false
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
if (-not (Test-Path $configFile)) {
    if (-not (Test-Path $templateFile)) {
        throw "Template not found: $templateFile"
    }

    $content = Get-Content $templateFile -Raw
    $content = $content.Replace("__OPENCLAW_GATEWAY_TOKEN__", $token)
    $content = $content.Replace("__OLLAMA_MODEL__", $model)
    [System.IO.File]::WriteAllText($configFile, $content, $utf8NoBom)
    $created = $true
    Write-Host "Created openclaw config from template."
} else {
    $content = Get-Content $configFile -Raw
    $updated = $content
    $updated = $updated -replace '"token"\s*:\s*"[^"]*"', "`"token`": `"$token`""
    $updated = $updated -replace '"primary"\s*:\s*"ollama/[^"]+"', "`"primary`": `"ollama/$model`""
    $updated = $updated -replace '"ollama/[^"]+"\s*:\s*\{\}', "`"ollama/$model`": {}"
    $updated = $updated -replace '("id"\s*:\s*")[^"]+(")', "`${1}$model`${2}"
    $updated = $updated -replace '("name"\s*:\s*")[^"]+(")', "`${1}$model`${2}"

    if ($updated -ne $content) {
        [System.IO.File]::WriteAllText($configFile, $updated, $utf8NoBom)
        Write-Host "Synced openclaw.json (token and/or model)."
    }
}

if ($created) {
    exit 2
}

exit 0
