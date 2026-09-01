param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot ".."))
)

$exe = Join-Path $ProjectRoot "dist\Paper2Data\Paper2Data.exe"

Write-Host "=== Paper2Data Windows Application Control Diagnostics ===" -ForegroundColor Cyan
Write-Host "EXE: $exe"

if (-not (Test-Path $exe)) {
    throw "Paper2Data.exe was not found: $exe"
}

Write-Host "`nFile hash:" -ForegroundColor Cyan
Get-FileHash $exe -Algorithm SHA256 | Format-List Algorithm, Hash, Path

Write-Host "`nAuthenticode signature:" -ForegroundColor Cyan
Get-AuthenticodeSignature $exe | Format-List Status, StatusMessage, SignerCertificate, TimeStamperCertificate, Path

Write-Host "`nMark-of-the-Web stream:" -ForegroundColor Cyan
$zone = Get-Item $exe -Stream Zone.Identifier -ErrorAction SilentlyContinue
if ($zone) {
    $zone | Format-List *
    Write-Host "The EXE has a Zone.Identifier stream. Because this EXE is your own local build, you may remove only that download-origin mark with:" -ForegroundColor Yellow
    Write-Host "  Unblock-File `"$exe`"" -ForegroundColor Yellow
} else {
    Write-Host "No Zone.Identifier stream found."
}

Write-Host "`nRecent Code Integrity events mentioning Paper2Data:" -ForegroundColor Cyan
try {
    $events = Get-WinEvent -LogName "Microsoft-Windows-CodeIntegrity/Operational" -MaxEvents 200 -ErrorAction Stop |
        Where-Object { $_.Message -like "*Paper2Data*" -or $_.Message -like "*Paper2Data.exe*" } |
        Select-Object -First 20 TimeCreated, Id, LevelDisplayName, Message

    if ($events) {
        $events | Format-List
    } else {
        Write-Host "No matching CodeIntegrity events were found in the latest 200 events."
    }
} catch {
    Write-Host "Could not read CodeIntegrity log: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`nRecent AppLocker EXE/DLL events mentioning Paper2Data:" -ForegroundColor Cyan
try {
    $events = Get-WinEvent -LogName "Microsoft-Windows-AppLocker/EXE and DLL" -MaxEvents 100 -ErrorAction Stop |
        Where-Object { $_.Message -like "*Paper2Data*" -or $_.Message -like "*Paper2Data.exe*" } |
        Select-Object -First 20 TimeCreated, Id, LevelDisplayName, Message

    if ($events) {
        $events | Format-List
    } else {
        Write-Host "No matching AppLocker events were found."
    }
} catch {
    Write-Host "Could not read AppLocker log: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`nWindows Security path:" -ForegroundColor Cyan
Write-Host "Windows Security -> App & browser control -> Smart App Control"
Write-Host ""
Write-Host "Do not disable organization-managed App Control/AppLocker/WDAC just to run this build." -ForegroundColor Yellow
Write-Host "If Smart App Control is the blocker, Microsoft does not provide a per-app bypass; the production solution is a valid code-signing certificate or testing on a suitable clean VM/test PC." -ForegroundColor Yellow
