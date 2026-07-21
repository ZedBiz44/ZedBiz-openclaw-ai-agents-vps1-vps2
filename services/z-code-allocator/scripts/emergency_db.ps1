param([ValidateSet('start','stop','status')][string]$Action = 'status')

$ErrorActionPreference = 'Stop'
$Key = Join-Path $env:USERPROFILE '.ssh\cody_vps1_runtime'
ssh -i $Key jackadmin@187.77.210.223 "bash /opt/zedbiz-services/z-code-allocator/scripts/emergency_db.sh $Action"
