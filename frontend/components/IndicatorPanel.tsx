import React from 'react';
import { Activity, TrendingUp, Minus } from 'lucide-react';

interface IndicatorPanelProps {
  strategy: string;
}

export const IndicatorPanel: React.FC<IndicatorPanelProps> = ({ strategy }) => {
  // Simple logic to determine visual state based on strategy string
  // In a real app, we would parse ADX values from the backend
  const isTrend = strategy?.toLowerCase().includes('trend');
  const isRange = strategy?.toLowerCase().includes('range') || strategy?.toLowerCase().includes('sideways');
  
  return (
    <div className="card bg-base-100 shadow-sm border border-base-200 h-full">
      <div className="card-body p-4">
        <h3 className="font-bold text-sm flex items-center gap-2 uppercase opacity-70 mb-2">
          <Activity className="w-4 h-4" /> Market Regime
        </h3>
        
        <div className="flex flex-col items-center justify-center h-full gap-2">
            {isTrend && (
                <>
                    <div className="p-3 bg-success/10 rounded-full text-success animate-pulse">
                        <TrendingUp className="w-8 h-8" />
                    </div>
                    <div className="text-center">
                        <div className="font-bold text-lg text-success">TRENDING</div>
                        <div className="text-xs opacity-50">Strong Momentum</div>
                    </div>
                </>
            )}
            
            {isRange && (
                <>
                    <div className="p-3 bg-base-300 rounded-full text-base-content opacity-50">
                        <Minus className="w-8 h-8" />
                    </div>
                    <div className="text-center">
                        <div className="font-bold text-lg text-base-content opacity-70">RANGING</div>
                        <div className="text-xs opacity-50">Low Volatility</div>
                    </div>
                </>
            )}
            
            {!isTrend && !isRange && (
                <div className="text-center opacity-50">
                    <div className="font-bold">WAITING</div>
                    <div className="text-xs">Analyzing Market...</div>
                </div>
            )}
        </div>
      </div>
    </div>
  );
};
