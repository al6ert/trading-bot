import React, { useState, useEffect } from 'react';

interface CapitalAllocationBarProps {
  totalValue: number;
  currentUsdcPct?: number; // Current actual allocation
  currentBtcPct?: number;  // Current actual allocation
  initialUsdcLock?: number; // Initial lock value from backend
  initialBtcLock?: number;  // Initial lock value from backend
  onAllocationChange?: (usdcLock: number, btcLock: number) => void;
}

export const CapitalAllocationBar: React.FC<CapitalAllocationBarProps> = ({
  totalValue,
  currentUsdcPct = 60, // Default mock
  currentBtcPct = 40,  // Default mock
  initialUsdcLock = 20,
  initialBtcLock = 20,
  onAllocationChange,
}) => {
  // State for locks (percentages 0-100)
  const [usdcLock, setUsdcLock] = useState(initialUsdcLock);
  const [btcLock, setBtcLock] = useState(initialBtcLock);

  // Sync with parent when initial values change
  useEffect(() => {
    setUsdcLock(initialUsdcLock);
    setBtcLock(initialBtcLock);
  }, [initialUsdcLock, initialBtcLock]);

  // Calculate Active Capital
  const activeCapital = 100 - usdcLock - btcLock;

  // Handlers
  const handleUsdcChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVal = parseInt(e.target.value);
    // Constraint: Cannot lock more than current allocation
    // Constraint: usdcLock + btcLock <= 100
    if (newVal <= currentUsdcPct && newVal + btcLock <= 100) {
      setUsdcLock(newVal);
      onAllocationChange?.(newVal, btcLock);
    }
  };

  const handleBtcChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVal = parseInt(e.target.value);
    // Constraint: Cannot lock more than current allocation
    // Constraint: usdcLock + btcLock <= 100
    if (newVal <= currentBtcPct && usdcLock + newVal <= 100) {
      setBtcLock(newVal);
      onAllocationChange?.(usdcLock, newVal);
    }
  };

  // Values in USD
  const usdcValue = totalValue * (usdcLock / 100);
  const btcValue = totalValue * (btcLock / 100);
  const activeValue = totalValue * (activeCapital / 100);

  return (
    <div className="flex flex-col w-full select-none">
      {/* Header Info */}
      <div className="flex justify-between items-end mb-3">
        <div>
          <div className="text-[10px] font-bold opacity-50 uppercase tracking-wider">Total Capital</div>
          <div className="text-2xl font-black tracking-tight text-base-content leading-none mt-1">
            ${totalValue.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
          </div>
        </div>
        <div className="text-right">
           <div className="text-[10px] font-bold text-success uppercase tracking-wider">Active Trading</div>
           <div className="text-xl font-bold text-success leading-none mt-1">
             ${activeValue.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
           </div>
        </div>
      </div>

      {/* Slider Container */}
      <div className="relative w-full h-8 mt-6 mb-2">
        
        {/* Visual Bar (Background Layers) */}
        <div className="absolute top-0 left-0 w-full h-full rounded-md overflow-hidden flex pointer-events-none">
          {/* USDC Lock (Left) */}
          <div 
            className="h-full bg-base-300 flex items-center justify-start px-2 transition-all duration-75 relative"
            style={{ width: `${usdcLock}%` }}
          >
            {usdcLock > 10 && <span className="text-[10px] font-bold opacity-60 whitespace-nowrap">🔒 USDC</span>}
          </div>

          {/* Active Capital (Middle) */}
          <div 
            className="h-full bg-success/20 border-x border-base-100 flex items-center justify-center transition-all duration-75"
            style={{ width: `${activeCapital}%` }}
          >
             {activeCapital > 15 && <span className="text-[10px] font-bold text-success whitespace-nowrap">ACTIVE</span>}
          </div>

          {/* BTC Lock (Right) */}
          <div 
            className="h-full bg-warning/20 flex items-center justify-end px-2 transition-all duration-75 relative"
            style={{ width: `${btcLock}%` }}
          >
            {btcLock > 10 && <span className="text-[10px] font-bold text-warning-content opacity-80 whitespace-nowrap">BTC 🔒</span>}
          </div>
        </div>

        {/* Current Allocation Markers */}
        {/* USDC Marker */}
        <div 
            className="absolute top-0 bottom-0 w-0.5 bg-base-content/30 z-10 pointer-events-none"
            style={{ left: `${currentUsdcPct}%` }}
        >
            <div className="absolute -top-6 -translate-x-1/2 text-[9px] font-bold opacity-50 whitespace-nowrap">
                MAX {currentUsdcPct}%
            </div>
        </div>

        {/* BTC Marker (Calculated from right) */}
        <div 
            className="absolute top-0 bottom-0 w-0.5 bg-warning/50 z-10 pointer-events-none"
            style={{ right: `${currentBtcPct}%` }}
        >
            <div className="absolute -top-6 translate-x-1/2 text-[9px] font-bold text-warning opacity-80 whitespace-nowrap">
                MAX {currentBtcPct}%
            </div>
        </div>

        {/* Range Inputs */}
        <input
            type="range"
            min="0"
            max="100"
            value={usdcLock}
            onChange={handleUsdcChange}
            className="absolute top-0 left-0 w-full h-full appearance-none bg-transparent pointer-events-none z-20 [&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-8 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:bg-base-content [&::-webkit-slider-thumb]:rounded-sm [&::-webkit-slider-thumb]:cursor-ew-resize"
        />

        <input
            type="range"
            min="0"
            max="100"
            value={100 - btcLock} 
            onChange={(e) => {
                const splitPoint = parseInt(e.target.value);
                const newBtcLock = 100 - splitPoint;
                // Constraint: Cannot lock more than current allocation
                if (newBtcLock <= currentBtcPct && splitPoint >= usdcLock) {
                    setBtcLock(newBtcLock);
                    onAllocationChange?.(usdcLock, newBtcLock);
                }
            }}
            className="absolute top-0 left-0 w-full h-full appearance-none bg-transparent pointer-events-none z-20 [&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-8 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:bg-warning [&::-webkit-slider-thumb]:rounded-sm [&::-webkit-slider-thumb]:cursor-ew-resize"
        />

      </div>

      {/* Legend / Tooltips */}
      <div className="flex justify-between mt-3 text-xs font-medium text-base-content/60">
        <div className="flex flex-col gap-0.5">
            <span>USDC Reserve: {usdcLock}%</span>
            <span className="text-[10px] opacity-70">${usdcValue.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
        </div>
        <div className="flex flex-col gap-0.5 text-right">
            <span>BTC Vault: {btcLock}%</span>
            <span className="text-[10px] opacity-70">${btcValue.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
        </div>
      </div>
    </div>
  );
};
