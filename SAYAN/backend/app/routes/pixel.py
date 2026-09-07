from fastapi import APIRouter, Query, HTTPException, status
from ..models.schemas import PixelResponse, ErrorDetail
from ..config import settings
from ..services.pixel_service import pixel_service

router = APIRouter(prefix="", tags=["Pixel Inspection"])

@router.get(
    "/pixel",
    response_model=PixelResponse,
    status_code=status.HTTP_200_OK,
    summary="Query Pixel-Level Geospatial & Radiometric Data",
    description=(
        "Returns sub-pixel land cover fractions, uncertainty entropy, model confidence, "
        "and Sentinel-2 multi-spectral reflectance values (B02, B03, B04, B08) for an exact "
        "geographic coordinate clicked on a Leaflet map."
    ),
    responses={
        200: {"description": "Pixel analysis retrieved successfully", "model": PixelResponse},
        400: {"description": "Coordinates out of bounds or invalid region", "model": ErrorDetail},
        422: {"description": "Malformed coordinate parameters", "model": ErrorDetail}
    }
)
def get_pixel(
    lat: float = Query(..., description="Latitude in WGS84 decimal degrees", ge=-90.0, le=90.0),
    lon: float = Query(..., description="Longitude in WGS84 decimal degrees", ge=-180.0, le=180.0),
    region: str = Query(default="mumbai_coastal", description="Region identifier (e.g. mumbai_coastal, sundarbans_delta, delhi_fringe)")
) -> PixelResponse:
    if region not in settings.regions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid region requested",
                "code": "INVALID_REGION",
                "detail": f"Region '{region}' is not recognized.",
                "allowed_values": list(settings.regions.keys())
            }
        )

    try:
        return pixel_service.query_pixel(lat=lat, lon=lon, region_id=region)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Coordinate validation error",
                "code": "OUT_OF_BOUNDS",
                "detail": str(e)
            }
        )
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Region error",
                "code": "INVALID_REGION",
                "detail": str(e)
            }
        )
