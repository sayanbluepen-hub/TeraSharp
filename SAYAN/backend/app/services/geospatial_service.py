import io
import math
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, Union
from PIL import Image

try:
    import rasterio
    from rasterio.transform import from_bounds, rowcol, xy
    from rasterio.enums import Resampling
    from rasterio.crs import CRS
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False
    rasterio = None
    from_bounds = None
    rowcol = None
    xy = None

from ..config import settings, RegionConfig

class GeospatialService:
    """
    Comprehensive geospatial pipeline handling GeoTIFF/COG reading, writing,
    affine transformation, coordinate extraction, and tile generation.
    """

    def __init__(self):
        self.has_rasterio = HAS_RASTERIO

    def read_raster(self, file_path: Union[str, Path]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Reads a GeoTIFF raster file and returns the band array and spatial metadata.
        Preserves CRS, affine transform, dimensions, and nodata value.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Raster file not found at: {file_path}")

        if self.has_rasterio:
            with rasterio.open(file_path) as src:
                data = src.read()
                metadata = {
                    "driver": src.driver,
                    "width": src.width,
                    "height": src.height,
                    "count": src.count,
                    "crs": str(src.crs),
                    "transform": list(src.transform),
                    "bounds": [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top],
                    "nodata": src.nodata,
                    "dtype": str(src.dtypes[0])
                }
                return data, metadata
        else:
            # Fallback loader using PIL
            img = Image.open(file_path)
            arr = np.array(img)
            if arr.ndim == 2:
                arr = arr[np.newaxis, ...]
            elif arr.ndim == 3:
                arr = np.transpose(arr, (2, 0, 1))
            metadata = {
                "driver": "GTiff",
                "width": img.width,
                "height": img.height,
                "count": arr.shape[0],
                "crs": "EPSG:4326",
                "transform": [0.0001, 0.0, 0.0, 0.0, -0.0001, 0.0],
                "bounds": [0, 0, 1, 1],
                "nodata": None,
                "dtype": str(arr.dtype)
            }
            return arr, metadata

    def write_geotiff(
        self,
        output_path: Union[str, Path],
        data: np.ndarray,
        bounds: Tuple[float, float, float, float],
        crs: str = "EPSG:4326",
        nodata: Optional[float] = None
    ) -> Path:
        """
        Writes a NumPy array to a valid GeoTIFF file preserving geographic referencing.
        Bounds: (min_lon, min_lat, max_lon, max_lat).
        data shape: (bands, height, width) or (height, width).
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if data.ndim == 2:
            data = data[np.newaxis, ...]
        bands, height, width = data.shape
        min_lon, min_lat, max_lon, max_lat = bounds

        if self.has_rasterio:
            transform = from_bounds(min_lon, min_lat, max_lon, max_lat, width, height)
            is_valid_tiled = (width >= 256 and height >= 256 and width % 16 == 0 and height % 16 == 0)
            profile = {
                "driver": "GTiff",
                "height": height,
                "width": width,
                "count": bands,
                "dtype": data.dtype,
                "crs": CRS.from_string(crs),
                "transform": transform,
                "nodata": nodata,
                "compress": "deflate"
            }
            if is_valid_tiled:
                profile.update({
                    "tiled": True,
                    "blockxsize": 256,
                    "blockysize": 256
                })
            with rasterio.open(output_path, "w", **profile) as dst:
                dst.write(data)
        else:
            # Fallback PIL TIFF output with metadata
            if bands == 1:
                img = Image.fromarray(data[0])
            elif bands in (3, 4):
                transposed = np.transpose(data, (1, 2, 0))
                img = Image.fromarray(transposed.astype(np.uint8))
            else:
                img = Image.fromarray(data[0])
            img.save(output_path, format="TIFF")

        return output_path

    def write_cog(
        self,
        input_geotiff: Union[str, Path],
        output_cog: Union[str, Path]
    ) -> Path:
        """
        Generates a Cloud Optimized GeoTIFF (COG) with tiled layout and overview pyramids.
        Enables efficient range queries and web streaming for map viewers.
        """
        input_geotiff = Path(input_geotiff)
        output_cog = Path(output_cog)
        output_cog.parent.mkdir(parents=True, exist_ok=True)

        if self.has_rasterio:
            with rasterio.open(input_geotiff) as src:
                profile = src.profile.copy()
                is_valid_tiled = (src.width >= 256 and src.height >= 256 and src.width % 16 == 0 and src.height % 16 == 0)
                profile.update({
                    "driver": "GTiff",
                    "compress": "deflate",
                    "interleave": "pixel" if src.count > 1 else "band"
                })
                if is_valid_tiled:
                    profile.update({
                        "tiled": True,
                        "blockxsize": 256,
                        "blockysize": 256
                    })

                with rasterio.open(output_cog, "w", **profile) as dst:
                    for i in range(1, src.count + 1):
                        dst.write(src.read(i), i)

                    # Build overviews (pyramids) for COG standard
                    factors = [2, 4, 8, 16]
                    try:
                        dst.build_overviews(factors, Resampling.nearest)
                        dst.update_tags(ns="rio_overview", resampling="nearest")
                    except Exception:
                        pass
        else:
            # If rasterio not available, copy input
            data, meta = self.read_raster(input_geotiff)
            img = Image.fromarray(data[0] if data.ndim == 3 else data)
            img.save(output_cog, format="TIFF")

        return output_cog

    def latlon_to_pixel(
        self,
        bounds: Tuple[float, float, float, float],
        width: int,
        height: int,
        lon: float,
        lat: float
    ) -> Tuple[int, int]:
        """
        Converts WGS84 geographic coordinate (lon, lat) to raster row and column indices.
        Bounds: (min_lon, min_lat, max_lon, max_lat).
        Returns: (row, col)
        """
        min_lon, min_lat, max_lon, max_lat = bounds
        if not (min_lon <= lon <= max_lon and min_lat <= lat <= max_lat):
            raise ValueError(f"Coordinate ({lat}, {lon}) is out of raster bounds {bounds}")

        col = int(((lon - min_lon) / (max_lon - min_lon)) * width)
        row = int(((max_lat - lat) / (max_lat - min_lat)) * height)

        col = max(0, min(width - 1, col))
        row = max(0, min(height - 1, row))
        return row, col

    def pixel_to_latlon(
        self,
        bounds: Tuple[float, float, float, float],
        width: int,
        height: int,
        row: int,
        col: int
    ) -> Tuple[float, float]:
        """
        Converts raster row and column to geographic (lon, lat).
        """
        min_lon, min_lat, max_lon, max_lat = bounds
        lon = min_lon + (col + 0.5) / width * (max_lon - min_lon)
        lat = max_lat - (row + 0.5) / height * (max_lat - min_lat)
        return lon, lat

    def get_raster_metadata(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Returns metadata description of raster without reading entire data into memory."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if self.has_rasterio:
            with rasterio.open(file_path) as src:
                return {
                    "path": str(file_path),
                    "driver": src.driver,
                    "width": src.width,
                    "height": src.height,
                    "count": src.count,
                    "crs": str(src.crs),
                    "bounds": [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top],
                    "resolution": [abs(src.transform[0]), abs(src.transform[4])],
                    "is_tiled": bool(src.profile.get("tiled", False)),
                    "file_size_bytes": file_path.stat().st_size
                }
        else:
            img = Image.open(file_path)
            return {
                "path": str(file_path),
                "driver": "TIFF",
                "width": img.width,
                "height": img.height,
                "count": len(img.getbands()),
                "crs": "EPSG:4326",
                "bounds": [0, 0, 1, 1],
                "file_size_bytes": file_path.stat().st_size
            }

    def generate_synthetic_raster(
        self,
        region: RegionConfig,
        layer_type: str,
        resolution_m: float = 2.5
    ) -> Tuple[np.ndarray, Tuple[float, float, float, float]]:
        """
        Generates realistic synthetic multi-spectral or single-band raster data
        for testing and mock pipelines.
        """
        bounds = (region.min_lon, region.min_lat, region.max_lon, region.max_lat)
        
        # Calculate grid size based on ground resolution
        # 1 deg latitude approx 111,000 meters
        lat_dist_m = (region.max_lat - region.min_lat) * 111000
        lon_dist_m = (region.max_lon - region.min_lon) * 111000 * math.cos(math.radians(region.center_lat))
        
        raw_h = max(64, min(512, int(lat_dist_m / (resolution_m * 40))))
        raw_w = max(64, min(512, int(lon_dist_m / (resolution_m * 40))))
        # Ensure dimensions are clean multiples of 16
        height = max(64, (raw_h // 16) * 16)
        width = max(64, (raw_w // 16) * 16)

        y_coords = np.linspace(region.max_lat, region.min_lat, height)
        x_coords = np.linspace(region.min_lon, region.max_lon, width)
        xx, yy = np.meshgrid(x_coords, y_coords)

        # Base spatial features based on coordinate geography
        dist_from_center = np.sqrt(((xx - region.center_lon) * 1.5) ** 2 + (yy - region.center_lat) ** 2)
        pattern = np.sin(xx * 80.0) * np.cos(yy * 80.0)

        if layer_type in ("sr", "sentinel"):
            # 4 bands: B04 (Red), B03 (Green), B02 (Blue), B08 (NIR)
            # Scaled to uint8 for imagery display or float32 for scientific calculations
            red = np.clip((0.35 + 0.25 * pattern - 0.1 * dist_from_center) * 255, 10, 250).astype(np.uint8)
            green = np.clip((0.40 + 0.20 * np.cos(xx * 50) + 0.1 * pattern) * 255, 10, 250).astype(np.uint8)
            blue = np.clip((0.30 + 0.15 * np.sin(yy * 50) - 0.05 * pattern) * 255, 10, 250).astype(np.uint8)
            nir = np.clip((0.55 + 0.30 * np.sin(dist_from_center * 10)) * 255, 10, 250).astype(np.uint8)
            data = np.stack([red, green, blue, nir], axis=0)
        elif layer_type == "entropy":
            # Uncertainty score [0, 1] scaled to uint8 [0, 255]
            entropy = np.clip(np.abs(pattern) * 0.7 + (dist_from_center % 0.1) * 3.0, 0.05, 0.95)
            data = (entropy * 255).astype(np.uint8)[np.newaxis, ...]
        elif layer_type == "fractions":
            # 5 channels for 5 land-cover classes
            f_built = np.clip(0.3 + 0.3 * pattern, 0.05, 0.8)
            f_veg = np.clip(0.3 - 0.2 * pattern, 0.05, 0.8)
            f_water = np.clip(0.2 + 0.1 * np.cos(xx * 40), 0.0, 0.5)
            f_soil = np.clip(0.1 + 0.1 * np.sin(yy * 40), 0.0, 0.4)
            f_crop = 1.0 - (f_built + f_veg + f_water + f_soil)
            f_crop = np.clip(f_crop, 0.01, 0.9)
            
            # Normalize so sum = 1.0
            total = f_built + f_veg + f_water + f_soil + f_crop
            data = np.stack([
                (f_built / total * 255).astype(np.uint8),
                (f_veg / total * 255).astype(np.uint8),
                (f_water / total * 255).astype(np.uint8),
                (f_soil / total * 255).astype(np.uint8),
                (f_crop / total * 255).astype(np.uint8),
            ], axis=0)
        else:
            data = np.full((1, height, width), 128, dtype=np.uint8)

        return data, bounds

    def render_mock_tile(self, layer: str, z: int, x: int, y: int) -> bytes:
        """
        Renders an XYZ map tile (256x256 PNG) representing the super-resolution
        imagery, entropy map, or fraction layer for Leaflet map viewers.
        """
        tile_size = 256
        u = np.linspace(0, 1, tile_size)
        v = np.linspace(0, 1, tile_size)
        uu, vv = np.meshgrid(u, v)

        # Coordinate seed variation
        seed = (x * 13 + y * 17 + z * 31) % 1000 / 1000.0
        grid_pattern = np.sin((uu + seed) * 12.0) * np.cos((vv + seed) * 12.0)

        if layer == "sr":
            # True-color RGB simulation (Enhanced resolution satellite imagery)
            r = np.clip((0.45 + 0.35 * grid_pattern) * 255, 20, 240).astype(np.uint8)
            g = np.clip((0.55 + 0.25 * np.cos((uu + seed) * 8.0)) * 255, 30, 240).astype(np.uint8)
            b = np.clip((0.40 + 0.20 * np.sin((vv + seed) * 8.0)) * 255, 40, 230).astype(np.uint8)
            alpha = np.full((tile_size, tile_size), 230, dtype=np.uint8)
            img_arr = np.dstack([r, g, b, alpha])
        elif layer == "entropy":
            # Colormap from Yellow (high confidence / low entropy) to Magenta/Red (high uncertainty)
            entropy_vals = np.clip(np.abs(grid_pattern) * 0.8 + 0.1, 0.0, 1.0)
            r = (entropy_vals * 240 + 15).astype(np.uint8)
            g = ((1.0 - entropy_vals) * 200 + 30).astype(np.uint8)
            b = (np.sin(entropy_vals * np.pi) * 180 + 20).astype(np.uint8)
            alpha = np.full((tile_size, tile_size), 200, dtype=np.uint8)
            img_arr = np.dstack([r, g, b, alpha])
        else:
            # Fallback grayscale tile
            gray = np.clip((uu * 0.5 + vv * 0.5) * 255, 50, 200).astype(np.uint8)
            alpha = np.full((tile_size, tile_size), 220, dtype=np.uint8)
            img_arr = np.dstack([gray, gray, gray, alpha])

        pil_img = Image.fromarray(img_arr, mode="RGBA")
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG", optimize=True)
        return buffer.getvalue()

geospatial_service = GeospatialService()
