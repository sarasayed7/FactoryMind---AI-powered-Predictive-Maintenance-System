from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)

# These are automated tests for the FastAPI application. They test the health endpoint, invalid sensor data handling, and the prediction endpoint with mocked behavior.

def test_health_endpoint():
    response = client.get('/health')

    #assertions
    assert response.status_code == 200
    assert response.json() == {'status': 'healthy'}

def test_invalid_sensor_data():
    sensor_data = {
        "air_temperature": 300.5,
        "process_temperature": 310.2,
        "rotational_speed": -100,
        "torque": 45.3,
        "tool_wear": 180
    }
    response = client.post('/predict', json=sensor_data)

    assert response.status_code == 422 # Invalid input data
    assert 'detail' in response.json()

def test_predict_with_mock():
    sensor_data = {
        "machine_id": "M-101",
        "air_temperature": 300.5,
        "process_temperature": 310.2,
        "rotational_speed": 1450,
        "torque": 45.3,
        "tool_wear": 180
    }

    with patch("app.main.run_prediction") as mock_predict:
        mock_predict.return_value = {
            "predicted_class": 1,
            "failure_probability": 0.85,
            "status": "failure_risk"
        }    
        response = client.post('/predict', json=sensor_data)

        assert response.status_code == 200
        assert response.json() == {
            "predicted_class": 1,
            "failure_probability": 0.85,
            "status": "failure_risk"
        }
# NOTE: RUN Command --> python -m pytest tests/test_api.py -v