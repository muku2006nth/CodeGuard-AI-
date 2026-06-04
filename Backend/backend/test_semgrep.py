import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.security.semgrep_runner import SemgrepRunner

code = """
import subprocess
user_input = "ls"
subprocess.call(user_input, shell=True)
"""

print("=" * 60)
print("SEMGREP INTEGRATION TEST")
print("=" * 60)
print(f"Test code:\n{code}")
print("-" * 60)

runner = SemgrepRunner()
print(f"Semgrep available: {runner.is_available()}")
print(f"Rules dir: {runner.rules_dir}")
print("-" * 60)

findings = runner.scan(code, "python")
print(f"Findings count: {len(findings)}")
print("-" * 60)

for i, f in enumerate(findings, 1):
    print(f"[{i}] Category: {f.category.name}")
    print(f"    Severity: {f.severity.value}")
    print(f"    Rule ID:  {f.rule_id}")
    print(f"    Line:     {f.line_number}")
    print(f"    Message:  {f.description[:100]}")
    print()

if any(f.category.name == "COMMAND_INJECTION" for f in findings):
    print("[PASS] SUCCESS: COMMAND_INJECTION detected!")
else:
    print("[FAIL] COMMAND_INJECTION not detected")
