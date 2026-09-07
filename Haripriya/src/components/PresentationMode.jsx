import React from 'react';
import { Maximize2, Minimize2 } from 'lucide-react';

const PresentationMode = ({ isPresentationMode, togglePresentationMode }) => {
  return (
    <button
      onClick={togglePresentationMode}
      className={`px-4 py-2 rounded text-sm font-medium transition-colors flex items-center gap-2 ${
        isPresentationMode 
          ? 'bg-blue-600 hover:bg-blue-700 text-white' 
          : 'bg-slate-700 hover:bg-slate-600 text-white'
      }`}
    >
      {isPresentationMode ? (
        <>
          <Minimize2 size={16} />
          Exit Presentation
        </>
      ) : (
        <>
          <Maximize2 size={16} />
          Presentation Mode
        </>
      )}
    </button>
  );
};

export default PresentationMode;
