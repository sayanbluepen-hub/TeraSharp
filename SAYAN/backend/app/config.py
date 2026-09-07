import os
from pathlib import Path
from typing import Dict, Any, List
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

class RegionConfig(BaseModel):
    id: str
    name: str
    description: str
    center_lat: float
    center_lon: float
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    default_zoom: int = 12

    def contains_point(self, lat: float, lon: float) -> bool:
        """Check if coordinates fall within the defined region bounding box."""
        return (self.min_lat <= lat <= self.max_lat) and (self.min_lon <= lon <= self.max_lon)

class Settings(BaseModel):
    app_name: str = "NTRO Satellite Super-Resolution API"
    app_version: str = "1.0.0"
    app_description: str = (
        "High-performance geospatial API providing 4x Super-Resolution enhancement "
        "(10m Sentinel-2 to 2.5m ground sampling distance), uncertainty/entropy estimation, "
        "sub-pixel land cover fractions, and XYZ/WMTS tile streaming."
    )
    
    # Resolution specifications (NTRO challenge requirement: 10m to <4m, targeting ~2.5m)
    input_resolution_m: float = 10.0
    target_resolution_m: float = 2.5
    scale_factor: int = 4
    
    # Data Storage Directories
    data_dir: Path = DATA_DIR
    sentinel_dir: Path = DATA_DIR / "sentinel"
    sr_output_dir: Path = DATA_DIR / "sr_output"
    entropy_dir: Path = DATA_DIR / "entropy"
    fractions_dir: Path = DATA_DIR / "fractions"
    
    # Supported Demo Regions
    regions: Dict[str, RegionConfig] = {
        "mumbai_coastal": RegionConfig(
            id="mumbai_coastal",
            name="Mumbai Coastal Zone",
            description="Urban coastal mega-city zone with ports, high density built-up, and mangroves.",
            center_lat=19.0760,
            center_lon=72.8777,
            min_lat=18.8500,
            max_lat=19.3000,
            min_lon=72.7500,
            max_lon=73.0500,
            default_zoom=12
        ),
        "sundarbans_delta": RegionConfig(
            id="sundarbans_delta",
            name="Sundarbans Biosphere Delta",
            description="Tidally active mangrove eco-region with dynamic waterways and mudflats.",
            center_lat=21.9497,
            center_lon=88.9000,
            min_lat=21.6000,
            max_lat=22.3000,
            min_lon=88.5000,
            max_lon=89.3000,
            default_zoom=11
        ),
        "delhi_fringe": RegionConfig(
            id="delhi_fringe",
            name="Delhi NCR Peri-Urban Fringe",
            description="Rapidly developing urban-rural interface with cropland, highways, and residential clusters.",
            center_lat=28.6139,
            center_lon=77.2090,
            min_lat=28.4000,
            max_lat=28.8500,
            min_lon=76.9000,
            max_lon=77.4500,
            default_zoom=12
        )
    }

    def ensure_directories(self) -> None:
        """Ensure all required data directories exist."""
        for d in [self.data_dir, self.sentinel_dir, self.sr_output_dir, self.entropy_dir, self.fractions_dir]:
            d.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()
