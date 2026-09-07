import { useState, useCallback } from "react";
import { MapContainer, TileLayer } from "react-leaflet";
import {
  Activity,
  Radio,
  Layers,
  Crosshair,
  Satellite,
  MapPin,
  Signal,
  Shield,
  ChevronLeft,
  ChevronRight,
  Eye,
  EyeOff,
  Clock,
  Cpu,
  Database,
  Wifi,
} from "lucide-react";
import MapController from "./MapController";

/* ── Constants ─────────────────────────────────────────────── */
const MUMBAI_CENTER: [number, number] = [19.076, 72.8777];
const DEFAULT_ZOOM = 11;
const DARK_TILE_URL =
  "https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png";
const TILE_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://stadiamaps.com/">Stadia</a>';

/* ── Helpers ───────────────────────────────────────────────── */
function formatCoord(val: number, pos: string, neg: string): string {
  const dir = val >= 0 ? pos : neg;
  const abs = Math.abs(val);
  const deg = Math.floor(abs);
  const min = Math.floor((abs - deg) * 60);
  const sec = ((abs - deg - min / 60) * 3600).toFixed(2);
  return `${deg}°${min}'${sec}"${dir}`;
}

function getTimestamp(): string {
  const now = new Date();
  return now.toLocaleTimeString("en-GB", { hour12: false }) + "." + String(now.getMilliseconds()).padStart(3, "0");
}

/* ── Layer Config ──────────────────────────────────────────── */
interface LayerItem {
  id: string;
  label: string;
  icon: typeof Layers;
  color: string;
  active: boolean;
}

const INITIAL_LAYERS: LayerItem[] = [
  { id: "terrain", label: "TERRAIN", icon: Layers, color: "text-emerald-400", active: true },
  { id: "satellite", label: "SAT IMAGERY", icon: Satellite, color: "text-sky-400", active: false },
  { id: "markers", label: "MARKERS", icon: MapPin, color: "text-amber-400", active: true },
  { id: "signals", label: "RF SIGNALS", icon: Signal, color: "text-rose-400", active: false },
  { id: "perimeter", label: "PERIMETER", icon: Shield, color: "text-violet-400", active: false },
];

/* ── Component ─────────────────────────────────────────────── */
export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mousePos, setMousePos] = useState<{ lat: number; lng: number }>({ lat: 19.076, lng: 72.8777 });
  const [zoom, setZoom] = useState(DEFAULT_ZOOM);
  const [layers, setLayers] = useState(INITIAL_LAYERS);
  const [timestamp, setTimestamp] = useState(getTimestamp());

  /* Update timestamp every second */
  useState(() => {
    const interval = setInterval(() => setTimestamp(getTimestamp()), 1000);
    return () => clearInterval(interval);
  });

  const handleMouseMove = useCallback((lat: number, lng: number) => {
    setMousePos({ lat, lng });
  }, []);

  const handleZoomChange = useCallback((z: number) => {
    setZoom(z);
  }, []);

  const toggleLayer = (id: string) => {
    setLayers((prev) =>
      prev.map((l) => (l.id === id ? { ...l, active: !l.active } : l))
    );
  };

  const activeCount = layers.filter((l) => l.active).length;

  return (
    <div className="flex h-screen w-screen flex-col bg-zinc-950 font-sans text-zinc-100 select-none">

      {/* ═══════════════════════════════════════════════════════
          TOP NAV — 48px
          ═══════════════════════════════════════════════════════ */}
      <nav className="relative z-50 flex h-12 min-h-12 w-full items-center justify-between border-b border-zinc-800/80 bg-zinc-950 px-4">

        {/* Left Cluster */}
        <div className="flex items-center gap-3">
          {/* Engine Status */}
          <div className="flex items-center gap-2">
            <div className="pulse-indicator h-1.5 w-1.5 rounded-full bg-emerald-400" />
            <span className="font-mono text-[11px] font-medium uppercase tracking-wider text-emerald-400">
              Engine: Ready
            </span>
          </div>

          <div className="h-3 w-px bg-zinc-800" />

          {/* CPU indicator */}
          <div className="flex items-center gap-1.5">
            <Cpu className="h-3 w-3 text-zinc-600" />
            <div className="flex items-end gap-px h-3">
              {[...Array(6)].map((_, i) => (
                <div
                  key={i}
                  className="bar-anim w-[2px] bg-emerald-500/60 rounded-none"
                  style={{ height: "100%" }}
                />
              ))}
            </div>
          </div>

          <div className="h-3 w-px bg-zinc-800" />

          {/* Uplink */}
          <div className="flex items-center gap-1.5">
            <Wifi className="h-3 w-3 text-emerald-500/60 data-tick" />
            <span className="font-mono text-[10px] text-zinc-600">UPLINK</span>
          </div>
        </div>

        {/* Center: Title */}
        <div className="absolute left-1/2 -translate-x-1/2 flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Radio className="h-3.5 w-3.5 text-emerald-500/50" />
            <h1 className="text-[13px] font-semibold uppercase tracking-[0.25em] text-zinc-200">
              Terrasharp
              <span className="text-zinc-600 mx-1">//</span>
              <span className="text-zinc-400">SRM</span>
            </h1>
          </div>
        </div>

        {/* Right Cluster */}
        <div className="flex items-center gap-3">
          {/* Clock */}
          <div className="flex items-center gap-1.5">
            <Clock className="h-3 w-3 text-zinc-600" />
            <span className="font-mono text-[10px] tabular-nums text-zinc-500">
              {timestamp}
            </span>
          </div>

          <div className="h-3 w-px bg-zinc-800" />

          {/* Database */}
          <div className="flex items-center gap-1.5">
            <Database className="h-3 w-3 text-zinc-600" />
            <span className="font-mono text-[10px] text-zinc-600">OK</span>
          </div>

          <div className="h-3 w-px bg-zinc-800" />

          {/* UTM Zone */}
          <div className="flex items-center gap-2">
            <span className="font-mono text-[10px] uppercase tracking-wider text-zinc-600">
              UTM
            </span>
            <span className="rounded-none border border-zinc-800 bg-zinc-900/80 px-2 py-0.5 font-mono text-[11px] font-medium text-emerald-400/80">
              43N
            </span>
          </div>
        </div>
      </nav>

      {/* ═══════════════════════════════════════════════════════
          MAIN CONTENT — Sidebar + Map + StatusBar
          ═══════════════════════════════════════════════════════ */}
      <div className="flex flex-1 overflow-hidden">

        {/* ── Left Sidebar ─────────────────────────────────── */}
        <aside
          className={`sidebar-enter flex flex-col border-r border-zinc-800/80 bg-zinc-950 ${
            sidebarOpen ? "w-56" : "w-10"
          } min-h-0 overflow-hidden`}
        >
          {/* Sidebar Header */}
          <div className="flex h-8 min-h-8 items-center justify-between border-b border-zinc-800/60 px-2">
            {sidebarOpen && (
              <span className="font-mono text-[9px] font-medium uppercase tracking-widest text-zinc-600">
                Layers · {activeCount}/{layers.length}
              </span>
            )}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="flex h-6 w-6 items-center justify-center rounded-none text-zinc-600 hover:text-zinc-300 hover:bg-zinc-800/50 transition-colors"
            >
              {sidebarOpen ? <ChevronLeft className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
            </button>
          </div>

          {/* Layer List */}
          {sidebarOpen && (
            <div className="flex flex-col gap-px p-1.5 overflow-y-auto flex-1">
              {layers.map((layer) => {
                const Icon = layer.icon;
                return (
                  <button
                    key={layer.id}
                    onClick={() => toggleLayer(layer.id)}
                    className={`sidebar-item flex items-center gap-2.5 rounded-none border px-2.5 py-2 text-left transition-all ${
                      layer.active
                        ? "border-zinc-800 bg-zinc-900/60"
                        : "border-transparent bg-transparent"
                    }`}
                  >
                    <Icon
                      className={`h-3.5 w-3.5 ${
                        layer.active ? layer.color : "text-zinc-700"
                      } transition-colors`}
                    />
                    <span
                      className={`font-mono text-[10px] uppercase tracking-wider ${
                        layer.active ? "text-zinc-300" : "text-zinc-600"
                      } transition-colors`}
                    >
                      {layer.label}
                    </span>
                    <span className="ml-auto">
                      {layer.active ? (
                        <Eye className="h-3 w-3 text-zinc-500" />
                      ) : (
                        <EyeOff className="h-3 w-3 text-zinc-700" />
                      )}
                    </span>
                  </button>
                );
              })}

              {/* ── Telemetry Block ──────────────────────────── */}
              <div className="mt-3 border-t border-zinc-800/60 pt-3">
                <span className="font-mono text-[9px] font-medium uppercase tracking-widest text-zinc-600 px-2.5">
                  Telemetry
                </span>
                <div className="mt-2 flex flex-col gap-1.5 px-2.5">
                  {[
                    { label: "ALTITUDE", value: "—", unit: "m" },
                    { label: "BEARING", value: "—", unit: "°" },
                    { label: "ACCURACY", value: "HIGH", unit: "" },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center justify-between">
                      <span className="font-mono text-[9px] text-zinc-600">{item.label}</span>
                      <span className="font-mono text-[10px] text-zinc-400 tabular-nums">
                        {item.value}
                        {item.unit && <span className="text-zinc-600 ml-0.5">{item.unit}</span>}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* ── Signal Strength ──────────────────────────── */}
              <div className="mt-3 border-t border-zinc-800/60 pt-3 px-2.5">
                <span className="font-mono text-[9px] font-medium uppercase tracking-widest text-zinc-600">
                  Signal Strength
                </span>
                <div className="mt-2 flex items-end gap-[3px] h-6">
                  {[40, 65, 80, 55, 90, 70, 45, 85, 60, 75, 50, 95].map((h, i) => (
                    <div
                      key={i}
                      className="w-[3px] bg-emerald-500/40 rounded-none transition-all"
                      style={{ height: `${h}%` }}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Collapsed icons */}
          {!sidebarOpen && (
            <div className="flex flex-col items-center gap-2 pt-2">
              <Layers className="h-3.5 w-3.5 text-zinc-600" />
              <Activity className="h-3.5 w-3.5 text-zinc-700" />
              <Signal className="h-3.5 w-3.5 text-zinc-700" />
            </div>
          )}
        </aside>

        {/* ── Map Area ─────────────────────────────────────── */}
        <div className="relative flex-1 flex flex-col min-h-0">
          {/* Map */}
          <div className="relative flex-1 min-h-0">
            {/* Tactical overlays */}
            <div className="scan-line" />
            <div className="tactical-grid" />
            <div className="corner-bracket tl" />
            <div className="corner-bracket tr" />
            <div className="corner-bracket bl" />
            <div className="corner-bracket br" />

            {/* Reticle */}
            <div className="reticle" style={{ width: 100, height: 100 }}>
              <div className="reticle-line h left" />
              <div className="reticle-line h right" />
              <div className="reticle-line v top" />
              <div className="reticle-line v bottom" />
              <div className="reticle-center" />
            </div>

            {/* Coordinate HUD — bottom-left of map */}
            <div className="absolute bottom-10 left-3 z-[1000] flex flex-col gap-0.5 rounded-none border border-zinc-800/80 bg-zinc-950/90 px-3 py-2">
              <div className="flex items-center gap-2">
                <Crosshair className="h-3 w-3 text-emerald-500/60" />
                <span className="font-mono text-[10px] uppercase tracking-wider text-zinc-600">
                  Cursor Position
                </span>
              </div>
              <div className="font-mono text-[11px] tabular-nums text-emerald-400/80 mt-0.5">
                {formatCoord(mousePos.lat, "N", "S")}
              </div>
              <div className="font-mono text-[11px] tabular-nums text-emerald-400/80">
                {formatCoord(mousePos.lng, "E", "W")}
              </div>
            </div>

            <MapContainer
              center={MUMBAI_CENTER}
              zoom={DEFAULT_ZOOM}
              className="h-full w-full"
              zoomControl={true}
              attributionControl={true}
            >
              <TileLayer url={DARK_TILE_URL} attribution={TILE_ATTRIBUTION} />
              <MapController onMouseMove={handleMouseMove} onZoomChange={handleZoomChange} />
            </MapContainer>
          </div>

          {/* ── Bottom Status Bar — 28px ────────────────────── */}
          <div className="flex h-7 min-h-7 items-center justify-between border-t border-zinc-800/80 bg-zinc-950 px-3">
            {/* Left */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-[9px] uppercase text-zinc-600">Lat</span>
                <span className="font-mono text-[10px] tabular-nums text-zinc-400">
                  {mousePos.lat.toFixed(6)}
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-[9px] uppercase text-zinc-600">Lng</span>
                <span className="font-mono text-[10px] tabular-nums text-zinc-400">
                  {mousePos.lng.toFixed(6)}
                </span>
              </div>
              <div className="h-3 w-px bg-zinc-800" />
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-[9px] uppercase text-zinc-600">Zoom</span>
                <span className="font-mono text-[10px] tabular-nums text-zinc-300">
                  {zoom}
                </span>
              </div>
            </div>

            {/* Center */}
            <div className="flex items-center gap-1.5">
              <div className="h-1.5 w-1.5 rounded-full bg-emerald-500/50 data-tick" />
              <span className="font-mono text-[9px] uppercase tracking-wider text-zinc-600">
                All Systems Nominal
              </span>
            </div>

            {/* Right */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-[9px] uppercase text-zinc-600">Proj</span>
                <span className="font-mono text-[10px] text-zinc-400">EPSG:4326</span>
              </div>
              <div className="h-3 w-px bg-zinc-800" />
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-[9px] uppercase text-zinc-600">Layers</span>
                <span className="font-mono text-[10px] text-zinc-300">{activeCount}</span>
              </div>
              <div className="h-3 w-px bg-zinc-800" />
              <span className="font-mono text-[9px] text-zinc-700">v0.1.0-alpha</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
