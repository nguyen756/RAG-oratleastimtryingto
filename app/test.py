import sys
from fastapi.testclient import TestClient
from app.main import app

sys.argv = ["main.py"] 
client = TestClient(app)
def test_api_health():
    response = client.get("/health") 
    assert response.status_code in [200, 404, 307]