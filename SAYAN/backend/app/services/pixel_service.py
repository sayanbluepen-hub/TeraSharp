import hashlib
import math
from typing import Dict, Any, Tuple
from ..config import settings, RegionConfig
from ..models.schemas import LandCoverFractions, SpectralBands, PixelResponse
from .entropy_service import entropy_service

class PixelService:
    """
    Handles coordinate-level queries, extracting sub-pixel land cover fractions,
    uncertainty entropy, and multi-spectral reflectance profiles (Sentinel-2 B02, B03, B04, B08).
    """

    def query_pixel(self, lat: float, lon: float, region_id: str) -> PixelResponse:
        """
        Processes a clicked map coordinate for a specified region.
        Validates spatial bounds and computes deterministic, stable values.
        """
        # Validate coordinates
        if not (-90.0 <= lat <= 90.0):
            raise ValueError(f"Latitude {lat} is invalid. Must be between -90 and 90.")
        if not (-180.0 <= lon <= 180.0):
            raise ValueError(f"Longitude {lon} is invalid. Must be between -180 and 180.")

        region = settings.regions.get(region_id)
        if not region:
            raise KeyError(f"Invalid region '{region_id}'. Available: {list(settings.regions.keys())}")

        if not region.contains_point(lat, lon):
            raise ValueError(
                f"Coordinates ({lat:.4f}, {lon:.4f}) fall outside region '{region_id}' bounds: "
                f"lat [{region.min_lat}, {region.max_lat}], lon [{region.min_lon}, {region.max_lon}]."
            )

        # 1. Deterministic entropy & confidence
        entropy, confidence = entropy_service.calculate_pixel_entropy(lat, lon, region)

        # 2. Deterministic land cover fractions
        fractions = self._calculate_fractions(lat, lon, region)

        # 3. Deterministic Sentinel-2 spectral reflectance bands
        spectral = self._calculate_spectral(lat, lon, region, fractions)

        return PixelResponse(
            latitude=round(lat, 6),
            longitude=round(lon, 6),
            fractions=fractions,
            entropy=entropy,
            confidence=confidence,
            spectral=spectral
        )

    def _calculate_fractions(self, lat: float, lon: float, region: RegionConfig) -> LandCoverFractions:
        """
        Generates deterministic land cover fractions based on coordinates and geography.
        Guarantees that all 5 classes sum exactly to 1.00.
        """
        # Deterministic seed using SHA-256
        seed_str = f"frac_{lat:.5f}_{lon:.5f}_{region.id}"
        h = hashlib.sha256(seed_str.encode("utf-8")).hexdigest()
        v1 = int(h[0:4], 16) / 65535.0
        v2 = int(h[4:8], 16) / 65535.0
        v3 = int(h[8:12], 16) / 65535.0
        v4 = int(h[12:16], 16) / 65535.0
        v5 = int(h[16:20], 16) / 65535.0

        # Region-specific environmental biases
        if region.id == "mumbai_coastal":
            # Higher built-up in center, water along western edge
            is_west = 1.0 if lon < (region.center_lon - 0.05) else 0.0
            raw_built = 0.35 + 0.30 * v1
            raw_veg = 0.15 + 0.15 * v2
            raw_water = 0.10 + 0.40 * is_west * v3
            raw_soil = 0.10 + 0.10 * v4
            raw_crop = 0.05 + 0.05 * v5
        elif region.id == "sundarbans_delta":
            # Dominated by mangrove vegetation and tidal waterways
            raw_built = 0.05 + 0.05 * v1
            raw_veg = 0.40 + 0.35 * v2
            raw_water = 0.30 + 0.25 * v3
            raw_soil = 0.10 + 0.10 * v4
            raw_crop = 0.05 + 0.10 * v5
        else: # delhi_fringe
            # Mix of cropland, expanding built-up, and bare soil
            raw_built = 0.25 + 0.20 * v1
            raw_veg = 0.15 + 0.15 * v2
            raw_water = 0.05 + 0.05 * v3
            raw_soil = 0.20 + 0.15 * v4
            raw_crop = 0.30 + 0.25 * v5

        # Normalize to strictly sum to 1.00
        raw_total = raw_built + raw_veg + raw_water + raw_soil + raw_crop
        f_built = round(raw_built / raw_total, 2)
        f_veg = round(raw_veg / raw_total, 2)
        f_water = round(raw_water / raw_total, 2)
        f_soil = round(raw_soil / raw_total, 2)
        
        # Ensure residual sums exactly to 1.00
        f_crop = round(1.0 - (f_built + f_veg + f_water + f_soil), 2)
        if f_crop < 0.0:
            # Rebalance
            f_crop = 0.01
            f_built = round(1.0 - (f_crop + f_veg + f_water + f_soil), 2)

        return LandCoverFractions(
            built_up=f_built,
            vegetation=f_veg,
            water=f_water,
            bare_soil=f_soil,
            cropland=f_crop
        )

    def _calculate_spectral(
        self,
        lat: float,
        lon: float,
        region: RegionConfig,
        fractions: LandCoverFractions
    ) -> SpectralBands:
        """
        Derives realistic Sentinel-2 Top-Of-Canopy (L2A) surface reflectance values:
        - B02 (Blue, 490 nm)
        - B03 (Green, 560 nm)
        - B04 (Red, 665 nm)
        - B08 (NIR, 842 nm)
        
        Reflectance profiles correlate with land cover fractions (e.g. high NIR for vegetation,
        low NIR for water, higher red/blue for built-up and soil).
        """
        seed_str = f"spec_{lat:.5f}_{lon:.5f}_{region.id}"
        h = hashlib.sha256(seed_str.encode("utf-8")).hexdigest()
        jitter = (int(h[0:4], 16) / 65535.0 - 0.5) * 0.04

        # Endmember physical signatures:
        # Water: low across all, very low NIR
        # Vegetation: green peak, red chlorophyll absorption, high NIR plateau (red edge effect)
        # Built-up / Soil: monotonically increasing or high visible
        b02 = 0.15 * fractions.built_up + 0.08 * fractions.vegetation + 0.18 * fractions.water + 0.12 * fractions.bare_soil + 0.10 * fractions.cropland + jitter
        b03 = 0.18 * fractions.built_up + 0.22 * fractions.vegetation + 0.14 * fractions.water + 0.16 * fractions.bare_soil + 0.20 * fractions.cropland + jitter
        b04 = 0.22 * fractions.built_up + 0.09 * fractions.vegetation + 0.08 * fractions.water + 0.24 * fractions.bare_soil + 0.12 * fractions.cropland + jitter
        b08 = 0.24 * fractions.built_up + 0.65 * fractions.vegetation + 0.03 * fractions.water + 0.28 * fractions.bare_soil + 0.55 * fractions.cropland + jitter

        return SpectralBands(
            B02=round(float(max(0.01, min(0.99, b02))), 2),
            B03=round(float(max(0.01, min(0.99, b03))), 2),
            B04=round(float(max(0.01, min(0.99, b04))), 2),
            B08=round(float(max(0.01, min(0.99, b08))), 2)
        )

pixel_service = PixelService()
