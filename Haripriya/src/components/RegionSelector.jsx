import React from 'react';
import { mockRegions } from '../data/mockRegions';

const RegionSelector = ({ selectedRegion, onRegionChange }) => {
  return (
    <div className="flex items-center space-x-2">
      <label htmlFor="region-select" className="text-sm text-slate-400 font-medium">
        Region:
      </label>
      <select
        id="region-select"
        value={selectedRegion}
        onChange={(e) => onRegionChange(e.target.value)}
        className="bg-slate-800 border border-slate-700 text-white text-sm rounded focus:ring-blue-500 focus:border-blue-500 block w-full p-2"
      >
        <option value="" disabled>Select a Region</option>
        {mockRegions.map((region) => (
          <option key={region.id} value={region.id}>
            {region.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default RegionSelector;
