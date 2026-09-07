/**
 * SubPixelInspector.jsx
 *
 * Displays per-pixel land-cover fractions, entropy, confidence, and spectral bands.
 *
 * Props:
 *   pixelData – object matching the shape below (can be supplied from FastAPI response)
 *
 * Expected pixelData shape:
 * {
 *   built_up:   number,  // 0–1 land-cover fraction
 *   vegetation: number,
 *   water:      number,
 *   cropland:   number,
 *   bare_land:  number,
 *   entropy:    number,  // 0–1 (lower = more confident)
 *   B04:        number,  // Sentinel-2 band reflectance (scaled)
 *   B03:        number,
 *   B02:        number,
 *   B08:        number,
 * }
 *
 * API integration note:
 *   To wire this to Sayan's FastAPI endpoint, lift pixelData state into App.jsx
 *   and pass the JSON response directly as the pixelData prop.
 *   Example:
 *     const res = await fetch('/api/pixel?x=...&y=...');
 *     const data = await res.json();
 *     setPixelData(data);
 *
 * Utility helper for programmatic updates (e.g., map click events):
 *   export function updatePixelData(setter, apiResponse) { setter(apiResponse); }
 */

import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';

// ─── Helpers ─────────────────────────────────────────────────────────────────

const LC_CLASSES = [
  { key: 'built_up',   label: 'Built-up',   color: '#f97316' },
  { key: 'vegetation', label: 'Vegetation', color: '#10b981' },
  { key: 'water',      label: 'Water',      color: '#0ea5e9' },
  { key: 'cropland',   label: 'Cropland',   color: '#a3e635' },
  { key: 'bare_land',  label: 'Bare Land',  color: '#a8a29e' },
];

const SPECTRAL_BANDS = [
  { key: 'B04', label: 'B04', desc: 'Red' },
  { key: 'B03', label: 'B03', desc: 'Green' },
  { key: 'B02', label: 'B02', desc: 'Blue' },
  { key: 'B08', label: 'B08', desc: 'NIR' },
];

function getConfidence(entropy) {
  if (entropy < 0.25) return { label: 'HIGH CONFIDENCE', colour: '#10b981', bg: 'rgba(16,185,129,0.12)', border: 'rgba(16,185,129,0.3)' };
  if (entropy < 0.55) return { label: 'MEDIUM CONFIDENCE', colour: '#f59e0b', bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.3)' };
  return { label: 'LOW CONFIDENCE', colour: '#ef4444', bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.3)' };
}

// Custom tooltip for bar chart
function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0];
  return (
    <div className="rounded px-2 py-1 text-xs" style={{ background: '#1a2235', border: '1px solid #1e3a5f', color: '#e2e8f0' }}>
      <span style={{ color: d.color }}>{d.name}</span>: {(d.value * 100).toFixed(1)}%
    </div>
  );
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function SubPixelInspector({ pixelData }) {
  const confidence = getConfidence(pixelData.entropy);

  const chartData = LC_CLASSES.map(({ key, label }) => ({
    name: label,
    value: pixelData[key] ?? 0,
  }));

  return (
    <section className="gis-card animate-fade-in-up" style={{ animationDelay: '60ms' }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded flex items-center justify-center" style={{ background: 'rgba(16,185,129,0.15)' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </div>
          <h2 className="text-sm font-semibold" style={{ color: '#e2e8f0' }}>Sub-Pixel Inspector</h2>
        </div>
        <span className="badge badge-demo">DEMO</span>
      </div>

      {/* Land Cover Fractions */}
      <p className="section-label">Land Cover Fractions</p>
      <div className="mb-3" style={{ height: 120 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 0, right: 30, bottom: 0, left: 60 }}
          >
            <XAxis
              type="number"
              domain={[0, 1]}
              tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
              tick={{ fontSize: 9, fill: '#64748b' }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fontSize: 10, fill: '#94a3b8' }}
              axisLine={false}
              tickLine={false}
              width={58}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
            <Bar dataKey="value" radius={[0, 3, 3, 0]} maxBarSize={14}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={LC_CLASSES[index].color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Entropy + Confidence */}
      <div className="flex items-center gap-2 mb-3">
        <div className="flex-1 rounded-lg p-2" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}>
          <p className="text-[10px] tracking-widest uppercase text-gis-muted mb-0.5">Entropy</p>
          <p className="text-lg font-bold tabular-nums" style={{ color: confidence.colour, fontFamily: "'JetBrains Mono', monospace" }}>
            {pixelData.entropy.toFixed(2)}
          </p>
        </div>
        <div
          className="flex-1 rounded-lg p-2 flex flex-col justify-center items-center pulse-green"
          style={{ background: confidence.bg, border: `1px solid ${confidence.border}` }}
        >
          <p className="text-[9px] font-bold tracking-wider text-center" style={{ color: confidence.colour }}>
            {confidence.label}
          </p>
        </div>
      </div>

      {/* Spectral Values */}
      <p className="section-label">Spectral Reflectance</p>
      <div className="grid grid-cols-4 gap-1.5">
        {SPECTRAL_BANDS.map(({ key, label, desc }) => (
          <div
            key={key}
            className="rounded-lg p-2 text-center"
            style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}
          >
            <p className="text-[9px] font-semibold tracking-wider mb-0.5" style={{ color: '#0ea5e9' }}>{label}</p>
            <p className="text-[10px] font-bold tabular-nums" style={{ color: '#e2e8f0', fontFamily: "'JetBrains Mono', monospace" }}>
              {pixelData[key] ?? '—'}
            </p>
            <p className="text-[9px]" style={{ color: '#64748b' }}>{desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

/**
 * updatePixelData — utility for programmatic updates from map click handlers.
 * Usage: updatePixelData(setPixelData, apiResponse)
 *
 * @param {Function} setter   – React setState function
 * @param {Object}   apiData  – JSON from FastAPI /api/pixel endpoint
 */
export function updatePixelData(setter, apiData) {
  setter(apiData);
}
