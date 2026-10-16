param(
  [string]$RuntimeDir = $env:AGILEUML_RUNTIME_DIR
)

$ErrorActionPreference = 'Stop'
$moduleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($RuntimeDir)) {
  $RuntimeDir = Join-Path $moduleRoot 'lib\agileuml-runtime.jar'
}
$RuntimeDir = [System.IO.Path]::GetFullPath($RuntimeDir)

if (Test-Path -LiteralPath $RuntimeDir -PathType Leaf) {
  if ([IO.Path]::GetExtension($RuntimeDir) -ne '.jar') {
    throw "AgileUML runtime file must be a JAR: $RuntimeDir"
  }
}
elseif (-not (Test-Path -LiteralPath (Join-Path $RuntimeDir 'ModelMatching.class'))) {
  throw "AgileUML runtime not found at: $RuntimeDir. Set AGILEUML_RUNTIME_DIR to a runtime JAR or classes directory."
}

$sourceDir = Join-Path $moduleRoot 'src'
$buildDir = Join-Path $moduleRoot 'build\classes'
$emptySourcePath = Join-Path $moduleRoot 'build\empty-sourcepath'
New-Item -ItemType Directory -Force $buildDir, $emptySourcePath | Out-Null

$sources = Get-ChildItem -LiteralPath $sourceDir -Filter '*.java' |
  Sort-Object Name |
  ForEach-Object FullName
if (-not $sources) {
  throw "No Java adapter sources found in: $sourceDir"
}

$mainClass = Join-Path $buildDir 'DssPipelineCli.class'
$needsCompile = -not (Test-Path -LiteralPath $mainClass -PathType Leaf)
if (-not $needsCompile) {
  $builtAt = (Get-Item -LiteralPath $mainClass).LastWriteTimeUtc
  $needsCompile = @($sources | Where-Object {
    (Get-Item -LiteralPath $_).LastWriteTimeUtc -gt $builtAt
  }).Count -gt 0
}
if (-not $needsCompile) {
  Write-Host ">>> AgileUML DSS adapter is up to date: $buildDir"
  return
}

& javac -encoding UTF-8 -sourcepath $emptySourcePath `
  -classpath $RuntimeDir -d $buildDir @sources
if ($LASTEXITCODE -ne 0) {
  throw "javac failed with exit code $LASTEXITCODE"
}

Write-Host ">>> Built AgileUML DSS headless adapter: $buildDir"

