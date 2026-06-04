from app.security.regex_detector import RegexDetector


def test_detects_sql_injection():
    code = 'cursor.execute("SELECT * FROM users WHERE id=" + user_id)'
    findings = RegexDetector().scan(code, "python")
    categories = {f.category.value for f in findings}
    assert "SQL_INJECTION" in categories


def test_detects_command_injection():
    code = "import os\nos.system(user_input)"
    findings = RegexDetector().scan(code, "python")
    assert any(f.category.value == "COMMAND_INJECTION" for f in findings)


def test_safe_code_minimal_findings():
    code = "def add(a, b):\n    return a + b\n"
    findings = RegexDetector().scan(code, "python")
    critical = [f for f in findings if f.severity.value == "CRITICAL"]
    assert len(critical) == 0
