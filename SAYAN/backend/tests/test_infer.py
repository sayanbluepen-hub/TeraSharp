import time
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_infer_success_mumbai():
    start = time.perf_counter()
    response = client.post("/infer", json={"region": "mumbai_coastal"})
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["region"] == "mumbai_coastal"
    assert data["input_resolution_m"] == 10.0
    assert data["output_resolution_m"] == 2.5
    assert data["scale_factor"] == 4
    assert data["processing_time_seconds"] >= 1.5
    assert "/tiles/sr/{z}/{x}/{y}.png" in data["sr_image_url"]
    assert "/tiles/entropy/{z}/{x}/{y}.png" in data["entropy_map_url"]
    assert "download_cog_url" in data
    assert "metadata" in data
    assert data["metadata"]["crs"] == "EPSG:4326"

def test_infer_all_regions():
    for region in ["sundarbans_delta", "delhi_fringe"]:
        response = client.post("/infer", json={"region": region})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["region"] == region
        assert data["output_resolution_m"] <= 4.0

def test_infer_invalid_region():
    response = client.post("/infer", json={"region": "atlantis_ocean"})
    assert response.status_code == 400
    error = response.json()["detail"]
    assert error["code"] == "INVALID_REGION"
    assert "allowed_values" in error
    assert "mumbai_coastal" in error["allowed_values"]

def test_infer_custom_parameters():
    payload = {
        "region": "mumbai_coastal",
        "image_id": "S2_CUSTOM_2024_01",
        "input_resolution": 10.0,
        "target_resolution": 2.5
    }
    response = client.post("/infer", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["input_resolution_m"] == 10.0
    assert data["output_resolution_m"] == 2.5
    assert data["scale_factor"] == 4
    assert data["metadata"]["image_id"] == "S2_CUSTOM_2024_01"
