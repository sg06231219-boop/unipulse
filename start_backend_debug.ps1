$outlog = "$env:TEMP\unipulse_out.log"
$errlog = "$env:TEMP\unipulse_err.log"
Remove-Item $outlog, $errlog -EA SilentlyContinue

$python = "C:\Users\LYS\AppData\Local\Python\bin\python.exe"
$dir = "C:\Users\LYS\.qclaw\workspace\projects\unipulse"

$proc = Start-Process -FilePath $python -ArgumentList "-m","uvicorn","server:app","--host","127.0.0.1","--port","8000" -WorkingDirectory $dir -WindowStyle Minimized -RedirectStandardOutput $outlog -RedirectStandardError $errlog -PassThru

Write-Host "Backend PID:" $proc.Id
Start-Sleep 5

Write-Host "=== stdout ==="
Get-Content $outlog -Raw -EA SilentlyContinue | Write-Host
Write-Host "=== stderr ==="
Get-Content $errlog -Raw -EA SilentlyContinue | Write-Host
Write-Host "=== End ==="

# Test it
try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 10
    Write-Host "OK:" $r.Content
} catch {
    Write-Host "FAIL:" $_.Exception.Message
}