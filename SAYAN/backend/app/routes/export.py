from pathlib import Path
from fastapi import APIRouter, HTTPException, Query, Path as FPath, status
from fastapi.responses import FileResponse, JSONResponse
from ..config import settings
from ..models.schemas import ErrorDetail, ExportResponse
from ..services.geospatial_service import geospatial_service

router = APIRouter(prefix="", tags=["Export & Download"])

@router.get(
    "/export/{region}",
    summary="Download Super-Resolution Products as COG or GeoTIFF",
    description=(
        "Exports processed rasters in Cloud Optimized GeoTIFF (COG) or standard GeoTIFF format. "
        "Supports Super-Resolution imagery ('sr'), Uncertainty/Entropy maps ('entropy'), and "
        "Sub-pixel Land Cover Fraction maps ('fractions'). Preserves spatial CRS (EPSG:4326), affine transforms, and tiling."
    ),
    responses={
        200: {"description": "GeoTIFF / COG binary stream or metadata JSON"},
        400: {"description": "Invalid region or unsupported layer/format requested", "model": ErrorDetail},
        404: {"description": "File not found", "model": ErrorDetail}
    }
)
async def export_product(
    region: str = FPath(..., description="Region identifier (e.g. mumbai_coastal, sundarbans_delta, delhi_fringe)"),
    layer: str = Query(default="sr", description="Layer to export: 'sr', 'entropy', or 'fractions'"),
    format: str = Query(default="cog", description="Target geospatial format: 'cog' or 'geotiff'"),
    metadata_only: bool = Query(default=False, description="If true, returns file metadata instead of binary download")
):
    if region not in settings.regions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid region requested",
                "code": "INVALID_REGION",
                "detail": f"Region '{region}' is not available.",
                "allowed_values": list(settings.regions.keys())
            }
        )

    valid_layers = ["sr", "entropy", "fractions"]
    if layer not in valid_layers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid layer type",
                "code": "INVALID_LAYER",
                "detail": f"Layer '{layer}' is not supported.",
                "allowed_values": valid_layers
            }
        )

    valid_formats = ["cog", "geotiff", "tif"]
    if format not in valid_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid format requested",
                "code": "INVALID_FORMAT",
                "detail": f"Format '{format}' is not supported. Use 'cog' or 'geotiff'.",
                "allowed_values": ["cog", "geotiff"]
            }
        )

    reg_config = settings.regions[region]
    target_dir = {
        "sr": settings.sr_output_dir,
        "entropy": settings.entropy_dir,
        "fractions": settings.fractions_dir
    }[layer]

    file_name = f"{region}_{layer}_{format}.tif"
    file_path = target_dir / file_name

    # Auto-generate sample GeoTIFF/COG file if not currently present on disk
    if not file_path.exists():
        data, bounds = geospatial_service.generate_synthetic_raster(
            region=reg_config,
            layer_type=layer,
            resolution_m=settings.target_resolution_m if layer == "sr" else 10.0
        )
        geospatial_service.write_geotiff(output_path=file_path, data=data, bounds=bounds)

    if metadata_only:
        meta = geospatial_service.get_raster_metadata(file_path)
        return {
            "region": region,
            "layer": layer,
            "format": format,
            "file_name": file_name,
            "file_size_bytes": meta["file_size_bytes"],
            "crs": meta.get("crs", "EPSG:4326"),
            "resolution_m": settings.target_resolution_m if layer == "sr" else 10.0,
            "bounds": [reg_config.min_lon, reg_config.min_lat, reg_config.max_lon, reg_config.max_lat],
            "download_url": f"/export/{region}?layer={layer}&format={format}"
        }

    return FileResponse(
        path=file_path,
        media_type="image/tiff",
        filename=file_name,
        headers={
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "X-Geospatial-CRS": "EPSG:4326",
            "X-Geospatial-Resolution": f"{settings.target_resolution_m}m"
        }
    )
