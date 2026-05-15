# restart_bore.ps1 - 重启 bore 隧道并提取公网地址
param($Port = 9999)

$boreExe = "C:\Users\LYS\.qclaw\workspace\projects\unipulse\tools\bore.exe"
$logDir  = $env:TEMP
$logFile = Join-Path $logDir "bore_$Port.log"

# 杀掉旧进程
Get-Process bore -EA 0 | Stop-Process -Force -EA 0
Start-Sleep 1

# 启动 bore，日志写到临时文件
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName  = $boreExe
$psi.Arguments = "tcp --to $Port"
$psi.WorkingDirectory = Split-Path $boreExe -Parent
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Minimized

$p = [System.Diagnostics.Process]::Start($psi)
Start-Sleep 6

# 从 stdout 里抓取端口行
$logContent = $p.StandardOutput.ReadToEnd() + $p.StandardError.ReadToEnd()
$logContent | Out-File $logFile -Encoding utf8

# 提取 bore.pub 端口
$portLine = $logContent -split "`n" | Where-Object { $_ -match 'bore\.pub' } | Select-Object -Last 1
if ($portLine -match 'bore\.pub[:：](\d+)') {
    $publicPort = $matches[1]
    "BORE_OK: bore.pub:$publicPort"
    "Log: $logFile"
} elseif ($portLine -match 'listening at .*bore\.pub[:：](\d+)') {
    $publicPort = $matches[1]
    "BORE_OK: bore.pub:$publicPort"
} else {
    "BORE_ERR: 无法提取端口，日志前20行："
    ($logContent -split "`n")[0..19] | ForEach-Object { "  $_" }
}
