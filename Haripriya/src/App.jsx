import React, { useState } from 'react';
import TopNavigation from './components/TopNavigation';
import DemoController from './components/DemoController';
import DemoProgress from './components/DemoProgress';
import { mockRegions } from './data/mockRegions';

const steps = ['region', 'input', 'output', 'entropy', 'validation'];

function App() {
  const [currentStep, setCurrentStep] = useState('region');
  const [selectedRegion, setSelectedRegion] = useState('');
  const [isPresentationMode, setIsPresentationMode] = useState(false);

  const nextStep = () => {
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1]);
    }
  };

  const previousStep = () => {
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1]);
    }
  };

  const resetDemo = () => {
    setCurrentStep('region');
  };

  const togglePresentationMode = () => {
    setIsPresentationMode(!isPresentationMode);
  };

  const selectedRegionName = mockRegions.find(r => r.id === selectedRegion)?.name || 'None Selected';

  const renderMockMainArea = () => {
    switch (currentStep) {
      case 'region':
        return (
          <div className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-slate-700 rounded-lg bg-slate-800/50">
            <h2 className="text-3xl font-bold text-white mb-2">Select a Region</h2>
            <p className="text-slate-400">Current selection: {selectedRegionName}</p>
          </div>
        );
      case 'input':
        return (
          <div className="flex-1 flex flex-col items-center justify-center border-2 border-slate-700 rounded-lg bg-[url('https://images.unsplash.com/photo-1524661135-423995f22d0b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80')] bg-cover bg-center relative">
            <div className="absolute inset-0 bg-slate-900/60 rounded-lg"></div>
            <h2 className="text-3xl font-bold text-white z-10">Medium-Resolution Input</h2>
            <p className="text-slate-300 z-10 mt-2">Original Satellite Image</p>
          </div>
        );
      case 'output':
        return (
          <div className="flex-1 flex flex-col items-center justify-center border-2 border-slate-700 rounded-lg bg-[url('https://images.unsplash.com/photo-1524661135-423995f22d0b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80')] bg-cover bg-center relative">
            <div className="absolute inset-0 bg-blue-900/40 rounded-lg backdrop-contrast-125"></div>
            <h2 className="text-3xl font-bold text-white z-10 drop-shadow-lg">Super-Resolution Output</h2>
            <p className="text-blue-100 z-10 mt-2 drop-shadow-md">Enhanced Image</p>
          </div>
        );
      case 'entropy':
        return (
          <div className="flex-1 flex flex-col items-center justify-center border-2 border-slate-700 rounded-lg bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 relative">
            <div className="absolute inset-0 mix-blend-overlay opacity-30 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')]"></div>
            <h2 className="text-3xl font-bold text-white z-10">Uncertainty / Entropy Map</h2>
            <p className="text-purple-200 z-10 mt-2">Displaying Entropy Layer</p>
          </div>
        );
      case 'validation':
        return (
          <div className="flex-1 flex flex-col items-center justify-center border-2 border-slate-700 rounded-lg bg-slate-800">
            <h2 className="text-3xl font-bold text-white mb-6">Model Validation</h2>
            <div className="grid grid-cols-2 gap-4 w-full max-w-2xl">
              <div className="bg-slate-700 p-6 rounded-lg text-center">
                <div className="text-sm text-slate-400 mb-1">PSNR</div>
                <div className="text-2xl font-bold text-emerald-400">32.4 dB</div>
              </div>
              <div className="bg-slate-700 p-6 rounded-lg text-center">
                <div className="text-sm text-slate-400 mb-1">SSIM</div>
                <div className="text-2xl font-bold text-emerald-400">0.89</div>
              </div>
            </div>
            <p className="text-slate-400 mt-6">(Existing Validation/Metrics Section Placeholder)</p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col font-sans">
      <TopNavigation 
        selectedRegion={selectedRegion}
        onRegionChange={setSelectedRegion}
        isPresentationMode={isPresentationMode}
        togglePresentationMode={togglePresentationMode}
      />
      
      <div className="flex-1 flex overflow-hidden p-4 gap-6">
        {/* Left Sidebar (Hidden in presentation mode) */}
        {!isPresentationMode && (
          <div className="w-64 flex flex-col shrink-0 gap-4">
            <DemoProgress currentStep={currentStep} />
            
            <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 flex-1">
              <h3 className="text-slate-400 text-sm font-semibold mb-4 uppercase tracking-wider">Other Tools</h3>
              <p className="text-sm text-slate-500 italic">
                (Member 3's Inspector Panels will go here)
              </p>
            </div>
          </div>
        )}
        
        {/* Main Workspace Area */}
        <div className="flex-1 flex flex-col gap-4 min-w-0">
          {/* Mock Map / Visualization Area */}
          <div className="flex-1 bg-black rounded-lg shadow-inner overflow-hidden flex flex-col">
            {renderMockMainArea()}
          </div>
          
          {/* Bottom Control Bar */}
          <div className="shrink-0">
            <DemoController 
              currentStep={currentStep}
              onNext={nextStep}
              onPrevious={previousStep}
              onReset={resetDemo}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
