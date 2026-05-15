# restart_backend.ps1 - 启动后端并验证
param($Port = 9999)

$python = "C:\Users\LYS\AppData\Local\Python\bin\python.exe"
$workDir = "C:\Users\LYS\.qclaw\workspace\projects\unipulse"
$logFile = "$env:TEMP\unipulse_backend.log"

# 杀旧进程
Get-Process python -EA 0 | Where-Object { $_.CommandLine -like '*uvicorn*9999*' } | Stop-Process -Force -EA 0
Start-Sleep 2

# 启动后端（最小化窗口）
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName  = $python
$psi.Arguments = "-m uvicorn server:app --host 127.0.0.1 --port $Port"
$psi.WorkingDirectory = $workDir
$psi.UseShellExecute = $false
$psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Minimized
$p = [System.Diagnostics.Process]::Start($psi)
"PID: $($p.Id)" | Out-File $logFile -Encoding utf8

Start-Sleep 6

# 验证
try {
    $r = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health" -TimeoutSec 5
    "OK: $($r | ConvertTo-Json)" | Add-Content $logFile -Encoding utf8
    "BACKEND_OK: port=$Port, pid=$($p.Id)"
} catch {
    "ERR: $_" | Add-Content $logFile -Encoding utf8
    "BACKEND_ERR: $_"
}
