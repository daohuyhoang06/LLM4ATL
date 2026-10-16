param(
  [Parameter(Mandatory = $true)][string]$Source,
  [Parameter(Mandatory = $true)][string]$Target,
  [Parameter(Mandatory = $true)][string]$Requirements,
  [Parameter(Mandatory = $true)][string]$OutputDir,
  [Parameter(Mandatory = $true)][string]$OriginalAgileUmlDir,
  [int]$SourceChain = 1,
  [int]$TargetChain = 1,
  [ValidateSet('fuzzy', 'exact')][string]$TypeMatch = 'fuzzy'
)

$ErrorActionPreference = 'Stop'
$moduleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$runtimeJar = Join-Path $moduleRoot 'lib\agileuml-runtime.jar'
$classDir = Join-Path $moduleRoot 'build\classes'
$OutputDir = [IO.Path]::GetFullPath($OutputDir)
$OriginalAgileUmlDir = [IO.Path]::GetFullPath($OriginalAgileUmlDir)

foreach ($requiredClass in 'ModelMatching.class', 'EntityMatching.class', 'AttributeMatching.class') {
  $classFile = Join-Path $OriginalAgileUmlDir $requiredClass
  if (-not (Test-Path -LiteralPath $classFile -PathType Leaf)) {
    throw "Original AgileUML class not found: $classFile"
  }
}

& (Join-Path $moduleRoot 'build.ps1') -RuntimeDir $runtimeJar

$adapterDir = Join-Path $OutputDir 'adapter'
$originalDir = Join-Path $OutputDir 'original-core'
New-Item -ItemType Directory -Force $adapterDir, $originalDir | Out-Null
$tagged = Join-Path $OutputDir 'requirements.tagged.txt'
& (Join-Path $moduleRoot 'tag_requirements.ps1') `
  -InputFile $Requirements -OutputFile $tagged

$commonArguments = @(
  '-Djava.awt.headless=true',
  'DssPipelineCli',
  '--source', [IO.Path]::GetFullPath($Source),
  '--target', [IO.Path]::GetFullPath($Target),
  '--tagged-requirements', $tagged,
  '--source-chain', [string]$SourceChain,
  '--target-chain', [string]$TargetChain,
  '--type-match', $TypeMatch,
  '--review', 'none',
  '--check-target-features', 'false'
)

function Invoke-DssVariant([string]$ClassPath, [string]$ResultDir) {
  $arguments = @('-cp', $ClassPath) + $commonArguments + @(
    '--req-output', (Join-Path $ResultDir 'req.tl'),
    '--forward-output', (Join-Path $ResultDir 'forward.tl')
  )
  & java @arguments
  if ($LASTEXITCODE -ne 0) {
    throw "DSS variant failed with exit code $LASTEXITCODE"
  }
}

$adapterClassPath = $classDir + [IO.Path]::PathSeparator + $runtimeJar
$originalClassPath = $OriginalAgileUmlDir + [IO.Path]::PathSeparator +
  $classDir + [IO.Path]::PathSeparator + $runtimeJar

Invoke-DssVariant $adapterClassPath $adapterDir
Invoke-DssVariant $originalClassPath $originalDir

$different = @()
foreach ($name in 'req.tl', 'forward.tl') {
  $adapterText = (Get-Content -LiteralPath (Join-Path $adapterDir $name) -Raw) -replace "`r`n", "`n"
  $originalText = (Get-Content -LiteralPath (Join-Path $originalDir $name) -Raw) -replace "`r`n", "`n"
  if ($adapterText -ceq $originalText) {
    Write-Host "[PASS] $name is byte-equivalent after newline normalisation"
  }
  else {
    Write-Host "[FAIL] $name differs"
    $different += $name
  }
}

if ($different.Count -gt 0) {
  throw "Adapter differs from original AgileUML core: $($different -join ', ')"
}
Write-Host ">>> AgileUML core compatibility passed: $OutputDir"
