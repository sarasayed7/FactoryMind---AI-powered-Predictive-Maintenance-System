from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_invalid_sensor_data():
    payload = {
        "machine_id": "M-101",
        "air_temperature": 300.0,
        "process_temperature": 310.0,
        "rotational_speed": -100,
        "torque": 40.0,
        "tool_wear": 100
    }

    response = client.post(
        "/machines/M-101/assess",
        json=payload
    )

    # Your assertions go here
    assert response.status_code == 422
    assert "detail" in response.json()

# NOTE: to run --> python -m pytest tests/test_assessment_api.py -v