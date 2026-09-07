import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_pixel_success():
    lat = 19.0760
    lon = 72.8777
    region = "mumbai_coastal"
    response = client.get(f"/pixel?lat={lat}&lon={lon}&region={region}")

    assert response.status_code == 200
    data = response.json()

    # Coordinates
    assert data["latitude"] == pytest.approx(lat, abs=1e-4)
    assert data["longitude"] == pytest.approx(lon, abs=1e-4)

    # Fractions
    fractions = data["fractions"]
    for key in ["built_up", "vegetation", "water", "bare_soil", "cropland"]:
        assert key in fractions
        assert 0.0 <= fractions[key] <= 1.0
    
    # Fractions sum verification
    fraction_sum = sum(fractions.values())
    assert fraction_sum == pytest.approx(1.0, abs=0.01)

    # Entropy and Confidence verification
    assert 0.0 <= data["entropy"] <= 1.0
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["confidence"] == pytest.approx(1.0 - data["entropy"], abs=0.01)

    # Spectral bands verification
    spectral = data["spectral"]
    for band in ["B02", "B03", "B04", "B08"]:
        assert band in spectral
        assert 0.0 <= spectral[band] <= 1.0

def test_pixel_deterministic_repeatability():
    lat = 19.1234
    lon = 72.8567
    region = "mumbai_coastal"

    res1 = client.get(f"/pixel?lat={lat}&lon={lon}&region={region}").json()
    res2 = client.get(f"/pixel?lat={lat}&lon={lon}&region={region}").json()

    assert res1 == res2, "Repeated queries for the same coordinate must return identical results"

def test_pixel_out_of_bounds():
    # Coordinates in Tokyo (far outside Mumbai)
    lat = 35.6762
    lon = 139.6503
    response = client.get(f"/pixel?lat={lat}&lon={lon}&region=mumbai_coastal")

    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "OUT_OF_BOUNDS"

def test_pixel_invalid_region():
    response = client.get("/pixel?lat=19.0760&lon=72.8777&region=invalid_region")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "INVALID_REGION"

def test_pixel_malformed_coordinates():
    # Latitude > 90
    response = client.get("/pixel?lat=95.0&lon=72.8777&region=mumbai_coastal")
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"

    # Non-numeric input
    response = client.get("/pixel?lat=invalid&lon=72.8777&region=mumbai_coastal")
    assert response.status_code == 422
