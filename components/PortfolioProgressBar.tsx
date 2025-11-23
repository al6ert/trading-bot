import React from 'react';

interface PortfolioProgressBarProps {
  totalValue: number;
  cryptoPct: number;
  stablePct: number;
}

export const PortfolioProgressBar: React.FC<PortfolioProgressBarProps> = ({
  totalValue,
  cryptoPct,
  stablePct,
}) => {
  const cryptoValue = totalValue * (cryptoPct / 100);
  const stableValue = totalValue * (stablePct / 100);

  return (
    <div className="flex flex-col w-full">
      <div className="mb-3">
        <div className="text-xs font-bold opacity-50 uppercase tracking-wider">Total Portfolio Value</div>
        <div className="text-5xl font-black tracking-tight text-base-content mt-1">
          ${totalValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="flex w-full h-3 rounded-sm overflow-hidden bg-base-200">
        <div 
          className="h-full bg-base-content" 
          style={{ width: `${cryptoPct}%` }}
        ></div>
        <div 
          className="h-full bg-base-300" 
          style={{ width: `${stablePct}%` }}
        ></div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-2 mt-2 text-xs font-medium">
        <div className="flex items-center gap-1">
          <span className="font-bold text-base-content">{cryptoPct}% Crypto</span>
          <span className="opacity-50">(${cryptoValue.toLocaleString(undefined, { maximumFractionDigits: 0 })})</span>
        </div>
        <span className="opacity-30 text-base-content">|</span>
        <div className="flex items-center gap-1">
          <span className="font-bold text-base-content">{stablePct}% Stable</span>
          <span className="opacity-50">(${stableValue.toLocaleString(undefined, { maximumFractionDigits: 0 })})</span>
        </div>
      </div>
    </div>
  );
};
