from fastapi import APIRouter, HTTPException, Path as FPath, Response, status
from typing import List
from ..config import settings
from ..models.schemas import RegionInfo
from ..services.geospatial_service import geospatial_service

router = APIRouter(prefix="", tags=["Map Tiles & Regions"])

@router.get(
    "/regions",
    response_model=List[RegionInfo],
    summary="List Supported Regions",
    description="Returns configuration, bounding boxes, and center coordinates for all supported demo regions."
)
def list_regions() -> List[RegionInfo]:
    return [
        RegionInfo(
            id=r.id,
            name=r.name,
            description=r.description,
            center=[r.center_lat, r.center_lon],
            bounds=[r.min_lon, r.min_lat, r.max_lon, r.max_lat],
            default_zoom=r.default_zoom
        )
        for r in settings.regions.values()
    ]

@router.get(
    "/tiles/{layer}/{z}/{x}/{y}.png",
    summary="Serve XYZ Map Tiles",
    description=(
        "Standard Web Mercator XYZ map tile service (compatible with Leaflet, OpenLayers, MapLibre, Cesium). "
        "Streams 256x256 PNG tiles for Super-Resolution enhanced imagery ('sr') or "
        "uncertainty/entropy heatmaps ('entropy')."
    ),
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "256x256 PNG map tile"
        },
        400: {"description": "Invalid tile layer requested"}
    }
)
def get_tile(
    layer: str = FPath(..., description="Layer type: 'sr' or 'entropy'"),
    z: int = FPath(..., description="Zoom level (0 - 20)", ge=0, le=22),
    x: int = FPath(..., description="Tile column index", ge=0),
    y: int = FPath(..., description="Tile row index", ge=0)
):
    if layer not in ("sr", "entropy", "fractions"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown tile layer '{layer}'. Available: 'sr', 'entropy', 'fractions'."
        )

    tile_bytes = geospatial_service.render_mock_tile(layer=layer, z=z, x=x, y=y)
    return Response(
        content=tile_bytes,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "X-Tile-Layer": layer,
            "X-Tile-Coord": f"{z}/{x}/{y}"
        }
    )

@router.get(
    "/tiles/capabilities.xml",
    summary="WMTS GetCapabilities XML",
    description="Returns standard OGC WMTS (Web Map Tile Service) XML capabilities declaration for GIS client interoperability (e.g. QGIS, ArcGIS)."
)
def wmts_capabilities():
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Capabilities xmlns="http://www.opengis.net/wmts/1.0" version="1.0.0">
  <ServiceIdentification>
    <Title>{settings.app_name}</Title>
    <Abstract>{settings.app_description}</Abstract>
    <ServiceType>OGC WMTS</ServiceType>
    <ServiceTypeVersion>1.0.0</ServiceTypeVersion>
  </ServiceIdentification>
  <Contents>
    <Layer>
      <Title>Super-Resolution Imagery (2.5m)</Title>
      <Identifier>sr</Identifier>
      <ResourceURL format="image/png" resourceType="tile" template="/tiles/sr/{{TileMatrix}}/{{TileCol}}/{{TileRow}}.png"/>
    </Layer>
    <Layer>
      <Title>Uncertainty Entropy Map</Title>
      <Identifier>entropy</Identifier>
      <ResourceURL format="image/png" resourceType="tile" template="/tiles/entropy/{{TileMatrix}}/{{TileCol}}/{{TileRow}}.png"/>
    </Layer>
  </Contents>
</Capabilities>"""
    return Response(content=xml_content, media_type="application/xml")
