$ErrorActionPreference = 'Stop'
$taskStaging = 'F:/Codex-Recovery-Staging'
[IO.Directory]::CreateDirectory($taskStaging) | Out-Null
$taskName = 'VPS1-2026-10-24-10.6-recovery-images.tar.gz.age'
$taskOutput = Join-Path $taskStaging $taskName
$taskPartial = $taskOutput + '.partial'
if ((Test-Path -LiteralPath $taskOutput) -or (Test-Path -LiteralPath $taskPartial)) { throw 'Existing export requires verification before retry' }
if ((Get-PSDrive F).Free -lt 12GB) { throw 'Insufficient local staging space' }
$taskIdentity = Join-Path $env:USERPROFILE '.ssh/codex_vps1_cody_key'
$taskRecipient = 'age1pv08um2d8w3jhyryjrlp6junfmgufv9fq2nxgm40n3kymjw8hdaslwnfly'
$taskExpectedHash = '9a233570b134c2b9c1863e4b77366c206439a22fe80e112f90376a2af30473f9'
function New-BackupSshProcess([string]$taskRemoteCommand,[bool]$taskInput) {
 $taskInfo = [Diagnostics.ProcessStartInfo]::new('ssh')
 foreach ($taskArgument in @('-i',$taskIdentity,'-o','BatchMode=yes','jackadmin@187.77.210.223',$taskRemoteCommand)) { $taskInfo.ArgumentList.Add($taskArgument) }
 $taskInfo.UseShellExecute = $false
 $taskInfo.CreateNoWindow = $true
 $taskInfo.RedirectStandardOutput = $true
 $taskInfo.RedirectStandardError = $true
 $taskInfo.RedirectStandardInput = $taskInput
 $taskProcess = [Diagnostics.Process]::new()
 $taskProcess.StartInfo = $taskInfo
 [void]$taskProcess.Start()
 return $taskProcess
}
$taskExportCommand = 'docker run --rm --label cody.encrypted-export=true --network none --privileged --pid=host --cgroupns=host alpine nsenter -t 1 -m -u -i -n -p -- /usr/bin/age -r ' + $taskRecipient + ' /opt/openclaw/recovery/release-20261024-fleet-tools/images.tar.gz'
$taskExport = New-BackupSshProcess $taskExportCommand $false
$taskExportError = $taskExport.StandardError.ReadToEndAsync()
$taskStream = [IO.File]::Open($taskPartial,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try { $taskExport.StandardOutput.BaseStream.CopyToAsync($taskStream).GetAwaiter().GetResult() } finally { $taskStream.Dispose() }
$taskExport.WaitForExit()
[IO.File]::WriteAllText($taskOutput+'.export.private.log',$taskExportError.GetAwaiter().GetResult())
if ($taskExport.ExitCode -ne 0) { throw 'Encrypted export failed; partial retained for inspection' }
if ((Get-Item -LiteralPath $taskPartial).Length -le 5648996485) { throw 'Encrypted export is truncated' }
Move-Item -LiteralPath $taskPartial -Destination $taskOutput
Write-Output 'Encrypted image export complete; testing decryption against the verified source hash.'
$taskVerifyCommand = 'docker run --rm -i --label cody.encrypted-verify=true --network none --privileged --pid=host --cgroupns=host alpine nsenter -t 1 -m -u -i -n -p -- /bin/bash -o pipefail -c ''/usr/bin/age --decrypt --identity /opt/openclaw/backups/private-recovery-20261024/age-identity.txt | sha256sum'''
$taskVerify = New-BackupSshProcess $taskVerifyCommand $true
$taskVerifyError = $taskVerify.StandardError.ReadToEndAsync()
$taskVerifyOutput = $taskVerify.StandardOutput.ReadToEndAsync()
$taskRead = [IO.File]::OpenRead($taskOutput)
try { $taskRead.CopyToAsync($taskVerify.StandardInput.BaseStream).GetAwaiter().GetResult() } finally { $taskRead.Dispose(); $taskVerify.StandardInput.Close() }
$taskVerify.WaitForExit()
[IO.File]::WriteAllText($taskOutput+'.decrypt.private.log',$taskVerifyError.GetAwaiter().GetResult())
$taskReturnedHash = ($taskVerifyOutput.GetAwaiter().GetResult().Trim() -split '\s+')[0]
if ($taskVerify.ExitCode -ne 0 -or $taskReturnedHash -ne $taskExpectedHash) { throw 'Encrypted archive roundtrip verification failed' }
$taskReceipt = [ordered]@{server='VPS1';date='2026-10-24';type='recovery-images';encryptedFile=$taskOutput;encryptedBytes=(Get-Item -LiteralPath $taskOutput).Length;encryptedSha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $taskOutput).Hash.ToLowerInvariant();encryptedMd5=(Get-FileHash -Algorithm MD5 -LiteralPath $taskOutput).Hash.ToLowerInvariant();sourceSha256=$taskExpectedHash;decryptionRoundtripVerified=$true;isolatedDockerRestorePreviouslyVerified=$true;imageCount=9;vault='z-backups';keyItemTitle='VPS1 agents backup unlocking code'}
[IO.File]::WriteAllText($taskOutput+'.receipt.json',($taskReceipt | ConvertTo-Json))
$taskReceipt | ConvertTo-Json

