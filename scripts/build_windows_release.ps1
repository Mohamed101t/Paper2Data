param(
    [string]$PythonExe = "",
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
$project = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (-not $PythonExe) {
    $preferred = Join-Path $HOME ".conda\envs\data_analysis\python.exe"
    if (Test-Path $preferred) {
        $PythonExe = $preferred
    } else {
        $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCommand) {
            throw "Python was not found. Pass -PythonExe with the environment Python path."
        }
        $PythonExe = $pythonCommand.Source
    }
}

if (-not (Test-Path $PythonExe)) {
    throw "Python executable does not exist: $PythonExe"
}

Set-Location $project
Write-Host "Paper2Data Windows Release Build V6.1" -ForegroundColor Cyan
Write-Host "Project: $project"
Write-Host "Python : $PythonExe"

Write-Host "`nInstalling release dependencies..." -ForegroundColor Cyan
& $PythonExe -m pip install -r requirements_release.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`nBuilding Qt translations..." -ForegroundColor Cyan
& $PythonExe scripts\build_translations.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $SkipTests) {
    Write-Host "`nInstalling test dependencies..." -ForegroundColor Cyan
    & $PythonExe -m pip install -r requirements_test.txt
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "`nRunning release quality gate..." -ForegroundColor Cyan
    & $PythonExe scripts\run_tests.py full
    if ($LASTEXITCODE -ne 0) {
        throw "Quality gate failed. The EXE will not be built."
    }
}

Write-Host "`nCleaning previous build output..." -ForegroundColor Cyan
Remove-Item "$project\build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$project\dist" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`nBuilding Paper2Data.exe (onedir)..." -ForegroundColor Cyan
& $PythonExe -m PyInstaller --noconfirm --clean "release\Paper2Data.spec"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`nChecking release for accidental local databases..." -ForegroundColor Cyan
$dbFiles = @(Get-ChildItem "$project\dist\Paper2Data" -Recurse -File -Include "*.db","*.db-wal","*.db-shm")
if ($dbFiles.Count -gt 0) {
    $dbFiles | ForEach-Object { Write-Host $_.FullName -ForegroundColor Red }
    throw "Release contains local database files. Build stopped to protect user data."
}

Write-Host "`nVerifying required runtime DLLs..." -ForegroundColor Cyan
$requiredDlls = @(
    "liblzma.dll",
    "LIBBZ2.dll",
    "libmpdec-4.dll",
    "ffi.dll",
    "libexpat.dll",
    "sqlite3.dll"
)

$missingDlls = @()
foreach ($dll in $requiredDlls) {
    $match = Get-ChildItem "$project\dist\Paper2Data" -Recurse -File -Filter $dll -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($match) {
        Write-Host "  OK  $dll -> $($match.FullName)" -ForegroundColor Green
    } else {
        Write-Host "  MISSING  $dll" -ForegroundColor Red
        $missingDlls += $dll
    }
}

if ($missingDlls.Count -gt 0) {
    throw "Release is missing required runtime DLL(s): $($missingDlls -join ', ')"
}

$smokeStatus = "NOT_RUN"
Write-Host ""
& "$project\scripts\test_windows_release.ps1" -ProjectRoot $project
$smokeExitCode = $LASTEXITCODE

if ($smokeExitCode -eq 0) {
    $smokeStatus = "PASSED"
} elseif ($smokeExitCode -eq 23) {
    $smokeStatus = "BLOCKED_BY_WINDOWS_APPLICATION_CONTROL"
} else {
    throw "Packaged EXE smoke test failed with exit code $smokeExitCode."
}

$outputDir = Join-Path $project "release_output"
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

$artifactSuffix = if ($smokeStatus -eq "PASSED") { "" } else { "-UNVERIFIED" }
$zipPath = Join-Path $outputDir "Paper2Data-1.0.0-windows-x64$artifactSuffix.zip"
Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
Compress-Archive -Path "$project\dist\Paper2Data\*" -DestinationPath $zipPath -CompressionLevel Optimal

$hash = Get-FileHash $zipPath -Algorithm SHA256
$checksumPath = "$zipPath.sha256.txt"
"$($hash.Hash)  $([IO.Path]::GetFileName($zipPath))" | Set-Content $checksumPath -Encoding ASCII

$report = @"
Paper2Data Windows Release Build
Version: 1.0.0
Built: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Python: $PythonExe
Executable: $project\dist\Paper2Data\Paper2Data.exe
Archive: $zipPath
SHA256: $($hash.Hash)
Quality gate: $(if ($SkipTests) { "SKIPPED" } else { "PASSED" })
Packaged EXE smoke test: $smokeStatus
"@
$report | Set-Content (Join-Path $outputDir "RELEASE_BUILD_REPORT.txt") -Encoding UTF8

Write-Host "`nBuild artifacts created." -ForegroundColor Green
Write-Host "EXE : $project\dist\Paper2Data\Paper2Data.exe"
Write-Host "ZIP : $zipPath"
Write-Host "SHA : $checksumPath"
Write-Host "Smoke test: $smokeStatus"

if ($smokeStatus -ne "PASSED") {
    Write-Host "`nThe build is NOT release-approved yet because Windows Application Control blocked execution." -ForegroundColor Yellow
    Write-Host "Do not publish the UNVERIFIED ZIP as the final release." -ForegroundColor Yellow
    Write-Host "Run: powershell -ExecutionPolicy Bypass -File .\scripts\diagnose_windows_app_control.ps1" -ForegroundColor Yellow
    exit 23
}

Write-Host "`nRelease build completed successfully." -ForegroundColor Green
