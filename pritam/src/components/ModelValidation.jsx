/**
 * ModelValidation.jsx
 *
 * Displays overall accuracy, kappa coefficient, and the confusion matrix.
 * Props:
 *   metrics       – { overall_accuracy: number, kappa: number }
 *   matrix        – number[][]
 *   classLabels   – string[]
 */

import React from 'react';
import ConfusionMatrix from './ConfusionMatrix';

function MetricBlock({ label, value, unit = '', colour = '#0ea5e9', sub }) {
  return (
    <div className="flex-1 rounded-lg p-3" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}>
      <p className="text-[10px] tracking-widest uppercase font-semibold mb-1" style={{ color: '#64748b' }}>{label}</p>
      <p className="text-2xl font-bold tabular-nums leading-none" style={{ color }}>
        {value}{unit}
      </p>
      {sub && <p className="text-[10px] mt-1" style={{ color: '#64748b' }}>{sub}</p>}
    </div>
  );
}

export default function ModelValidation({ metrics, matrix, classLabels }) {
  const { overall_accuracy, kappa } = metrics;

  // Colour for OA
  const oaColour = overall_accuracy >= 90 ? '#10b981' : overall_accuracy >= 75 ? '#f59e0b' : '#ef4444';
  const kappaColour = kappa >= 0.8 ? '#10b981' : kappa >= 0.6 ? '#f59e0b' : '#ef4444';

  return (
    <section className="gis-card animate-fade-in-up" style={{ animationDelay: '0ms' }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {/* Icon */}
          <div className="w-6 h-6 rounded flex items-center justify-center" style={{ background: 'rgba(14,165,233,0.15)' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
            </svg>
          </div>
          <h2 className="text-sm font-semibold" style={{ color: '#e2e8f0' }}>Model Validation</h2>
        </div>
        <span className="badge badge-demo">DEMO</span>
      </div>

      {/* Metric row */}
      <div className="flex gap-2 mb-4">
        <MetricBlock
          label="Overall Accuracy"
          value={overall_accuracy.toFixed(1)}
          unit="%"
          colour={oaColour}
          sub="5-class LC classification"
        />
        <MetricBlock
          label="Kappa Coefficient"
          value={kappa.toFixed(2)}
          colour={kappaColour}
          sub="Almost Perfect (κ ≥ 0.80)"
        />
      </div>

      {/* Confusion Matrix */}
      <div>
        <p className="section-label">Confusion Matrix</p>
        <ConfusionMatrix matrix={matrix} classLabels={classLabels} />
      </div>
    </section>
  );
}
