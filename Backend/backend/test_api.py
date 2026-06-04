import requests
import json

code = """import subprocess
user_input = "ls"
subprocess.call(user_input, shell=True)"""

r = requests.post("http://localhost:8000/analyze", json={"code": code, "language": "python"})
data = r.json()
print("Status:", r.status_code)
findings = data.get("findings", [])
print(f"Total findings: {len(findings)}")
for f in findings:
    print(f"  [{f['source']}] {f['category']} - {f['description'][:80]}")
