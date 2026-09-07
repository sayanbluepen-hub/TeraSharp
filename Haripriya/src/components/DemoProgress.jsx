import React from 'react';

const steps = [
  { id: 'region', label: 'Load Region' },
  { id: 'input', label: 'Raw Input' },
  { id: 'output', label: 'SRM Output' },
  { id: 'entropy', label: 'Entropy Map' },
  { id: 'validation', label: 'Validation' }
];

const DemoProgress = ({ currentStep }) => {
  return (
    <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 shadow-md mb-6">
      <h3 className="text-slate-400 text-sm font-semibold mb-4 uppercase tracking-wider">Demo Progress</h3>
      <ul className="space-y-3">
        {steps.map((step) => {
          const isActive = step.id === currentStep;
          return (
            <li key={step.id} className={`flex items-center gap-3 transition-colors ${isActive ? 'text-blue-400 font-bold' : 'text-slate-500'}`}>
              <div className={`w-2.5 h-2.5 rounded-full ${isActive ? 'bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.8)]' : 'bg-slate-600'}`}></div>
              <span className="text-sm">{step.label}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default DemoProgress;
