# keepalive_dac.ps1 - Giu backend DongAnh Capital (Render free) khong ngu trong buoi demo.
# Render free ngu sau 15 phut khong co request; ping moi 10 phut de luon thuc.
# Duoc start_all.ps1 bat o cua so minimized; co the chay rieng: .\keepalive_dac.ps1
while ($true) {
    try {
        Invoke-RestMethod -Uri "https://donganhcapital.onrender.com/api/vnindex?limit=1" -TimeoutSec 90 | Out-Null
        Write-Host "$(Get-Date -Format 'HH:mm:ss') DAC ping OK"
    } catch {
        Write-Host "$(Get-Date -Format 'HH:mm:ss') DAC ping loi: $_"
    }
    Start-Sleep -Seconds 600
}
