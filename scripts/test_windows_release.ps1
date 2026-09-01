param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot ".."))
)

$ErrorActionPreference = "Stop"
$exe = Join-Path $ProjectRoot "dist\Paper2Data\Paper2Data.exe"

if (-not (Test-Path $exe)) {
    throw "Paper2Data.exe was not found: $exe"
}

$tempData = Join-Path $env:TEMP ("Paper2DataSmoke_" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempData -Force | Out-Null
$previousDataDir = $env:PAPER2DATA_DATA_DIR
$env:PAPER2DATA_DATA_DIR = $tempData

try {
    Write-Host "Running packaged EXE smoke test..." -ForegroundColor Cyan

    try {
        $process = Start-Process -FilePath $exe -ArgumentList "--smoke-test" -PassThru -Wait
    } catch {
        $message = $_.Exception.Message
        if ($message -match "Application Control policy has blocked" -or
            $message -match "blocked this file") {
            Write-Host "EXE smoke test: BLOCKED BY WINDOWS APPLICATION CONTROL" -ForegroundColor Yellow
            Write-Host "The executable was built, but this Windows policy refused to start it." -ForegroundColor Yellow
            Write-Host "This is not an application test failure. Run scripts\diagnose_windows_app_control.ps1." -ForegroundColor Yellow
            exit 23
        }
        throw
    }

    if ($process.ExitCode -ne 0) {
        throw "EXE smoke test failed with exit code $($process.ExitCode)."
    }

    Write-Host "EXE smoke test: PASS" -ForegroundColor Green
    exit 0
} finally {
    if ($null -eq $previousDataDir) {
        Remove-Item Env:PAPER2DATA_DATA_DIR -ErrorAction SilentlyContinue
    } else {
        $env:PAPER2DATA_DATA_DIR = $previousDataDir
    }
    Remove-Item $tempData -Recurse -Force -ErrorAction SilentlyContinue
}
