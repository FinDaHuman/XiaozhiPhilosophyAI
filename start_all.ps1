# start_all.ps1 - Khoi dong toan bo he thong Lily cho ngay thuyet trinh (PowerShell 5.1)
# Chay tu root repo:  .\start_all.ps1
# Neu bi chan script:  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned  (chay 1 lan)
$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$py   = Join-Path $root "venv\Scripts\python.exe"

if (-not (Test-Path $py)) {
    Write-Host "[LOI] Khong tim thay $py - venv chua duoc tao?" -ForegroundColor Red
    exit 1
}

# --- Doc NGROK_DOMAIN tu .env ---
$domain = $null
$envFile = Join-Path $root ".env"
if (Test-Path $envFile) {
    foreach ($line in (Get-Content $envFile)) {
        if ($line -match '^\s*NGROK_DOMAIN\s*=\s*(.+?)\s*$') { $domain = $Matches[1].Trim() }
    }
}
if (-not $domain) {
    Write-Host "[LOI] Thieu NGROK_DOMAIN trong .env (vd: NGROK_DOMAIN=lily-hiro.ngrok-free.app)" -ForegroundColor Red
    Write-Host "      Xem GUIDE_KHOI_DONG.md muc setup ngrok." -ForegroundColor Red
    exit 1
}

$pids = @{}
$skipHeader = @{ "ngrok-skip-browser-warning" = "true" }

# --- 1) Backend (cua so rieng, giu mo) ---
Write-Host "[1/6] Bat backend Lily (load embeddings lan dau co the mat 1-2 phut)..."
$backendCmd = '$env:PYTHONIOENCODING="utf-8"; Set-Location "' + $root + '"; & "' + $py + '" main.py api'
$p = Start-Process powershell -ArgumentList '-NoExit','-Command',$backendCmd -PassThru
$pids["backend"] = $p.Id

# --- 2) Cho /health ---
$ok = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $r = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2
        if ($r.status -eq "ok") { $ok = $true; break }
    } catch { }
    Start-Sleep -Seconds 2
}
if (-not $ok) {
    Write-Host "[LOI] Backend khong len sau 120s - xem cua so backend de biet loi." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Backend: http://localhost:8000" -ForegroundColor Green

# --- 3) ngrok (domain co dinh - khong can parse URL) ---
Write-Host "[2/6] Bat ngrok tunnel ($domain)..."
try {
    $p = Start-Process ngrok -ArgumentList "http","--domain=$domain","8000" -PassThru
    $pids["ngrok"] = $p.Id
} catch {
    Write-Host "[LOI] Khong chay duoc ngrok - da cai va add-authtoken chua? ($_)" -ForegroundColor Red
    exit 1
}
Start-Sleep -Seconds 4
$tunnelOk = $false
for ($i = 0; $i -lt 5; $i++) {
    try {
        $r = Invoke-RestMethod -Uri "https://$domain/health" -Headers $skipHeader -TimeoutSec 10
        if ($r.status -eq "ok") { $tunnelOk = $true; break }
    } catch { Start-Sleep -Seconds 3 }
}
if ($tunnelOk) { Write-Host "[OK] Tunnel: https://$domain" -ForegroundColor Green }
else { Write-Host "[CANH BAO] Chua verify duoc tunnel - kiem tra cua so ngrok." -ForegroundColor Yellow }

# --- 4) Robot bridge (mcp_pipe.py, cua so rieng) ---
Write-Host "[3/6] Bat robot bridge (mcp_pipe.py)..."
$mcpDir = Join-Path $root "mcp"
$pipeCmd = '$env:PYTHONIOENCODING="utf-8"; Set-Location "' + $mcpDir + '"; & "' + $py + '" mcp_pipe.py'
$p = Start-Process powershell -ArgumentList '-NoExit','-Command',$pipeCmd -PassThru
$pids["mcp_pipe"] = $p.Id

# --- 5) Danh thuc backend DAC (Render free ngu sau 15p, cold start ~60s) ---
Write-Host "[4/6] Danh thuc DongAnh Capital (Render - co the mat toi 90s)..."
try {
    Invoke-RestMethod -Uri "https://donganhcapital.onrender.com/api/vnindex?limit=1" -TimeoutSec 90 | Out-Null
    Write-Host "[OK] DAC backend da thuc." -ForegroundColor Green
} catch {
    Write-Host "[CANH BAO] Chua danh thuc duoc DAC ($_). Cache cua robot se do phan nay." -ForegroundColor Yellow
}

# --- 6) Keep-alive DAC (cua so minimized, ping moi 10 phut) ---
Write-Host "[5/6] Bat keep-alive DAC..."
$p = Start-Process powershell -ArgumentList '-WindowStyle','Minimized','-File',(Join-Path $root "keepalive_dac.ps1") -PassThru
$pids["keepalive"] = $p.Id

# --- 7) Luu PID + tong ket ---
Write-Host "[6/6] Luu PID vao .run_pids.txt..."
$pids.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" } | Set-Content (Join-Path $root ".run_pids.txt") -Encoding ascii

Write-Host ""
Write-Host "================ READY ================" -ForegroundColor Cyan
Write-Host " Backend : http://localhost:8000"
Write-Host " Tunnel  : https://$domain"
Write-Host " Web app : https://lily-hiro.vercel.app"
Write-Host " Robot   : mcp_pipe dang chay (xem cua so cua no de biet trang thai ket noi)"
Write-Host " Dung het: .\stop_all.ps1"
Write-Host "=======================================" -ForegroundColor Cyan
