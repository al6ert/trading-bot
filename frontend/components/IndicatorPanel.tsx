import React from 'react';
import { SessionHealth } from './SessionHealth';

interface IndicatorPanelProps {
  strategy?: string;
}

export const IndicatorPanel: React.FC<IndicatorPanelProps> = ({ strategy }) => {
  return (
    <div className="h-full flex flex-col gap-4">
      {/* Session Health */}
      <div className="flex-1">
        <SessionHealth 
            winRate={68} 
            maxDrawdown={-1.45} 
            profitFactor={2.1} 
        />
      </div>
    </div>
  );
};
