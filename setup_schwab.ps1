# Schwab Futures Setup Script
# Run this after installing schwab-py

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Charles Schwab Futures Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if schwab-py is installed
Write-Host "Checking for schwab-py..." -ForegroundColor Yellow
$schwabInstalled = python -c "import schwab; print('OK')" 2>$null

if ($schwabInstalled -eq "OK") {
    Write-Host "✓ schwab-py is installed" -ForegroundColor Green
} else {
    Write-Host "✗ schwab-py not found" -ForegroundColor Red
    $install = Read-Host "Install schwab-py now? (y/n)"
    
    if ($install -eq "y") {
        Write-Host "Installing schwab-py..." -ForegroundColor Yellow
        pip install schwab-py
        Write-Host "✓ Installation complete" -ForegroundColor Green
    } else {
        Write-Host "Exiting. Install schwab-py with: pip install schwab-py" -ForegroundColor Yellow
        exit
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Get Schwab API Credentials:" -ForegroundColor White
Write-Host "   Visit: https://developer.schwab.com" -ForegroundColor Gray
Write-Host "   Register an app and copy your App Key & Secret" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run FinalAI Quantum:" -ForegroundColor White
Write-Host "   python Trading.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Configure Schwab:" -ForegroundColor White
Write-Host "   Select Option 18 (Preflight Setup)" -ForegroundColor Gray
Write-Host "   Answer 'yes' to Schwab futures" -ForegroundColor Gray
Write-Host "   Enter your credentials" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Start Trading:" -ForegroundColor White
Write-Host "   Option 22: View Dashboard" -ForegroundColor Gray
Write-Host "   Option 23: Place Orders" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 For detailed instructions, see:" -ForegroundColor Yellow
Write-Host "   SCHWAB_FUTURES_GUIDE.md" -ForegroundColor Gray
Write-Host ""
Write-Host "✓ Setup script complete!" -ForegroundColor Green
Write-Host ""
