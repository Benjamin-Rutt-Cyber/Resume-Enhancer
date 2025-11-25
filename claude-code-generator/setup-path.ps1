# PowerShell script to add Python Scripts directory to PATH
# Run this as Administrator if you want system-wide installation

$pythonVersion = python -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')"
$scriptsPath = "$env:APPDATA\Python\Python$pythonVersion\Scripts"

Write-Host "Checking Python Scripts directory..." -ForegroundColor Cyan
Write-Host "Location: $scriptsPath" -ForegroundColor Yellow

if (Test-Path $scriptsPath) {
    Write-Host "✓ Scripts directory exists" -ForegroundColor Green

    # Check if already in PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -like "*$scriptsPath*") {
        Write-Host "✓ Already in PATH" -ForegroundColor Green
        Write-Host "`nYou can now use: claude-gen --help" -ForegroundColor Cyan
    } else {
        Write-Host "Adding to PATH..." -ForegroundColor Yellow

        # Add to user PATH
        $newPath = "$currentPath;$scriptsPath"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")

        Write-Host "✓ Added to PATH" -ForegroundColor Green
        Write-Host "`nIMPORTANT: Close and reopen your terminal for changes to take effect" -ForegroundColor Yellow
        Write-Host "`nThen you can use: claude-gen --help" -ForegroundColor Cyan
    }

    # Test if claude-gen.exe exists
    $claudeGenPath = Join-Path $scriptsPath "claude-gen.exe"
    if (Test-Path $claudeGenPath) {
        Write-Host "`n✓ claude-gen.exe found at: $claudeGenPath" -ForegroundColor Green
    } else {
        Write-Host "`n⚠ claude-gen.exe not found. Make sure package is installed:" -ForegroundColor Yellow
        Write-Host "  pip install -e ." -ForegroundColor Cyan
    }
} else {
    Write-Host "✗ Scripts directory not found at: $scriptsPath" -ForegroundColor Red
    Write-Host "Make sure Python is installed correctly" -ForegroundColor Yellow
}

Write-Host "`nCurrent workaround (always works):" -ForegroundColor Cyan
Write-Host "  python -m src.cli.main --help" -ForegroundColor White
