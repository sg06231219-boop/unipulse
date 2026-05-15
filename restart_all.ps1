# 强制释放 8000 端口
$p = Get-NetTCPConnection -LocalPort 8000 -EA SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($p) {
    Stop-Process -Id $p -Force -EA SilentlyContinue
    Write-Host "Killed port owner: $p"
    Start-Sleep 2
}

# 启动后端
$python = "C:\Users\LYS\AppData\Local\Python\bin\python.exe"
$backend = Start-Process -FilePath $python -ArgumentList "-m","uvicorn","server:app","--host","127.0.0.1","--port","8000" -WindowStyle Minimized -WorkingDirectory "C:\Users\LYS\.qclaw\workspace\projects\unipulse" -PassThru
Write-Host "Backend PID:" $backend.Id
Start-Sleep 4

# 验证后端
try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 8
    Write-Host "Backend OK:" $r.Content
} catch {
    Write-Host "Backend FAIL:" $_.Exception.Message
}

# 启动 bore 并捕获端口
$boreLog = "$env:TEMP\bore_output.txt"
Remove-Item $boreLog -EA SilentlyContinue
$boreExe = "C:\Users\LYS\.qclaw\workspace\tools\bore.exe"
$bore = Start-Process -FilePath $boreExe -ArgumentList "local","8000","--to","bore.pub" -WindowStyle Minimized -RedirectStandardOutput $boreLog -PassThru
Write-Host "Bore PID:" $bore.Id
Write-Host "Waiting 10s for bore to connect..."
Start-Sleep 10

# 读取 bore 端口
$port = $null
if (Test-Path $boreLog) {
    $output = Get-Content $boreLog -Raw
    Write-Host "Bore output:" $output
    if ($output -match 'remote_port=(\d+)') {
        $port = $Matches[1]
        Write-Host "Detected bore port: $port"
        $env:UNIPULSE_BORE_PORT = $port
        $port | Out-File "$env:TEMP\unipulse_bore_port.txt" -Encoding ascii
    }
}

# 测试 bore.pub
if ($port) {
    Write-Host "Testing http://bore.pub:$port ..."
    try {
        $r = Invoke-WebRequest -Uri "http://bore.pub:$port/api/health" -TimeoutSec 10
        Write-Host "Bore OK:" $r.Content
    } catch {
        Write-Host "Bore test FAIL:" $_.Exception.Message
    }
}

Write-Host "Done. Bore port: $port"
Write-Host "Access URL: http://bore.pub:$port"
