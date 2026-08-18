import os
import sys
import glob
import subprocess
import shutil

# Thêm thư mục ATL_Parser vào sys.path để import fastchrf
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ATL_PARSER_DIR = os.path.join(PROJECT_ROOT, 'ATL_Parser')
sys.path.append(ATL_PARSER_DIR)

try:
    from fastchrf import aggregate_chrf
    FASTCHRF_AVAILABLE = True
except ImportError:
    FASTCHRF_AVAILABLE = False
    print("WARNING: Cannot import fastchrf from ATL_Parser.")

ATL_TESTS_DIR = os.path.join(PROJECT_ROOT, 'ATL_Tests')
AST2ATL_DIR = r"D:\LLM4MTLs goc\LLM-based code generation for MTL\LLM-based code generation for MTL\Workflows\n8n-docker\mtl_snippets\ATLAS_transformation_language\responses\gemini-2-5-pro\few_shot"
REFERENCES_DIR = os.path.join(ATL_PARSER_DIR, 'src', 'test', 'resources', 'other_references')
TEST_REF_DIR = os.path.join(ATL_TESTS_DIR, 'src', 'main', 'atl')

FILE_TO_TEST = {
    "AmaltheaToAscet_All":  "org.example.AmaltheaToAscetAllExecutionTest",
    "BibTeX2DocBook_All":   "org.example.BibTeX2DocBookAllExecutionTest",
    "CPL2SPL_All":          "org.example.CPL2SPLAllExecutionTest",
    "Class2Interface_All":  "org.example.Class2InterfaceAllExecutionTest",
    "DSL2KM3_All":          "org.example.DSL2KM3AllExecutionTest",
    "Document2Report_All":  "org.example.Document2ReportAllExecutionTest",
    "FamiliesToPersons_All":"org.example.FamiliesToPersonsAllExecutionTest",
    "Grafcet2PetriNet_All": "org.example.Grafcet2PetriNetAllExecutionTest",
    "IEEE1471_2_MoDAF_All": "org.example.IEEE1471_2_MoDAFAllExecutionTest",
    "Item2Product_All":     "org.example.Item2ProductAllExecutionTest",
    "Make2Ant_All":         "org.example.Make2AntAllExecutionTest",
    "NetworkToGraph_All":   "org.example.NetworkToGraphAllExecutionTest",
    "PetriNet2Grafcet_All": "org.example.PetriNet2GrafcetAllExecutionTest",
    "User2Account_All":     "org.example.User2AccountAllExecutionTest",
    "XML2DSL_All":          "org.example.XML2DSLAllExecutionTest",
}

def check_atl_syntax(atl_file_path):
    mvn_cmd = 'mvn.cmd' if os.name == 'nt' else 'mvn'
    result = subprocess.run(
        [mvn_cmd, '-q', 'exec:java',
         '-Dexec.mainClass=com.example.atlparser.ATLParserMain',
         f'-Dexec.args={atl_file_path}'],
        cwd=ATL_PARSER_DIR,
        capture_output=True,
        text=True
    )
    if "Error" in result.stdout or "Error" in result.stderr:
        return False
    # CPL2SPL_All or others might output "Error" or "Problem". Let's check exit code instead.
    # Actually ATLParserMain prints "Valid" or something.
    if "Valid ATL" in result.stdout or result.returncode == 0 and "Problem" not in result.stdout:
        # We assume valid if it doesn't print Problem
        pass
    
    # We will use the same check as testATLParsedRate.py
    is_valid = True
    problem_count = 0
    for line in result.stdout.splitlines():
        if "Problem" in line:
            is_valid = False
            problem_count += 1
    for line in result.stderr.splitlines():
        if "Exception" in line or "Error" in line:
            is_valid = False
            problem_count += 1
    return is_valid

def run_junit_test(test_class, source_atl_path, target_filename):
    dest_path = os.path.join(TEST_REF_DIR, target_filename)
    if os.path.exists(dest_path):
        os.remove(dest_path)
    shutil.copy2(source_atl_path, dest_path)
    
    mvn_cmd = 'mvn.cmd' if os.name == 'nt' else 'mvn'
    result = subprocess.run(
        [mvn_cmd, '-q', 'test', f'-Dtest={test_class}'],
        cwd=ATL_TESTS_DIR,
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def main():
    atl_files = glob.glob(os.path.join(AST2ATL_DIR, '*.atl'))
    if not atl_files:
        print(f"No .atl files found in {AST2ATL_DIR}")
        return

    total_files = 0
    unparsed_count = 0
    chrf_scores = []
    passed_tests = 0

    print("=" * 50)
    print("Evaluating AST2ATL Folder")
    print("=" * 50)

    for atl_path in atl_files:
        filename = os.path.basename(atl_path)
        base_name = os.path.splitext(filename)[0]
        total_files += 1

        print(f"\nProcessing: {filename}")

        # 1. Parse Rate
        is_parsed = check_atl_syntax(atl_path)
        if not is_parsed:
            unparsed_count += 1
        print(f"  - Parsed: {is_parsed}")

        # 2. ChrF Score
        chrf = 0.0
        ref_path = os.path.join(REFERENCES_DIR, filename)
        if os.path.exists(ref_path) and FASTCHRF_AVAILABLE:
            with open(atl_path, 'r', encoding='utf-8') as f:
                gen_content = f.read().strip()
            with open(ref_path, 'r', encoding='utf-8') as f:
                ref_content = f.read().strip()
            
            if gen_content:
                score = aggregate_chrf([[gen_content]], [[ref_content]])
                chrf = float(score[0][0])
            chrf_scores.append(chrf)
            print(f"  - ChrF: {chrf:.4f}")
        else:
            print(f"  - ChrF: Skipping (Ref missing or fastchrf not available)")

        # 3. Pass@1 (Execution Test)
        is_passed = False
        if base_name in FILE_TO_TEST:
            test_class = FILE_TO_TEST[base_name]
            is_passed = run_junit_test(test_class, atl_path, filename)
            if is_passed:
                passed_tests += 1
        print(f"  - Pass@1: {is_passed}")

    # Calculate metrics
    avg_unparsed = (unparsed_count / total_files) * 100 if total_files > 0 else 0
    mean_chrf = sum(chrf_scores) / len(chrf_scores) if chrf_scores else 0
    pass_at_1 = (passed_tests / total_files) * 100 if total_files > 0 else 0

    print("\n" + "=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)
    print(f"Total Files Tested: {total_files}")
    print(f"Average Unparsed Rate: {avg_unparsed:.2f}%")
    print(f"Mean ChrF Score: {mean_chrf:.2f}")
    print(f"Pass@1: {pass_at_1:.2f}%")

if __name__ == "__main__":
    main()
