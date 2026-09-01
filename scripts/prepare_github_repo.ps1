$ErrorActionPreference = "Stop"

$project = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $project

Write-Host "=== Paper2Data GitHub Repository Preparation ===" -ForegroundColor Cyan

Write-Host "Removing generated caches/build output (source files and databases are not deleted)..." -ForegroundColor Cyan

$generatedDirectories = @(
    ".pytest_cache",
    "build",
    "dist",
    "release_output",
    "htmlcov"
)

foreach ($directory in $generatedDirectories) {
    $path = Join-Path $project $directory
    if (Test-Path $path) {
        Remove-Item $path -Recurse -Force
        Write-Host "  Removed $directory"
    }
}

Get-ChildItem $project -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
    Sort-Object FullName -Descending |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Get-ChildItem $project -Recurse -File -Filter "*.pyc" -ErrorAction SilentlyContinue |
    Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "Checking Git..." -ForegroundColor Cyan
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is not installed or is not available on PATH. Install Git for Windows, then run this script again."
}

git --version

if (-not (Test-Path (Join-Path $project ".git"))) {
    git init
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "Initialized Git repository." -ForegroundColor Green
}

Write-Host "Running repository health check..." -ForegroundColor Cyan
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCommand) {
    & $pythonCommand.Source scripts\repository_health_check.py
} else {
    $preferredPython = Join-Path $HOME ".conda\envs\data_analysis\python.exe"
    if (-not (Test-Path $preferredPython)) {
        throw "Python was not found. Run scripts\repository_health_check.py with your project Python manually."
    }
    & $preferredPython scripts\repository_health_check.py
}
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`nFiles Git would add:" -ForegroundColor Cyan
git add --dry-run .

Write-Host "`nPreparation complete." -ForegroundColor Green
Write-Host "Review the dry-run list before running: git add ."
Write-Host "Local databases are intentionally NOT deleted; .gitignore keeps them out of Git."
