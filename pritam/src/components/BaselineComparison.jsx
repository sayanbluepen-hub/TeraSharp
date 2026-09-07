/**
 * BaselineComparison.jsx
 *
 * Compares Nearest Neighbor interpolation vs SRM AI Model.
 * Props:
 *   baselineData – {
 *     nearest_neighbor: { overall_accuracy: number, kappa: number },
 *     srm_model:        { overall_accuracy: number, kappa: number },
 *   }
 */

import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, LabelList,
} from 'recharts';

// ─── Custom Tooltip ──────────────────────────────────────────────────────────
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded px-2 py-1.5 text-xs" style={{ background: '#1a2235', border: '1px solid #1e3a5f', color: '#e2e8f0' }}>
      <p className="font-semibold mb-1" style={{ color: '#94a3b8' }}>{label}</p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color }}>
          {p.name}: <strong>{p.value}{p.name === 'OA (%)' ? '%' : ''}</strong>
        </p>
      ))}
    </div>
  );
}

// ─── Comparison Card ─────────────────────────────────────────────────────────
function ModelCard({ title, oa, kappa, highlight, icon }) {
  return (
    <div
      className="flex-1 rounded-xl p-3 flex flex-col gap-2"
      style={{
        background: highlight ? 'rgba(16,185,129,0.08)' : 'rgba(255,255,255,0.03)',
        border: `1px solid ${highlight ? 'rgba(16,185,129,0.35)' : 'rgba(255,255,255,0.07)'}`,
      }}
    >
      <div className="flex items-center gap-1.5">
        <span className="text-base">{icon}</span>
        <p className="text-[10px] font-semibold leading-tight" style={{ color: highlight ? '#10b981' : '#94a3b8' }}>{title}</p>
      </div>
      <div>
        <p className="text-[10px] tracking-wider uppercase" style={{ color: '#64748b' }}>Overall Accuracy</p>
        <p className="text-2xl font-bold tabular-nums leading-none" style={{ color: highlight ? '#10b981' : '#e2e8f0' }}>
          {oa.toFixed(1)}<span className="text-sm">%</span>
        </p>
      </div>
      <div>
        <p className="text-[10px] tracking-wider uppercase" style={{ color: '#64748b' }}>Kappa</p>
        <p className="text-lg font-bold tabular-nums" style={{ color: highlight ? '#10b981' : '#e2e8f0', fontFamily: "'JetBrains Mono', monospace" }}>
          {kappa.toFixed(2)}
        </p>
      </div>
    </div>
  );
}

// ─── Improvement Badge ────────────────────────────────────────────────────────
function ImprovementBadge({ delta, label }) {
  return (
    <div className="flex flex-col items-center justify-center px-2">
      <div
        className="rounded-full px-2 py-0.5 mb-0.5"
        style={{ background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.3)' }}
      >
        <p className="text-[11px] font-bold" style={{ color: '#10b981' }}>+{delta}</p>
      </div>
      <p className="text-[9px] text-center" style={{ color: '#64748b', maxWidth: 40 }}>{label}</p>
    </div>
  );
}

// ─── Component ────────────────────────────────────────────────────────────────
export default function BaselineComparison({ baselineData }) {
  const nn  = baselineData.nearest_neighbor;
  const srm = baselineData.srm_model;

  const oaDelta    = (srm.overall_accuracy - nn.overall_accuracy).toFixed(1);
  const kappaDelta = (srm.kappa - nn.kappa).toFixed(2);

  const chartData = [
    {
      name: 'Nearest\nNeighbor',
      'OA (%)': parseFloat(nn.overall_accuracy.toFixed(1)),
      'Kappa (×100)': parseFloat((nn.kappa * 100).toFixed(1)),
    },
    {
      name: 'SRM\nModel',
      'OA (%)': parseFloat(srm.overall_accuracy.toFixed(1)),
      'Kappa (×100)': parseFloat((srm.kappa * 100).toFixed(1)),
    },
  ];

  return (
    <section className="gis-card animate-fade-in-up" style={{ animationDelay: '120ms' }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded flex items-center justify-center" style={{ background: 'rgba(245,158,11,0.15)' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>
              <line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/>
            </svg>
          </div>
          <h2 className="text-sm font-semibold" style={{ color: '#e2e8f0' }}>Baseline Comparison</h2>
        </div>
        <span className="badge badge-demo">DEMO</span>
      </div>

      {/* Model cards */}
      <div className="flex gap-1 mb-3 items-center">
        <ModelCard title="Nearest Neighbor" oa={nn.overall_accuracy} kappa={nn.kappa} highlight={false} icon="🔲" />
        <div className="flex flex-col items-center gap-1">
          <ImprovementBadge delta={`${oaDelta}%`}    label="OA gain" />
          <ImprovementBadge delta={kappaDelta}         label="κ gain" />
        </div>
        <ModelCard title="SRM AI Model"     oa={srm.overall_accuracy} kappa={srm.kappa} highlight={true}  icon="🛰️" />
      </div>

      {/* Bar chart */}
      <p className="section-label">Visual Comparison</p>
      <div style={{ height: 110 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 14, right: 12, bottom: 0, left: -10 }} barCategoryGap="30%">
            <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis
              dataKey="name"
              tick={{ fontSize: 9, fill: '#94a3b8' }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              domain={[0, 105]}
              tick={{ fontSize: 9, fill: '#64748b' }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
            <Bar dataKey="OA (%)"       fill="#0ea5e9" radius={[4,4,0,0]} maxBarSize={28}>
              <LabelList dataKey="OA (%)"       position="top" style={{ fontSize: 9, fill: '#94a3b8' }} formatter={(v) => `${v}%`} />
            </Bar>
            <Bar dataKey="Kappa (×100)" fill="#10b981" radius={[4,4,0,0]} maxBarSize={28}>
              <LabelList dataKey="Kappa (×100)" position="top" style={{ fontSize: 9, fill: '#94a3b8' }} formatter={(v) => `${(v/100).toFixed(2)}`} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Note */}
      <p className="text-[9px] mt-2 text-center" style={{ color: '#475569' }}>
        ⚠️ Demo metrics — replace with real ML evaluation results from the model team.
      </p>
    </section>
  );
}
