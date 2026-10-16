param(
  [Parameter(Mandatory = $true)][string]$Source,
  [Parameter(Mandatory = $true)][string]$Target,
  [Parameter(Mandatory = $true)][string]$TaggedRequirements,
  [Parameter(Mandatory = $true)][string]$ReqOutput,
  [Parameter(Mandatory = $true)][string]$ForwardOutput,
  [string]$RuntimeDir = $env:AGILEUML_RUNTIME_DIR,
  [int]$SourceChain = 2,
  [int]$TargetChain = 2,
  [ValidateSet('fuzzy', 'exact')][string]$TypeMatch = 'fuzzy',
  [long]$MaxCandidates = 1000000,
  [ValidateSet('none', 'accept', 'reject')][string]$Review = 'none',
  [bool]$CheckTargetFeatures = $false
)

$ErrorActionPreference = 'Stop'
$moduleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($RuntimeDir)) {
  $RuntimeDir = Join-Path $moduleRoot 'lib\agileuml-runtime.jar'
}
$RuntimeDir = [System.IO.Path]::GetFullPath($RuntimeDir)

& (Join-Path $moduleRoot 'build.ps1') -RuntimeDir $RuntimeDir
$classPath = (Join-Path $moduleRoot 'build\classes') + [IO.Path]::PathSeparator + $RuntimeDir

& java '-Djava.awt.headless=true' -cp $classPath DssPipelineCli `
  --source $Source `
  --target $Target `
  --tagged-requirements $TaggedRequirements `
  --req-output $ReqOutput `
  --forward-output $ForwardOutput `
  --source-chain $SourceChain `
  --target-chain $TargetChain `
  --type-match $TypeMatch `
  --max-candidates $MaxCandidates `
  --review $Review `
  --check-target-features $CheckTargetFeatures
if ($LASTEXITCODE -ne 0) {
  throw "DSS pipeline failed with exit code $LASTEXITCODE"
}

