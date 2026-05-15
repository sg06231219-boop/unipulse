$proc = Start-Process -FilePath 'C:\Users\LYS\.qclaw\workspace\tools\bore.exe' -ArgumentList 'local','9999','--to','bore.pub' -WindowStyle Minimized -PassThru
Write-Host "Bore PID:" $proc.Id
Start-Sleep 6