/**
 * App.jsx
 *
 * Main application layout integrating the SRM Validation Dashboard.
 * Left: A mock GIS map area (to represent where the map goes).
 * Right: The Validation side-panel with the three components.
 */

import React, { useState } from 'react';

import ModelValidation from './components/ModelValidation';
import SubPixelInspector from './components/SubPixelInspector';
import BaselineComparison from './components/BaselineComparison';

import {
  VALIDATION_METRICS,
  CLASS_LABELS,
  CONFUSION_MATRIX,
  MOCK_PIXEL_DATA,
  BASELINE_DATA,
} from './data/mockValidationData';

function App() {
  // State for pixel inspector. In a real app, this is populated by an API response
  // when the user clicks on the map.
  const [pixelData, setPixelData] = useState(MOCK_PIXEL_DATA);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-gis-bg">
      {/* ─── LEFT: MAIN MAP AREA ────────────────────────────────────────────── */}
      <main className="flex-1 relative bg-gis-surface border-r border-gis-border flex items-center justify-center">
        <div className="absolute inset-0 opacity-10 pointer-events-none"
             style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.15) 1px, transparent 0)', backgroundSize: '32px 32px' }} />
        
        <div className="text-center z-10">
          <h1 className="text-2xl font-bold tracking-tight text-gis-text mb-2">
            Super-Resolution Mapping (SRM)
          </h1>
          <p className="text-gis-muted max-w-md mx-auto">
            (Map component goes here. Click on a pixel to view sub-pixel validation metrics in the right panel.)
          </p>
        </div>
        
        {/* Mock API "fetch" button just to show interaction */}
        <button
          onClick={() => {
            // Simulate fetching new pixel data with slightly jittered values
            const jitter = () => (Math.random() * 0.1 - 0.05);
            setPixelData(prev => ({
              ...prev,
              built_up: Math.max(0, Math.min(1, prev.built_up + jitter())),
              vegetation: Math.max(0, Math.min(1, prev.vegetation + jitter())),
              entropy: Math.max(0, Math.min(1, prev.entropy + jitter() * 2)),
              B04: Math.floor(prev.B04 * (1 + jitter())),
            }));
          }}
          className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-gis-card border border-gis-border px-4 py-2 rounded-lg shadow-lg hover:bg-gis-surface transition-colors text-sm font-medium text-gis-accent"
        >
          Simulate Map Click (Update Pixel)
        </button>
      </main>

      {/* ─── RIGHT: VALIDATION SIDEBAR ──────────────────────────────────────── */}
      <aside className="w-[420px] h-full flex flex-col bg-gis-bg shrink-0 shadow-2xl">
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gis-border shrink-0">
          <p className="section-label mb-1">SIH 2026</p>
          <h2 className="text-lg font-bold text-gis-text">Validation & Metrics</h2>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-5">
          <ModelValidation
            metrics={VALIDATION_METRICS}
            matrix={CONFUSION_MATRIX}
            classLabels={CLASS_LABELS}
          />
          
          <SubPixelInspector
            pixelData={pixelData}
          />
          
          <BaselineComparison
            baselineData={BASELINE_DATA}
          />
        </div>
      </aside>
    </div>
  );
}

export default App;
