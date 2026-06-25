param(
    [string]$EnvFile,
    [string]$PreferredModel
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $EnvFile)) {
    throw ".env not found: $EnvFile"
}

$envLines = Get-Content $EnvFile
$modelLine = $envLines | Where-Object { $_ -match '^\s*LM_STUDIO_MODEL_ID\s*=' } | Select-Object -First 1
$configured = if ($modelLine) { ($modelLine -split '=', 2)[1].Trim() } else { $PreferredModel }

$raw = docker exec a7_server_1-lmstudio wget -qO- "http://127.0.0.1:1234/v1/models" 2>$null
if (-not $raw) {
    Write-Host "Could not query LM Studio models; using configured id: $configured"
    Write-Output $configured
    exit 0
}

$payload = $raw | ConvertFrom-Json
$available = @()
if ($payload.data) {
    $available = @($payload.data | ForEach-Object { $_.id })
}

if ($available.Count -eq 0) {
    Write-Host "No models loaded in LM Studio; using configured id: $configured"
    Write-Output $configured
    exit 0
}

$resolved = $configured
if ($available -notcontains $configured) {
    if ($available -contains $PreferredModel) {
        $resolved = $PreferredModel
    } else {
        $resolved = $available[0]
    }
    Write-Host "LM Studio model resolved: $resolved (configured was $configured; available: $($available -join ', '))"
    $updated = ($envLines | ForEach-Object {
        if ($_ -match '^\s*LM_STUDIO_MODEL_ID\s*=') {
            "LM_STUDIO_MODEL_ID=$resolved"
        } else {
            $_
        }
    })
    if (-not ($updated | Where-Object { $_ -match '^\s*LM_STUDIO_MODEL_ID\s*=' })) {
        $updated += "LM_STUDIO_MODEL_ID=$resolved"
    }
    Set-Content -Path $EnvFile -Value $updated -Encoding UTF8
} else {
    Write-Host "Using configured LM Studio model: $resolved"
}

Write-Output $resolved
