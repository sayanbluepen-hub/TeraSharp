from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from .config import settings
from .routes.infer import router as infer_router
from .routes.pixel import router as pixel_router
from .routes.export import router as export_router
from .routes.tiles import router as tiles_router
from .services.geospatial_service import geospatial_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context: initialize directories and sample seed rasters."""
    settings.ensure_directories()
    # Pre-generate sample GeoTIFF/COG files for demo regions
    for region_id, reg in settings.regions.items():
        sample_path = settings.sr_output_dir / f"{region_id}_sr_cog.tif"
        if not sample_path.exists():
            data, bounds = geospatial_service.generate_synthetic_raster(reg, "sr", 2.5)
            geospatial_service.write_geotiff(sample_path, data, bounds)
    yield

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Enable CORS for frontend applications (Leaflet / React / Vue / Vanilla JS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom error handler for validation errors (e.g. malformed lat/lon)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_msg = errors[0]["msg"] if errors else "Validation failed"
    field_loc = " -> ".join([str(loc) for loc in errors[0]["loc"]]) if errors else "body"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "code": "VALIDATION_ERROR",
            "detail": f"Field '{field_loc}': {error_msg}",
            "raw_errors": [
                {"loc": err["loc"], "msg": err["msg"], "type": err["type"]}
                for err in errors
            ]
        }
    )

# Register Sub-Routers
app.include_router(infer_router)
app.include_router(pixel_router)
app.include_router(export_router)
app.include_router(tiles_router)

@app.get(
    "/",
    tags=["System Health"],
    summary="System Health & API Information",
    description="Returns service status, target resolution specs, and available endpoints."
)
def root():
    return {
        "status": "online",
        "service": settings.app_name,
        "version": settings.app_version,
        "input_resolution": f"{settings.input_resolution_m}m (Sentinel-2 L2A)",
        "target_resolution": f"{settings.target_resolution_m}m (<4m target)",
        "scale_factor": f"{settings.scale_factor}x",
        "docs_url": "/docs",
        "supported_regions": list(settings.regions.keys()),
        "endpoints": {
            "infer": "POST /infer",
            "pixel": "GET /pixel?lat={lat}&lon={lon}&region={region}",
            "export": "GET /export/{region}?layer={layer}&format={format}",
            "tiles": "GET /tiles/{layer}/{z}/{x}/{y}.png",
            "regions": "GET /regions"
        }
    }

@app.get("/health", tags=["System Health"], summary="Health Check Probe")
def health_check():
    return {"status": "healthy", "service": settings.app_name}
