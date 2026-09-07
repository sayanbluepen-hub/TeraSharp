import React from 'react';
import { Play, ArrowLeft, ArrowRight, RotateCcw } from 'lucide-react';

const steps = ['region', 'input', 'output', 'entropy', 'validation'];

const DemoController = ({ currentStep, onNext, onPrevious, onReset }) => {
  const currentIndex = steps.indexOf(currentStep);
  const isFirstStep = currentIndex === 0;
  const isLastStep = currentIndex === steps.length - 1;

  return (
    <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 shadow-md flex items-center gap-4 justify-between">
      <button
        onClick={() => onReset()}
        className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded font-medium transition-colors"
      >
        <Play size={16} />
        Start Demo
      </button>

      <div className="flex items-center gap-3">
        <button
          onClick={onPrevious}
          disabled={isFirstStep}
          className={`flex items-center gap-2 px-4 py-2 rounded font-medium transition-colors ${
            isFirstStep
              ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
              : 'bg-slate-700 hover:bg-slate-600 text-white'
          }`}
        >
          <ArrowLeft size={16} />
          Previous
        </button>

        <button
          onClick={onNext}
          disabled={isLastStep}
          className={`flex items-center gap-2 px-6 py-2 rounded font-bold transition-colors shadow-lg ${
            isLastStep
              ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-500 text-white'
          }`}
        >
          Next
          <ArrowRight size={16} />
        </button>
      </div>

      <button
        onClick={onReset}
        className="flex items-center gap-2 px-4 py-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded font-medium transition-colors"
      >
        <RotateCcw size={16} />
        Reset
      </button>
    </div>
  );
};

export default DemoController;
