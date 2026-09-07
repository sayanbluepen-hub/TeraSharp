import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_export_cog_download():
    response = client.get("/export/mumbai_coastal?layer=sr&format=cog")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/tiff"
    assert "attachment" in response.headers["content-disposition"]
    assert "mumbai_coastal_sr_cog.tif" in response.headers["content-disposition"]
    assert response.headers["x-geospatial-crs"] == "EPSG:4326"
    assert len(response.content) > 0

def test_export_entropy_and_fractions():
    for layer in ["entropy", "fractions"]:
        response = client.get(f"/export/mumbai_coastal?layer={layer}&format=cog")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/tiff"

def test_export_metadata_mode():
    response = client.get("/export/mumbai_coastal?layer=sr&format=cog&metadata_only=true")
    assert response.status_code == 200
    data = response.json()
    assert data["region"] == "mumbai_coastal"
    assert data["layer"] == "sr"
    assert data["format"] == "cog"
    assert data["crs"] == "EPSG:4326"
    assert data["resolution_m"] == 2.5
    assert data["file_size_bytes"] > 0

def test_export_invalid_parameters():
    # Invalid layer
    res1 = client.get("/export/mumbai_coastal?layer=invalid_layer")
    assert res1.status_code == 400
    assert res1.json()["detail"]["code"] == "INVALID_LAYER"

    # Invalid format
    res2 = client.get("/export/mumbai_coastal?layer=sr&format=pdf")
    assert res2.status_code == 400
    assert res2.json()["detail"]["code"] == "INVALID_FORMAT"

def test_tiles_serving():
    # SR tile
    res_sr = client.get("/tiles/sr/10/500/500.png")
    assert res_sr.status_code == 200
    assert res_sr.headers["content-type"] == "image/png"
    assert len(res_sr.content) > 0

    # Entropy tile
    res_entropy = client.get("/tiles/entropy/10/500/500.png")
    assert res_entropy.status_code == 200
    assert res_entropy.headers["content-type"] == "image/png"

    # Invalid tile layer
    res_invalid = client.get("/tiles/unknown_layer/10/500/500.png")
    assert res_invalid.status_code == 400

def test_regions_list():
    response = client.get("/regions")
    assert response.status_code == 200
    regions = response.json()
    region_ids = [r["id"] for r in regions]
    assert "mumbai_coastal" in region_ids
    assert "sundarbans_delta" in region_ids
    assert "delhi_fringe" in region_ids

def test_wmts_capabilities():
    response = client.get("/tiles/capabilities.xml")
    assert response.status_code == 200
    assert "application/xml" in response.headers["content-type"]
    assert "<Capabilities" in response.text
