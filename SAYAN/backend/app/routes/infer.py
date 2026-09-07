from fastapi import APIRouter, HTTPException, status
from ..models.schemas import InferenceRequest, InferenceResponse, ErrorDetail
from ..config import settings
from ..services.inference_service import inference_service

router = APIRouter(prefix="", tags=["Super-Resolution Inference"])

@router.post(
    "/infer",
    response_model=InferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger Satellite Super-Resolution Inference Pipeline",
    description=(
        "Triggers the Super-Resolution enhancement pipeline for a Sentinel-2 region. "
        "Enhances 10m spatial resolution to 2.5m (<4m target requirement), computing "
        "pixel-level uncertainty and generating Cloud Optimized GeoTIFF and XYZ tile streaming endpoints."
    ),
    responses={
        200: {"description": "Super-Resolution enhancement completed successfully", "model": InferenceResponse},
        400: {"description": "Invalid region or parameters provided", "model": ErrorDetail},
        500: {"description": "Inference pipeline failure", "model": ErrorDetail}
    }
)
async def infer(request: InferenceRequest) -> InferenceResponse:
    if request.region not in settings.regions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid region requested",
                "code": "INVALID_REGION",
                "detail": f"Region '{request.region}' is not configured.",
                "allowed_values": list(settings.regions.keys())
            }
        )

    try:
        response = await inference_service.run_super_resolution(
            region_id=request.region,
            image_id=request.image_id,
            input_resolution=request.input_resolution or settings.input_resolution_m,
            target_resolution=request.target_resolution or settings.target_resolution_m
        )
        return response
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Region error", "code": "INVALID_REGION", "detail": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Inference failed", "code": "INFERENCE_ERROR", "detail": str(e)}
        )
