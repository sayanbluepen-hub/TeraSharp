import React from 'react';
import RegionSelector from './RegionSelector';
import ExportModal from './ExportModal';
import PresentationMode from './PresentationMode';

const TopNavigation = ({ selectedRegion, onRegionChange, isPresentationMode, togglePresentationMode }) => {
  return (
    <div className="bg-slate-900 border-b border-slate-800 p-4 flex items-center justify-between shadow-md">
      <div className="flex flex-col">
        <h1 className="text-xl font-bold text-white tracking-tight">
          SRM — Satellite Super Resolution Mapping
        </h1>
        <span className="text-xs text-blue-400 font-semibold tracking-wider uppercase mt-1">
          Smart India Hackathon 2026
        </span>
      </div>
      
      {!isPresentationMode && (
        <div className="flex items-center gap-6">
          <RegionSelector 
            selectedRegion={selectedRegion} 
            onRegionChange={onRegionChange} 
          />
          <div className="h-8 w-px bg-slate-700"></div>
          <ExportModal />
        </div>
      )}

      <div className="ml-6">
        <PresentationMode 
          isPresentationMode={isPresentationMode} 
          togglePresentationMode={togglePresentationMode} 
        />
      </div>
    </div>
  );
};

export default TopNavigation;
