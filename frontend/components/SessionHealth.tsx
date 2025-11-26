import React from 'react';

interface SessionHealthProps {
  winRate?: number;    // %
  maxDrawdown?: number; // %
  profitFactor?: number;
}

export const SessionHealth: React.FC<SessionHealthProps> = ({
  winRate = 0,
  maxDrawdown = 0,
  profitFactor = 0,
}) => {
  return (
    <div className="card bg-base-100 shadow-sm border border-base-200">
      <div className="card-body p-4">
        <h3 className="text-xs font-bold uppercase opacity-50 mb-3">Session Health</h3>
        
        <div className="grid grid-cols-3 gap-2 text-center">
            {/* Win Rate */}
            <div className="bg-base-200/50 rounded p-2">
                <div className="text-[10px] opacity-60 uppercase">Win Rate</div>
                <div className={`text-lg font-black ${winRate >= 50 ? 'text-success' : 'text-warning'}`}>
                    {winRate.toFixed(0)}%
                </div>
            </div>

            {/* Max Drawdown */}
            <div className="bg-base-200/50 rounded p-2">
                <div className="text-[10px] opacity-60 uppercase">Max DD</div>
                <div className="text-lg font-black text-error">
                    {maxDrawdown > 0 ? '-' : ''}{Math.abs(maxDrawdown).toFixed(2)}%
                </div>
            </div>

            {/* Profit Factor */}
            <div className="bg-base-200/50 rounded p-2">
                <div className="text-[10px] opacity-60 uppercase">Pr. Factor</div>
                <div className="text-lg font-black">
                    {profitFactor.toFixed(2)}
                </div>
            </div>
        </div>
      </div>
    </div>
  );
};
