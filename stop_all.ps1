# stop_all.ps1 - Dung toan bo he thong Lily da bat boi start_all.ps1 (PowerShell 5.1)
# Chi kill dung cac PID da ghi trong .run_pids.txt + ngrok theo ten (khong kill python theo ten).
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$pidFile = Join-Path $root ".run_pids.txt"

if (Test-Path $pidFile) {
    foreach ($line in (Get-Content $pidFile)) {
        if ($line -match '^(\w+)=(\d+)$') {
            $name = $Matches[1]; $procId = [int]$Matches[2]
            try {
                $proc = Get-Process -Id $procId -ErrorAction Stop
                # Cua so powershell con (backend/mcp_pipe) se keo theo python con khi bi kill
                Stop-Process -Id $procId -Force -ErrorAction Stop
                Write-Host "[OK] Da dung $name (PID $procId)" -ForegroundColor Green
            } catch {
                Write-Host "[--] $name (PID $procId) khong con chay." -ForegroundColor Yellow
            }
        }
    }
    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "[--] Khong thay .run_pids.txt - co the chua chay start_all.ps1." -ForegroundColor Yellow
}

# ngrok la binary rieng, kill theo ten an toan
try { Get-Process ngrok -ErrorAction Stop | Stop-Process -Force -ErrorAction Stop; Write-Host "[OK] Da dung ngrok." -ForegroundColor Green } catch { }

# Don python mo coi cua repo nay (uvicorn/mcp giu port 8000 neu cua so cha bi dong tay):
# chi kill process python co duong dan trong venv cua repo nay - khong dung python khac cua may
$venvPy = (Join-Path $root "venv\Scripts\python.exe").ToLower()
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -and $_.Path.ToLower() -eq $venvPy } | ForEach-Object {
    try { Stop-Process -Id $_.Id -Force -ErrorAction Stop; Write-Host "[OK] Da dung python venv (PID $($_.Id))" -ForegroundColor Green } catch { }
}

Write-Host "Xong. Kiem tra: Get-Process ngrok -ErrorAction SilentlyContinue (phai rong)."
