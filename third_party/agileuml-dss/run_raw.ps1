param(
  [Parameter(Mandatory = $true)][string]$Source,
  [Parameter(Mandatory = $true)][string]$Target,
  [Parameter(Mandatory = $true)][string]$Requirements,
  [Parameter(Mandatory = $true)][string]$OutputDir,
  [string]$RuntimeDir = $env:AGILEUML_RUNTIME_DIR,
  [string]$TaggerDir = $env:DSS_STANFORD_TAGGER_DIR,
  [int]$SourceChain = 1,
  [int]$TargetChain = 1,
  [ValidateSet('fuzzy', 'exact')][string]$TypeMatch = 'fuzzy',
  [ValidateSet('none', 'accept', 'reject')][string]$Review = 'accept',
  [bool]$CheckTargetFeatures = $false
)

$ErrorActionPreference = 'Stop'
$moduleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$OutputDir = [IO.Path]::GetFullPath($OutputDir)
New-Item -ItemType Directory -Force $OutputDir | Out-Null
$tagged = Join-Path $OutputDir 'requirements.tagged.txt'

& (Join-Path $moduleRoot 'tag_requirements.ps1') `
  -InputFile $Requirements -OutputFile $tagged -TaggerDir $TaggerDir
& (Join-Path $moduleRoot 'run.ps1') `
  -Source $Source -Target $Target -TaggedRequirements $tagged `
  -ReqOutput (Join-Path $OutputDir 'req.tl') `
  -ForwardOutput (Join-Path $OutputDir 'forward.tl') `
  -RuntimeDir $RuntimeDir -SourceChain $SourceChain `
  -TargetChain $TargetChain -TypeMatch $TypeMatch `
  -Review $Review -CheckTargetFeatures $CheckTargetFeatures

