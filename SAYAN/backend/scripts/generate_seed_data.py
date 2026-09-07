"""Script to generate realistic seed GeoTIFF / COG data for demo regions."""
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app.config import settings
from backend.app.services.geospatial_service import geospatial_service

def generate_all_seeds():
    settings.ensure_directories()
    print("Generating seed GeoTIFF and COG datasets for demo regions...")

    layers = [
        ("sr", settings.sr_output_dir, settings.target_resolution_m),
        ("entropy", settings.entropy_dir, settings.target_resolution_m),
        ("fractions", settings.fractions_dir, settings.target_resolution_m),
        ("sentinel", settings.sentinel_dir, settings.input_resolution_m),
    ]

    for region_id, reg in settings.regions.items():
        print(f"\nProcessing region: {region_id} ({reg.name})")
        for layer_name, target_dir, res in layers:
            data, bounds = geospatial_service.generate_synthetic_raster(reg, layer_name, res)
            
            # Write standard GeoTIFF
            tif_path = target_dir / f"{region_id}_{layer_name}_geotiff.tif"
            geospatial_service.write_geotiff(tif_path, data, bounds)
            
            # Write COG
            cog_path = target_dir / f"{region_id}_{layer_name}_cog.tif"
            geospatial_service.write_cog(tif_path, cog_path)
            
            print(f"  [+] Generated {layer_name}: {cog_path.name} (size: {cog_path.stat().st_size} bytes)")

    print("\nSeed data generation complete!")

if __name__ == "__main__":
    generate_all_seeds()
