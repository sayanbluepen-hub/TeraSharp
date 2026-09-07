import React, { useState } from 'react';
import { Download, Link as LinkIcon, X } from 'lucide-react';

const ExportModal = () => {
  const [isOpen, setIsOpen] = useState(false);

  const downloadEnhancedGeoTIFF = () => {
    alert('Mock: Downloading Enhanced GeoTIFF...');
    setIsOpen(false);
  };

  const downloadEntropyGeoTIFF = () => {
    alert('Mock: Downloading Entropy GeoTIFF...');
    setIsOpen(false);
  };

  const copyTileURL = () => {
    navigator.clipboard.writeText('https://mock-tile-server.com/srm/{z}/{x}/{y}.png');
    alert('Mock: WMTS/XYZ Link copied to clipboard!');
    setIsOpen(false);
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded text-sm font-medium transition-colors flex items-center gap-2"
      >
        <Download size={16} />
        Export
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 border border-slate-700 rounded-lg shadow-xl w-96 max-w-full overflow-hidden">
            <div className="flex justify-between items-center p-4 border-b border-slate-700">
              <h3 className="text-lg font-semibold text-white">Export Results</h3>
              <button 
                onClick={() => setIsOpen(false)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="p-4 flex flex-col gap-3">
              <button 
                onClick={downloadEnhancedGeoTIFF}
                className="w-full text-left px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded transition-colors flex items-center gap-3"
              >
                <Download size={18} className="text-blue-400" />
                <span>Download Enhanced GeoTIFF</span>
              </button>
              
              <button 
                onClick={downloadEntropyGeoTIFF}
                className="w-full text-left px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded transition-colors flex items-center gap-3"
              >
                <Download size={18} className="text-purple-400" />
                <span>Download Entropy GeoTIFF</span>
              </button>

              <button 
                onClick={copyTileURL}
                className="w-full text-left px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded transition-colors flex items-center gap-3"
              >
                <LinkIcon size={18} className="text-green-400" />
                <span>Copy WMTS / XYZ Link</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ExportModal;
