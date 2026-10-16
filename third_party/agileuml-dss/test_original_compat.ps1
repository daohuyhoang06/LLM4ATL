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
$metamodelDir = Join-Path $llm4atlRoot 'LLM4ATL_Project\Neuro_Symbolic_Pipeline\input\ATL_metamodel'
$requirementsDir = Join-Path $moduleRoot 'requirements'
$resultRoot = Join-Path $moduleRoot 'build\original-compat'

$cases = @(
  @{
    Name = 'FamiliesToPersons'
    Source = 'families.ecore'
    Target = 'persons.ecore'
    Requirements = 'FamiliesToPersons_cnl.txt'
  },
  @{
    Name = 'Class2Interface'
    Source = 'Class.ecore'
    Target = 'Interface.ecore'
    Requirements = 'Class2Interface_cnl.txt'
  },
  @{
    Name = 'Document2Report'
    Source = 'Document.ecore'
    Target = 'Report.ecore'
    Requirements = 'Document2Report_cnl.txt'
  }
)

foreach ($case in $cases) {
  Write-Host "=== $($case.Name) ==="
  & (Join-Path $moduleRoot 'compare_with_original.ps1') `
    -Source (Join-Path $metamodelDir $case.Source) `
    -Target (Join-Path $metamodelDir $case.Target) `
    -Requirements (Join-Path $requirementsDir $case.Requirements) `
    -OutputDir (Join-Path $resultRoot $case.Name) `
    -OriginalAgileUmlDir $OriginalAgileUmlDir `
    -SourceChain 1 -TargetChain 1 -TypeMatch fuzzy
}

Write-Host ">>> All original AgileUML compatibility cases passed: $resultRoot"
