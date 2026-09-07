import pytest
import numpy as np
from pathlib import Path
from backend.app.config import settings
from backend.app.services.geospatial_service import geospatial_service

def test_latlon_to_pixel_conversion():
    region = settings.regions["mumbai_coastal"]
    bounds = (region.min_lon, region.min_lat, region.max_lon, region.max_lat)
    width = 256
    height = 256

    # Center coordinates should map close to center pixel (128, 128)
    row, col = geospatial_service.latlon_to_pixel(
        bounds=bounds,
        width=width,
        height=height,
        lon=region.center_lon,
        lat=region.center_lat
    )
    assert 100 <= row <= 160
    assert 100 <= col <= 160

    # Invert pixel back to lat/lon
    lon_back, lat_back = geospatial_service.pixel_to_latlon(
        bounds=bounds,
        width=width,
        height=height,
        row=row,
        col=col
    )
    assert lon_back == pytest.approx(region.center_lon, abs=0.01)
    assert lat_back == pytest.approx(region.center_lat, abs=0.01)

def test_latlon_out_of_bounds_raises_error():
    bounds = (72.75, 18.85, 73.05, 19.30)
    with pytest.raises(ValueError, match="out of raster bounds"):
        geospatial_service.latlon_to_pixel(bounds, 256, 256, lon=80.0, lat=25.0)

def test_read_and_write_geotiff(tmp_path: Path):
    test_file = tmp_path / "test_geo.tif"
    data = np.random.randint(0, 255, size=(4, 64, 64), dtype=np.uint8)
    bounds = (72.75, 18.85, 73.05, 19.30)

    # Write
    written_path = geospatial_service.write_geotiff(test_file, data, bounds, crs="EPSG:4326")
    assert written_path.exists()

    # Read back
    read_data, meta = geospatial_service.read_raster(written_path)
    assert read_data.shape == (4, 64, 64)
    assert meta["width"] == 64
    assert meta["height"] == 64
    assert meta["count"] == 4
    assert "4326" in str(meta["crs"])

def test_raster_metadata(tmp_path: Path):
    test_file = tmp_path / "test_meta.tif"
    data = np.zeros((1, 32, 32), dtype=np.uint8)
    bounds = (0.0, 0.0, 1.0, 1.0)
    geospatial_service.write_geotiff(test_file, data, bounds)

    meta = geospatial_service.get_raster_metadata(test_file)
    assert meta["width"] == 32
    assert meta["height"] == 32
    assert meta["count"] == 1
    assert meta["file_size_bytes"] > 0
