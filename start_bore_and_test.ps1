$log = "$env:TEMP\bore_9999.log"
Remove-Item $log -EA SilentlyContinue

$proc = Start-Process -FilePath 'C:\Users\LYS\.qclaw\workspace\tools\bore.exe' `
    -ArgumentList 'local','9999','--to','bore.pub' `
    -WindowStyle Minimized `
    -RedirectStandardOutput $log `
    -PassThru

Write-Host "Bore PID:" $proc.Id
Write-Host "Log file: $log"
Start-Sleep 6

$content = Get-Content $log -Raw -EA SilentlyContinue
Write-Host "=== Bore output ==="
Write-Host $content
Write-Host "=== End ==="

# Try to extract port
if ($content -match 'bore\.pub:(\d+)') {
    $port = $Matches[1]
    Write-Host "BORE PORT: $port"
} else {
    Write-Host "Could not extract bore port from output"
}

# Test the URL
$python = 'C:\Users\LYS\AppData\Local\Python\bin\python.exe'
$testScript = "$env:TEMP\test_bore.py"
@"
import urllib.request
try:
    r = urllib.request.urlopen('http://bore.pub:$port/api/health', timeout=15)
    print('BORE OK:', r.status, r.read().decode())
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code, e.reason, e.read().decode()[:200])
except Exception as e:
    print('Error:', type(e).__name__, e)
"@ | Out-File -FilePath $testScript -Encoding UTF8
& $python $testScript
Remove-Item $testScript -EA SilentlyContinue