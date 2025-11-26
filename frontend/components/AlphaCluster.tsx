import React from 'react';

interface AlphaClusterProps {
  botPerformance?: number; // %
  benchmarkBtc?: number;   // %
  benchmarkDca?: number;   // %
}

export const AlphaCluster: React.FC<AlphaClusterProps> = ({
  botPerformance = 0,
  benchmarkBtc = 0,
  benchmarkDca = 0,
}) => {
  // Find max absolute value to scale bars
  const maxValue = Math.max(
    Math.abs(botPerformance),
    Math.abs(benchmarkBtc),
    Math.abs(benchmarkDca),
    1 // Avoid division by zero
  );

  const getWidth = (val: number) => `${(Math.abs(val) / maxValue) * 100}%`;

  const renderBar = (label: string, value: number, colorClass: string, icon: string) => (
    <div className="flex items-center gap-2 mb-2 last:mb-0">
      <div className="w-8 text-lg text-center">{icon}</div>
      <div className="flex-1">
        <div className="flex justify-between text-xs font-bold mb-0.5">
          <span className="opacity-70">{label}</span>
          <span className={value >= 0 ? 'text-success' : 'text-error'}>
            {value > 0 ? '+' : ''}{value.toFixed(2)}%
          </span>
        </div>
        <div className="h-2 bg-base-300 rounded-full overflow-hidden flex">
            {/* Negative part (if needed, simplified for now to just 0-100 positive visual) */}
            {/* Real implementation would center 0 if we expect negatives often, 
                but for "Race Bars" usually we just show magnitude or simple progress. 
                Let's do simple left-aligned bars for now. */}
            <div 
                className={`h-full rounded-full ${colorClass}`} 
                style={{ width: getWidth(value) }}
            ></div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="card bg-base-100 shadow-sm border border-base-200">
      <div className="card-body p-4">
        <h3 className="text-xs font-bold uppercase opacity-50 mb-3">Alpha Cluster</h3>
        
        {renderBar('BOT', botPerformance, 'bg-success', '🤖')}
        {renderBar('Buy & Hold', benchmarkBtc, 'bg-base-content/30', '💰')}
        {renderBar('DCA Strategy', benchmarkDca, 'bg-info', '📅')}
        
        <div className="mt-2 text-[10px] text-center opacity-40">
            Relative Performance (Since Session Start)
        </div>
      </div>
    </div>
  );
};
