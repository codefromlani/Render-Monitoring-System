from fastapi.testclient import TestClient
from main import app
from schemas import monitor_state


def test_stop_monitoring():
    with TestClient(app) as client:
        test_app_url = "https://example.com/"
        monitor_state[test_app_url] = {
            "is_active": True,
            "last_active": "2024-02-19",
            "current_status": "running"
        }
       
        response = client.post(f"/monitor/stop?app_url={test_app_url}")  
        assert response.status_code == 200
        assert response.json() == {
            "status": "stopped",
            "app": test_app_url
        }
        assert test_app_url not in monitor_state

        response = client.post(f"/monitor/stop?app_url=nonexistent-app")
        assert response.status_code == 404
        assert response.json()["detail"] == "App nonexistent-app not found in monitoring list"
