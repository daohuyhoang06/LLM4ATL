param(
  [Parameter(Mandatory = $true)][string]$InputFile,
  [Parameter(Mandatory = $true)][string]$OutputFile,
  [string]$TaggerDir = $env:DSS_STANFORD_TAGGER_DIR,
  [string]$Model = $env:DSS_STANFORD_MODEL
)

$ErrorActionPreference = 'Stop'
$moduleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($TaggerDir)) {
  $TaggerDir = Join-Path $moduleRoot 'lib\stanford-postagger'
}
$TaggerDir = [IO.Path]::GetFullPath($TaggerDir)
if ([string]::IsNullOrWhiteSpace($Model)) {
  $Model = Join-Path $TaggerDir 'models\english-left3words-distsim.tagger'
}
$Model = [IO.Path]::GetFullPath($Model)
$jar = Join-Path $TaggerDir 'stanford-postagger.jar'

if (-not (Test-Path -LiteralPath $InputFile -PathType Leaf)) {
  throw "Requirements file not found: $InputFile"
}
if (-not (Test-Path -LiteralPath $jar -PathType Leaf)) {
  throw "Stanford POS tagger not found: $jar"
}
if (-not (Test-Path -LiteralPath $Model -PathType Leaf)) {
  throw "Stanford POS model not found: $Model"
}

$result = & java -mx300m -cp $jar `
  edu.stanford.nlp.tagger.maxent.MaxentTagger `
  -model $Model -textFile ([IO.Path]::GetFullPath($InputFile))
if ($LASTEXITCODE -ne 0) {
  throw "Stanford POS tagger failed with exit code $LASTEXITCODE"
}

$sentences = @($result | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
if ($sentences.Count -eq 0) {
  throw 'Stanford POS tagger produced no output.'
}
$parent = Split-Path -Parent ([IO.Path]::GetFullPath($OutputFile))
New-Item -ItemType Directory -Force $parent | Out-Null
[IO.File]::WriteAllText(
  [IO.Path]::GetFullPath($OutputFile),
  (($sentences -join "`r`n`r`n") + "`r`n"),
  [Text.UTF8Encoding]::new($false)
)
Write-Host ">>> Tagged requirements: $([IO.Path]::GetFullPath($OutputFile))"

