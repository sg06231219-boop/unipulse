$ErrorActionPreference = 'SilentlyContinue'
$log = 'C:\Users\LYS\.qclaw\workspace\projects\unipulse\bore.log'
$exe = 'C:\Users\LYS\.qclaw\workspace\tools\bore.exe'
$port = '8000'
$relay = 'bore.pub'
$proc = Start-Process -FilePath $exe -ArgumentList "local","$port","--to","$relay" -PassThru -WindowStyle Minimized -RedirectStandardOutput $log -RedirectStandardError "$log"
Start-Sleep 2
if ($proc.HasExited) {
    Write-Output "Bore crashed: $($proc.ExitCode)" >> $log
} else {
    Write-Output "Bore started PID=$($proc.Id)" >> $log
}
