# NTRO Satellite Super-Resolution Backend & Geospatial Pipeline

A modular, high-performance **FastAPI backend** and **geospatial pipeline** developed for the **NTRO Satellite Super-Resolution Challenge**.

The system ingests **Sentinel-2 L2A (10m ground sampling distance)** multi-spectral imagery and enhances it via a 4x Super-Resolution pipeline to produce high-fidelity imagery at **below 4m resolution (target ~2.5m)**, alongside sub-pixel land-cover fractions, uncertainty/entropy maps, and Cloud-Optimized GeoTIFF (COG) streaming.

---

## 1. System Overview

### Core Objectives
- **Super-Resolution Enhancement**: Scaled 4x from 10m (Sentinel-2 bands B02, B03, B04, B08) down to **2.5m** ground sampling distance.
- **Uncertainty Quantification**: Pixel-level Shannon entropy score in range $[0, 1]$ where 0 = high model confidence, 1 = high ambiguity; confidence score calculated as $1.0 - \text{entropy}$.
- **Sub-Pixel Land Cover**: Deterministic extraction of 5 land cover fractions (`built_up`, `vegetation`, `water`, `bare_soil`, `cropland`) strictly summing to $1.00$.
- **Geospatial Pipeline**: Rasterio & GDAL preserving spatial CRS (WGS84 EPSG:4326 / UTM), affine transformation matrices, dimensions, and overview pyramids for Cloud Optimized GeoTIFFs (COGs).
- **Web Map Tile Serving**: Standard Web Mercator XYZ PNG tile endpoint (`/tiles/{layer}/{z}/{x}/{y}.png`) ready for Leaflet and OpenLayers, with OGC WMTS capabilities.

---

## 2. Project Architecture

```
backend/
├── app/
│   ├── main.py                     # FastAPI application entrypoint, CORS, exception handlers
│   ├── config.py                   # Settings, demo regions configuration, paths
│   │
│   ├── routes/
│   │   ├── infer.py                # POST /infer (Triggers Super-Resolution pipeline)
│   │   ├── pixel.py                # GET /pixel (Lat/Lon inspection for fractions & spectral)
│   │   ├── export.py               # GET /export/{region} (COG / GeoTIFF export & download)
│   │   └── tiles.py                # GET /tiles/{layer}/{z}/{x}/{y}.png (Leaflet XYZ tile streaming)
│   │
│   ├── services/
│   │   ├── inference_service.py    # Pluggable Super-Resolution orchestrator (Mock -> SEN2SR/ESAOpenSR)
│   │   ├── pixel_service.py        # Coordinate lookup, 5-class fractions, spectral reflectance
│   │   ├── entropy_service.py      # Uncertainty & entropy estimation
│   │   └── geospatial_service.py   # Rasterio / GDAL GeoTIFF/COG reading, writing, indexing
│   │
│   └── models/
│       └── schemas.py              # Pydantic data schemas and API contracts
│
├── data/                           # Managed raster directory
│   ├── sentinel/                   # 10m input Sentinel-2 rasters
│   ├── sr_output/                  # 2.5m enhanced Super-Resolution COGs
│   ├── entropy/                    # Uncertainty & entropy rasters
│   └── fractions/                  # Sub-pixel land cover fraction rasters
│
├── scripts/
│   └── generate_seed_data.py       # Generates sample GeoTIFF & COG files for demo regions
│
├── tests/                          # Pytest automated test suite
│   ├── test_infer.py
│   ├── test_pixel.py
│   ├── test_export.py
│   └── test_geospatial.py
│
├── requirements.txt
└── README.md
```

---

## 3. Installation & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.14 on Windows 64-bit)
- `pip` package manager

### 1. Install Dependencies
```bash
python -m pip install -r backend/requirements.txt
```

### 2. Generate Seed GeoTIFF and COG Datasets
Before launching the server, initialize the seed GeoTIFF and Cloud-Optimized GeoTIFF rasters for the demo regions:
```bash
python backend/scripts/generate_seed_data.py
```

### 3. Run FastAPI Development Server
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 4. Interactive API Documentation (Swagger)

Once the server is running, access the interactive OpenAPI documentation:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI Schema**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 5. API Endpoints & Usage Examples

### 1. Trigger Super-Resolution Inference
**`POST /infer`**

Triggers the 4x super-resolution pipeline for a target region. Simulates 1.5–2.0s deep learning execution time to allow the frontend to validate progress bars and loading spinners.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/infer" \
     -H "Content-Type: application/json" \
     -d '{"region": "mumbai_coastal"}'
```

**Response (`200 OK`):**
```json
{
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
    "model_architecture": "SEN2SR_EDSR_RCAN_4x",
    "weights_version": "v1.0-mock",
    "bands_enhanced": ["B02_Blue", "B03_Green", "B04_Red", "B08_NIR"],
    "crs": "EPSG:4326",
    "bounds": [72.75, 18.85, 73.05, 19.30],
    "center": [19.076, 72.8777]
  }
}
```

---

### 2. Query Pixel Coordinate
**`GET /pixel?lat={lat}&lon={lon}&region={region}`**

Called when an operator or user clicks anywhere on the Leaflet map. Returns deterministic, stable sub-pixel fractions (summing to 1.00), entropy uncertainty, confidence, and Sentinel-2 multi-spectral values.

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/pixel?lat=19.0760&lon=72.8777&region=mumbai_coastal"
```

**Response (`200 OK`):**
```json
{
  "latitude": 19.076,
  "longitude": 72.8777,
  "fractions": {
    "built_up": 0.38,
    "vegetation": 0.22,
    "water": 0.12,
    "bare_soil": 0.18,
    "cropland": 0.10
  },
  "entropy": 0.24,
  "confidence": 0.76,
  "spectral": {
    "B02": 0.15,
    "B03": 0.22,
    "B04": 0.19,
    "B08": 0.54
  }
}
```

---

### 3. Download GeoTIFF / Cloud Optimized GeoTIFF (COG)
**`GET /export/{region}?layer={layer}&format={format}`**

Streams or downloads GeoTIFF or COG files with full spatial metadata (CRS `EPSG:4326`, affine transforms, resolution headers).

- **`layer` options**: `sr` (Super-Resolution), `entropy` (Uncertainty), `fractions` (Land-cover fractions)
- **`format` options**: `cog` (Cloud Optimized GeoTIFF), `geotiff` (Standard GeoTIFF)

**Download SR COG:**
```bash
curl -O -J "http://127.0.0.1:8000/export/mumbai_coastal?layer=sr&format=cog"
```

**Query Metadata Only (`metadata_only=true`):**
```bash
curl -X GET "http://127.0.0.1:8000/export/mumbai_coastal?layer=sr&format=cog&metadata_only=true"
```

---

### 4. Leaflet Map Tile Streaming
**`GET /tiles/{layer}/{z}/{x}/{y}.png`**

Directly consumable by Leaflet `L.tileLayer`:
```javascript
// In Leaflet.js frontend:
L.tileLayer('http://127.0.0.1:8000/tiles/sr/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: 'NTRO 2.5m Super-Resolution'
}).addTo(map);

// Entropy heatmap layer:
L.tileLayer('http://127.0.0.1:8000/tiles/entropy/{z}/{x}/{y}.png', {
    maxZoom: 18,
    opacity: 0.6
}).addTo(map);
```

---

### 5. List Demo Regions
**`GET /regions`**
Returns spatial bounding boxes, descriptions, and center coordinates for:
- `mumbai_coastal` (Urban coastal mega-city zone)
- `sundarbans_delta` (Tidal mangrove biosphere)
- `delhi_fringe` (Peri-urban cropland interface)

---

## 6. How Mock Inference Works & How to Replace With Real ML Model

### Current Flow
```
Client (Leaflet)
   ↓ POST /infer
InferenceRoute (routes/infer.py)
   ↓ run_super_resolution(...)
InferenceService (services/inference_service.py)
   ↓ [asyncio.sleep(1.8) simulating GPU compute]
GeospatialService (services/geospatial_service.py)
   ↓ Generates 2.5m resolution GeoTIFF / COG with Rasterio
Returns /tiles/sr/{z}/{x}/{y}.png & /export/ links
```

### Plugging in Real SEN2SR / ESAOpenSR / PyTorch Model
To switch to the real deep learning model, **no routes or frontend contracts need to change**. Simply update `backend/app/services/inference_service.py`:

```python
# In backend/app/services/inference_service.py

import torch
# Example: from sen2sr import Sen2SrModel
# Example: from esa_opensr import OpenSRModel

class InferenceService:
    def __init__(self):
        # 1. Load weights once on startup
        # self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # self.model = OpenSRModel.load_pretrained("sen2sr_edsr_4x.pt").to(self.device)
        pass

    async def run_super_resolution(
        self,
        region_id: str,
        image_id: Optional[str] = None,
        input_resolution: float = 10.0,
        target_resolution: float = 2.5
    ) -> InferenceResponse:
        region = settings.regions[region_id]
        
        # 2. Read 10m Sentinel-2 input bands (B02, B03, B04, B08) using Rasterio
        s2_input_path = settings.sentinel_dir / f"{region_id}_sentinel_cog.tif"
        input_tensor, metadata = geospatial_service.read_raster(s2_input_path)
        
        # 3. Model forward pass
        # with torch.no_grad():
        #     # input shape: [1, 4, H, W]
        #     sr_tensor = self.model(torch.from_numpy(input_tensor).float().to(self.device))
        #     sr_numpy = sr_tensor.cpu().numpy().squeeze(0)
        
        # 4. Save enhanced 2.5m output as COG
        # output_cog_path = settings.sr_output_dir / f"{region_id}_sr_2.5m.tif"
        # geospatial_service.write_geotiff(output_cog_path, sr_numpy, bounds, crs="EPSG:4326")
        # geospatial_service.write_cog(output_cog_path, output_cog_path)
        
        # 5. Return the exact same response schema
        return InferenceResponse(...)
```

---

## 7. Connecting to Copernicus Data Space Ecosystem (CDAS)

The system is configured to ingest Sentinel-2 L2A data from the **Copernicus Data Space Ecosystem (CDAS)**.

- **Copernicus Browser Reference**:
  `https://browser.dataspace.copernicus.eu/?zoom=10&lat=27.89614&lng=-15.55981&themeId=DEFAULT-THEME&datasetId=S2_L2A_CDAS`
- **Granule Bands**:
  - `B02` (Blue - 490 nm, 10m GSD)
  - `B03` (Green - 560 nm, 10m GSD)
  - `B04` (Red - 665 nm, 10m GSD)
  - `B08` (NIR - 842 nm, 10m GSD)
- In production, granules can be pulled directly using the Copernicus OpenSearch or STAC API:
  `https://catalogue.dataspace.copernicus.eu/stac/search`

---

## 8. Running Automated Tests

Run the complete test suite verifying all endpoints, validations, fraction summation, entropy ranges, and geospatial conversions:

```bash
python -m pytest backend/tests -v
```

**Test Coverage Summary:**
- `test_infer.py`: Verifies `/infer` response schema, scale factor (4x), 10m to 2.5m resolution, simulated execution time, and region error validation.
- `test_pixel.py`: Verifies exact coordinate queries, deterministic reproducibility, land-cover fraction summation to 1.00, entropy in $[0, 1]$, confidence $= 1.0 - \text{entropy}$, and boundary checks.
- `test_export.py`: Verifies binary COG/GeoTIFF downloads, Content-Disposition headers, metadata query mode, and Leaflet tile streaming.
- `test_geospatial.py`: Verifies Rasterio read/write, COG generation, affine coordinate conversion (lat/lon to pixel), and CRS preservation.
