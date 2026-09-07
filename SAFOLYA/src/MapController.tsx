import { useEffect } from "react";
import { useMap, useMapEvents } from "react-leaflet";

interface MapControllerProps {
  onMouseMove: (lat: number, lng: number) => void;
  onZoomChange: (zoom: number) => void;
}

/**
 * Headless controller component that lives inside <MapContainer>.
 * Exposes mouse-position and zoom-level via callbacks.
 */
export default function MapController({ onMouseMove, onZoomChange }: MapControllerProps) {
  const map = useMap();

  useEffect(() => {
    onZoomChange(map.getZoom());
  }, [map, onZoomChange]);

  useMapEvents({
    mousemove(e) {
      onMouseMove(e.latlng.lat, e.latlng.lng);
    },
    zoomend() {
      onZoomChange(map.getZoom());
    },
  });

  return null;
}
