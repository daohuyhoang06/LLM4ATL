param(
  [string]$RuntimeDir = $env:AGILEUML_RUNTIME_DIR
)

$ErrorActionPreference = 'Stop'
$moduleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$fixtureDir = Join-Path $moduleRoot 'tests\fixtures'
$outputDir = Join-Path $moduleRoot 'build\test-output\er2rel'
New-Item -ItemType Directory -Force $outputDir | Out-Null
$req = Join-Path $outputDir 'req.tl'
$forward = Join-Path $outputDir 'forward.tl'

& (Join-Path $moduleRoot 'run.ps1') `
  -Source (Join-Path $fixtureDir 'ER.ecore') `
  -Target (Join-Path $fixtureDir 'REL.ecore') `
  -TaggedRequirements (Join-Path $fixtureDir 'requirements.tagged.txt') `
  -ReqOutput $req -ForwardOutput $forward -RuntimeDir $RuntimeDir `
  -SourceChain 1 -TargetChain 1 -TypeMatch fuzzy `
  -Review accept -CheckTargetFeatures $false

$reqText = Get-Content -LiteralPath $req -Raw
$forwardText = Get-Content -LiteralPath $forward -Raw
$expectations = [ordered]@{
  'requirements class seed ERSchema -> RELSchema' = $reqText.Contains('ERSchema |--> RELSchema')
  'requirements feature seed isKey -> isKey' = $reqText.Contains('isKey |--> isKey')
  'DSS class mapping SchemaElement -> Relation' = $forwardText.Contains('SchemaElement |--> Relation')
  'DSS class mapping RelshipEnd -> RELAttribute' = $forwardText.Contains('RelshipEnd |--> RELAttribute')
  'DSS collection synthesis for schema' = $forwardText.Contains('entities->union(relships) |--> relations')
  'DSS collection synthesis for entity attrs' = $forwardText.Contains('attrs->union(relshipEnds) |--> attrs')
  'requirements mapping preserved Entity -> Relation' = $forwardText.Contains('Entity |--> Relation')
  'requirements mapping preserved ERAttribute -> RELAttribute' = $forwardText.Contains('ERAttribute |--> RELAttribute')
}

$failed = @($expectations.GetEnumerator() | Where-Object { -not $_.Value })
foreach ($entry in $expectations.GetEnumerator()) {
  $status = if ($entry.Value) { 'PASS' } else { 'FAIL' }
  Write-Host "[$status] $($entry.Key)"
}
if ($failed.Count -gt 0) {
  throw "$($failed.Count) DSS integration assertion(s) failed."
}

$rawOutputDir = Join-Path $moduleRoot 'build\test-output\raw-er2rel'
& (Join-Path $moduleRoot 'run_raw.ps1') `
  -Source (Join-Path $fixtureDir 'ER.ecore') `
  -Target (Join-Path $fixtureDir 'REL.ecore') `
  -Requirements (Join-Path $fixtureDir 'requirements.txt') `
  -OutputDir $rawOutputDir -RuntimeDir $RuntimeDir `
  -SourceChain 1 -TargetChain 1 -TypeMatch fuzzy `
  -Review accept -CheckTargetFeatures $false

$rawReq = Get-Content -LiteralPath (Join-Path $rawOutputDir 'req.tl') -Raw
$rawForward = Get-Content -LiteralPath (Join-Path $rawOutputDir 'forward.tl') -Raw
if (-not $rawReq.Contains('ERSchema |--> RELSchema') -or
    -not $rawForward.Contains('entities->union(relships) |--> relations')) {
  throw 'Bundled Stanford POS tagger smoke test failed.'
}
Write-Host '[PASS] bundled Stanford POS tagger -> requirements -> DSS'

$collisionOutputDir = Join-Path $moduleRoot 'build\test-output\collision'
New-Item -ItemType Directory -Force $collisionOutputDir | Out-Null
$collisionReq = Join-Path $collisionOutputDir 'req.tl'
$collisionForward = Join-Path $collisionOutputDir 'forward.tl'
& (Join-Path $moduleRoot 'run.ps1') `
  -Source (Join-Path $fixtureDir 'CollisionSource.ecore') `
  -Target (Join-Path $fixtureDir 'CollisionTarget.ecore') `
  -TaggedRequirements (Join-Path $fixtureDir 'collision.requirements.tagged.txt') `
  -ReqOutput $collisionReq -ForwardOutput $collisionForward `
  -RuntimeDir $RuntimeDir -SourceChain 1 -TargetChain 1 `
  -TypeMatch fuzzy -Review none -CheckTargetFeatures $false

$collisionText = (Get-Content -LiteralPath $collisionReq -Raw) +
  (Get-Content -LiteralPath $collisionForward -Raw)
if (-not $collisionText.Contains('Link |--> Link')) {
  throw 'EClass collision adapter did not preserve Link |--> Link.'
}
if ($collisionText.Contains('__DssTarget')) {
  throw 'EClass collision adapter leaked an internal alias into TL output.'
}
Write-Host '[PASS] duplicate EClass simple-name adapter'
Write-Host ">>> DSS standalone tests passed. Output: $forward"

