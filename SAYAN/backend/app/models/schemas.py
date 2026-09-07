from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator

class LandCoverFractions(BaseModel):
    built_up: float = Field(..., ge=0.0, le=1.0, description="Fraction of urban, built structures and impervious surfaces")
    vegetation: float = Field(..., ge=0.0, le=1.0, description="Fraction of trees, canopy, and dense natural green cover")
    water: float = Field(..., ge=0.0, le=1.0, description="Fraction of open water, rivers, ocean, and lakes")
    bare_soil: float = Field(..., ge=0.0, le=1.0, description="Fraction of unpaved ground, mud, and bare soil")
    cropland: float = Field(..., ge=0.0, le=1.0, description="Fraction of agricultural fields and cultivated vegetation")

    @field_validator("cropland")
    @classmethod
    def validate_fraction_sum(cls, v, info):
        values = info.data
        if "built_up" in values and "vegetation" in values and "water" in values and "bare_soil" in values:
            total = round(values["built_up"] + values["vegetation"] + values["water"] + values["bare_soil"] + v, 3)
            if not (0.98 <= total <= 1.02):
                raise ValueError(f"Fractions must sum to approximately 1.0 (received sum: {total})")
        return v

class SpectralBands(BaseModel):
    B02: float = Field(..., ge=0.0, le=1.0, description="Sentinel-2 Blue band (490 nm) normalized reflectance")
    B03: float = Field(..., ge=0.0, le=1.0, description="Sentinel-2 Green band (560 nm) normalized reflectance")
    B04: float = Field(..., ge=0.0, le=1.0, description="Sentinel-2 Red band (665 nm) normalized reflectance")
    B08: float = Field(..., ge=0.0, le=1.0, description="Sentinel-2 NIR band (842 nm) normalized reflectance")

class InferenceRequest(BaseModel):
    region: str = Field(default="mumbai_coastal", description="Target geographical region (e.g. mumbai_coastal, sundarbans_delta, delhi_fringe)")
    image_id: Optional[str] = Field(default=None, description="Optional Sentinel-2 L2A Granule or Product ID")
    input_resolution: Optional[float] = Field(default=10.0, ge=1.0, le=100.0, description="Input ground sampling distance in meters (Sentinel-2 is 10m)")
    target_resolution: Optional[float] = Field(default=2.5, ge=0.5, le=10.0, description="Target ground sampling distance in meters (e.g. 2.5m for 4x enhancement)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "region": "mumbai_coastal",
                "image_id": "S2A_MSIL2A_20240315T052651_N0510_R105_T43QDA",
                "input_resolution": 10.0,
                "target_resolution": 2.5
            }
        }
    }

class InferenceResponse(BaseModel):
    status: str = Field(default="completed", description="Execution status of the Super-Resolution pipeline")
    region: str = Field(..., description="Region identifier processed")
    input_resolution_m: float = Field(..., description="Original input resolution in meters")
    output_resolution_m: float = Field(..., description="Enhanced output resolution in meters")
    scale_factor: int = Field(..., description="Super-resolution scaling factor (e.g. 4x)")
    processing_time_seconds: float = Field(..., description="Wall-clock execution time in seconds")
    sr_image_url: str = Field(..., description="XYZ tile endpoint template for Super-Resolution enhanced image")
    entropy_map_url: str = Field(..., description="XYZ tile endpoint template for pixel-level uncertainty/entropy map")
    download_cog_url: str = Field(..., description="Direct download URL for Super-Resolution Cloud Optimized GeoTIFF")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Geographic bounds, CRS, and radiometric metadata")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "completed",
                "region": "mumbai_coastal",
                "input_resolution_m": 10.0,
                "output_resolution_m": 2.5,
                "scale_factor": 4,
                "processing_time_seconds": 1.82,
                "sr_image_url": "/tiles/sr/{z}/{x}/{y}.png",
                "entropy_map_url": "/tiles/entropy/{z}/{x}/{y}.png",
                "download_cog_url": "/export/mumbai_coastal?layer=sr&format=cog",
                "metadata": {
                    "crs": "EPSG:4326",
                    "bounds": [72.75, 18.85, 73.05, 19.30],
                    "channels": ["B04", "B03", "B02", "B08"],
                    "model_backend": "MOCK_SEN2SR_PIPELINE"
                }
            }
        }
    }

class PixelQuery(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in WGS84 decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in WGS84 decimal degrees")
    region: str = Field(default="mumbai_coastal", description="Region key")

class PixelResponse(BaseModel):
    latitude: float
    longitude: float
    fractions: LandCoverFractions
    entropy: float = Field(..., ge=0.0, le=1.0, description="Information entropy uncertainty score (0 = high confidence, 1 = highly uncertain)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score = 1.0 - entropy")
    spectral: SpectralBands

    model_config = {
        "json_schema_extra": {
            "example": {
                "latitude": 19.0760,
                "longitude": 72.8777,
                "fractions": {
                    "built_up": 0.35,
                    "vegetation": 0.25,
                    "water": 0.10,
                    "bare_soil": 0.20,
                    "cropland": 0.10
                },
                "entropy": 0.23,
                "confidence": 0.77,
                "spectral": {
                    "B04": 0.31,
                    "B03": 0.28,
                    "B02": 0.22,
                    "B08": 0.51
                }
            }
        }
    }

class RegionInfo(BaseModel):
    id: str
    name: str
    description: str
    center: List[float] = Field(..., description="[lat, lon]")
    bounds: List[float] = Field(..., description="[min_lon, min_lat, max_lon, max_lat]")
    default_zoom: int

class ExportResponse(BaseModel):
    region: str
    layer: str
    format: str
    file_name: str
    file_size_bytes: int
    crs: str
    resolution_m: float
    bounds: List[float]
    download_url: str

class ErrorDetail(BaseModel):
    error: str
    code: str
    detail: Optional[str] = None
    allowed_values: Optional[List[str]] = None
