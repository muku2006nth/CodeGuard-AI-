from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_analyze():
    r = client.post(
        "/analyze",
        json={"code": "os.system('ls')", "language": "python"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "risk_score" in data
    assert "findings" in data
    assert "report_id" in data


def test_reports_list():
    client.post("/analyze", json={"code": "x=1", "language": "python"})
    r = client.get("/reports")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
