import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_get_schedule():
    response = client.get(
        "/schedule",
        params={
            "soc_start": 10.0,
            "soc_min": 0.0,
            "soc_max": 50.0,
            "soc_target": 40.0,
            "power_capacity": 10.0,
            "conversion_efficiency": 0.9,
            "storage_capacity": 50.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_cost" in data
    assert "charge_schedule" in data
    assert "discharge_schedule" in data
    assert "soc_schedule" in data

def test_get_schedule_top_up():
    response = client.get(
        "/schedule",
        params={
            "soc_start": 10.0,
            "soc_min": 0.0,
            "soc_max": 50.0,
            "soc_target": 100.0,
            "power_capacity": 10.0,
            "conversion_efficiency": 0.9,
            "storage_capacity": 100.0,
            "top_up": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_cost" in data
    assert "charge_schedule" in data
    assert "discharge_schedule" in data
    assert "soc_schedule" in data

def test_get_schedule_infeasible():
    response = client.get(
        "/schedule",
        params={
            "soc_start": 90.0,
            "soc_min": 0.0,
            "soc_max": 50.0,
            "soc_target": 100.0,
            "power_capacity": 10.0,
            "conversion_efficiency": 0.9,
            "storage_capacity": 50.0
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Infeasible problem or no solution found"}
