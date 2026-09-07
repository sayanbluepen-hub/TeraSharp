/**
 * ConfusionMatrix.jsx
 *
 * Renders a 5×5 heatmap confusion matrix.
 * Props:
 *   matrix      – number[][] (rows = actual, cols = predicted)
 *   classLabels – string[]
 */

import React from 'react';

// Colour scale: white-ish → dark green (diagonal), light → orange-red (off-diag)
function cellColour(value, isDiagonal) {
  if (isDiagonal) {
    // Green gradient: 80→100 maps to darker greens
    const intensity = Math.min(1, (value - 70) / 30); // 0–1
    const r = Math.round(16  - 16  * intensity);
    const g = Math.round(185 - 50  * (1 - intensity));
    const b = Math.round(129 - 80  * (1 - intensity));
    return `rgba(${r},${g},${b},${0.25 + 0.65 * intensity})`;
  } else {
    if (value === 0) return 'transparent';
    const alpha = Math.min(0.7, value / 10);
    return `rgba(239,68,68,${alpha})`;
  }
}

function textColour(value, isDiagonal) {
  if (isDiagonal) return '#d1fae5';
  if (value === 0) return '#64748b';
  return value > 5 ? '#fecaca' : '#94a3b8';
}

export default function ConfusionMatrix({ matrix, classLabels }) {
  const maxVal = Math.max(...matrix.flat());

  return (
    <div className="overflow-x-auto">
      {/* Column header */}
      <div className="mb-1">
        <p className="text-center text-[10px] text-gis-muted tracking-widest uppercase mb-1">
          Predicted →
        </p>
        <div className="grid" style={{ gridTemplateColumns: `56px repeat(${classLabels.length}, 1fr)` }}>
          <div />
          {classLabels.map((lbl) => (
            <div key={lbl} className="text-center text-[9px] font-medium text-gis-muted leading-tight px-0.5 truncate" title={lbl}>
              {lbl.split(' ')[0]}
            </div>
          ))}
        </div>
      </div>

      {/* Row label + cells */}
      <div className="flex gap-1 items-center mb-2">
        <p className="text-[10px] text-gis-muted tracking-widest uppercase"
           style={{ writingMode: 'vertical-rl', transform: 'rotate(180deg)', whiteSpace: 'nowrap', marginRight: 2 }}>
          Actual ↓
        </p>
        <div className="flex-1">
          {matrix.map((row, ri) => (
            <div
              key={ri}
              className="grid items-center"
              style={{ gridTemplateColumns: `56px repeat(${classLabels.length}, 1fr)`, marginBottom: 2 }}
            >
              <div className="text-[9px] font-medium text-gis-muted leading-tight pr-1 truncate" title={classLabels[ri]}>
                {classLabels[ri].split(' ')[0]}
              </div>
              {row.map((val, ci) => {
                const isDiag = ri === ci;
                return (
                  <div
                    key={ci}
                    title={`Actual: ${classLabels[ri]}, Predicted: ${classLabels[ci]}, Count: ${val}`}
                    className="flex items-center justify-center rounded text-[11px] font-semibold transition-all duration-200 hover:scale-105 hover:z-10 relative"
                    style={{
                      height: 32,
                      background: cellColour(val, isDiag),
                      color: textColour(val, isDiag),
                      fontFamily: "'JetBrains Mono', monospace",
                      border: isDiag ? '1px solid rgba(16,185,129,0.4)' : '1px solid rgba(255,255,255,0.04)',
                      cursor: 'default',
                    }}
                  >
                    {val}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-1 justify-center">
        <span className="flex items-center gap-1 text-[10px] text-gis-muted">
          <span className="w-3 h-3 rounded-sm inline-block" style={{ background: 'rgba(16,185,129,0.7)', border: '1px solid rgba(16,185,129,0.5)' }} />
          Correct (diagonal)
        </span>
        <span className="flex items-center gap-1 text-[10px] text-gis-muted">
          <span className="w-3 h-3 rounded-sm inline-block" style={{ background: 'rgba(239,68,68,0.5)' }} />
          Misclassified
        </span>
      </div>
    </div>
  );
}
