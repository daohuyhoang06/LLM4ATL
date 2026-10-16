param(
  [string]$OriginalAgileUmlDir
)

$ErrorActionPreference = 'Stop'
$moduleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$llm4atlRoot = Split-Path -Parent (Split-Path -Parent $moduleRoot)
$workspaceRoot = Split-Path -Parent $llm4atlRoot
if ([string]::IsNullOrWhiteSpace($OriginalAgileUmlDir)) {
  $OriginalAgileUmlDir = Join-Path $workspaceRoot 'AgileUML\umlrsds'
}
$fixtureDir = Join-Path $moduleRoot 'tests\fixtures'
$resultRoot = Join-Path $moduleRoot 'build\special-cases'

$cases = @(
  @{
    Name = 'RichGraphCollisionEnum'
    Source = 'SpecialRichGraphSource.ecore'
    Target = 'SpecialRichGraphTarget.ecore'
    Requirements = 'SpecialRichGraph.requirements.txt'
    SourceChain = 1
    TargetChain = 1
    TypeMatch = 'fuzzy'
    Expected = @('GraphModel |--> Diagram', 'Node |--> Node')
  },
  @{
    Name = 'AbstractInheritanceExactTypes'
    Source = 'SpecialInheritanceSource.ecore'
    Target = 'SpecialInheritanceTarget.ecore'
    Requirements = 'SpecialInheritance.requirements.txt'
    SourceChain = 1
    TargetChain = 1
    TypeMatch = 'exact'
    Expected = @('WorkItem |--> Artifact', 'Task |--> Job', 'Bug |--> Defect')
  },
  @{
    Name = 'DeepFeatureChain'
    Source = 'SpecialDeepChainSource.ecore'
    Target = 'SpecialDeepChainTarget.ecore'
    Requirements = 'SpecialDeepChain.requirements.txt'
    SourceChain = 2
    TargetChain = 1
    TypeMatch = 'fuzzy'
    Expected = @('Company |--> Catalogue', 'Employee |--> Entry')
  },
  @{
    Name = 'NoRequirementSeeds'
    Source = 'SpecialSeedlessSource.ecore'
    Target = 'SpecialSeedlessTarget.ecore'
    Requirements = 'SpecialSeedless.requirements.txt'
    SourceChain = 1
    TargetChain = 1
    TypeMatch = 'fuzzy'
    Expected = @('Alpha |-->', 'Beta |-->')
  }
)

foreach ($case in $cases) {
  Write-Host "=== $($case.Name) ==="
  $caseOutput = Join-Path $resultRoot $case.Name
  & (Join-Path $moduleRoot 'compare_with_original.ps1') `
    -Source (Join-Path $fixtureDir $case.Source) `
    -Target (Join-Path $fixtureDir $case.Target) `
    -Requirements (Join-Path $fixtureDir $case.Requirements) `
    -OutputDir $caseOutput `
    -OriginalAgileUmlDir $OriginalAgileUmlDir `
    -SourceChain $case.SourceChain -TargetChain $case.TargetChain `
    -TypeMatch $case.TypeMatch

  $forward = Get-Content -LiteralPath (Join-Path $caseOutput 'adapter\forward.tl') -Raw
  foreach ($expected in $case.Expected) {
    if (-not $forward.Contains($expected)) {
      throw "$($case.Name) is missing expected mapping: $expected"
    }
  }
  if ($forward.Contains('__DssTarget')) {
    throw "$($case.Name) leaked an internal collision alias"
  }
  Write-Host "[PASS] $($case.Name) semantic assertions"
}

$seedlessReq = Get-Content -LiteralPath `
  (Join-Path $resultRoot 'NoRequirementSeeds\adapter\req.tl') -Raw
if ($seedlessReq.Trim().Length -ne 0) {
  throw 'NoRequirementSeeds unexpectedly produced a requirements mapping seed.'
}
Write-Host '[PASS] no-seed case really entered DSS with an empty req.tl'

$repeatOutput = Join-Path $resultRoot 'NoRequirementSeedsRepeat'
& (Join-Path $moduleRoot 'compare_with_original.ps1') `
  -Source (Join-Path $fixtureDir 'SpecialSeedlessSource.ecore') `
  -Target (Join-Path $fixtureDir 'SpecialSeedlessTarget.ecore') `
  -Requirements (Join-Path $fixtureDir 'SpecialSeedless.requirements.txt') `
  -OutputDir $repeatOutput -OriginalAgileUmlDir $OriginalAgileUmlDir `
  -SourceChain 1 -TargetChain 1 -TypeMatch fuzzy

$first = (Get-Content -LiteralPath `
  (Join-Path $resultRoot 'NoRequirementSeeds\adapter\forward.tl') -Raw) -replace "`r`n", "`n"
$second = (Get-Content -LiteralPath `
  (Join-Path $repeatOutput 'adapter\forward.tl') -Raw) -replace "`r`n", "`n"
if ($first -cne $second) {
  throw 'No-seed DSS result was not deterministic across repeated runs.'
}
Write-Host '[PASS] no-seed DSS selection is deterministic across repeated runs'
Write-Host ">>> All special DSS cases passed: $resultRoot"
