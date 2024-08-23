import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_get_schedule():
    json_input = {
        "soc_start": 20,
        "soc_max": 90,
        "soc_min": 10,
        "soc_target": 90,
        "power_capacity": 10,
        "conversion_efficiency": 1.0,
        "storage_capacity": 100,
        "prices": {
            "production": [7, 2, 3, 4, 1, 6],
            "consumption": [8, 3, 4, 5, 2, 7]
        }
    }

    response = client.post("/schedule", json=json_input)

    assert response.status_code == 200
    data = response.json()

    expected_keys = {"total_cost", "charge_schedule", "discharge_schedule", "soc_schedule"}
    assert isinstance(data, dict)
    assert expected_keys.issubset(data.keys())
    assert isinstance(data["total_cost"], (int, float))
    assert all(isinstance(x, (int, float)) for x in data["charge_schedule"])
    assert all(isinstance(x, (int, float)) for x in data["discharge_schedule"])
    assert all(isinstance(x, (int, float)) for x in data["soc_schedule"])

def test_invalid_prices():
    json_input = {
        "prices": {
            "production": [7, 2, 3, 4, 1, 6],
            "consumption": [8, 3, 4, 5, 2]  # Mismatched length
        },
        "soc_start": 20,
        "soc_min": 10,
        "soc_max": 90,
        "soc_target": 90,
        "power_capacity": 10,
        "conversion_efficiency": 1.0,
        "storage_capacity": 100
    }

    response = client.post("/schedule", json=json_input)

    assert response.status_code == 422
    # assert response.json()["detail"] == 'Length of production and consumption must be the same'
