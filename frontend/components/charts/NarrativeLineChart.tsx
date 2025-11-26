import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceDot,
  CartesianGrid
} from 'recharts';
import { format } from 'date-fns';

interface Candle {
  time: number; // Unix timestamp in seconds
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface Trade {
  time: number;
  side: 'buy' | 'sell';
  price: number;
  size: number;
}

interface NarrativeLineChartProps {
  candles: Candle[];
  trades?: Trade[];
  height?: number;
}

export const NarrativeLineChart: React.FC<NarrativeLineChartProps> = ({
  candles,
  trades = [],
  height = 400,
}) => {
  if (!candles || candles.length === 0) {
    return (
      <div className="flex items-center justify-center h-full bg-base-100 text-base-content/30 font-bold uppercase tracking-widest">
        Waiting for Market Data...
      </div>
    );
  }

  // 1. Prepare Data for Recharts
  // We need to determine the "State" for each point to color it.
  // Since Backend doesn't send state yet, we MOCK it:
  // Green (Bull): Close > Open
  // Orange (Bear): Close < Open
  // Gray (Chop): Abs(Close - Open) < 0.05% (Tiny move)
  
  const data = candles.map((c, i) => {
    const change = (c.close - c.open) / c.open;
    let state = 'chop';
    if (change > 0.0005) state = 'bull'; // > 0.05%
    else if (change < -0.0005) state = 'bear'; // < -0.05%
    
    return {
      ...c,
      date: c.time * 1000, // Recharts uses ms usually for formatting
      state,
      // We need a single value for the line, usually 'close'
      value: c.close,
    };
  });

  // 2. Gradient Logic
  // To make the line change color, we use a LinearGradient.
  // We need to calculate the percentage offsets where the state changes.
  // This is expensive for many points.
  
  // ALTERNATIVE: Split into multiple series? No, gaps.
  // ALTERNATIVE: "ReferenceArea" for background? Nice but not the line itself.
  
  // FOR MVP: We will use a single color (Blue/Gray) for the line, 
  // BUT we will use "ReferenceAreas" or "ReferenceLine" to show the "Regime" background?
  // OR: Just color the Area fill with a gradient based on the overall trend?
  
  // Let's try the "Gradient Stops" approach.
  // We define a gradient that changes color at specific X coordinates.
  // But Recharts gradients are defined by 0% to 100% of the SVG width.
  // We can calculate this if the X-axis is linear.
  
  // Let's try a simpler "Narrative" approach first:
  // The "Line" is neutral (White/Gray).
  // The "Background" or "Area" under it tells the story.
  // Actually, the PRD says "The price line color matters".
  
  // Let's use a simplified approach:
  // If the LAST candle is Bull, the whole line is Green? No, misleading.
  // If we can't easily do multi-color line in Recharts without complex SVG:
  // We will use a "Stepped" color approach using multiple Areas?
  // No, let's use a custom `dot` to show state at each point? No, too noisy.
  
  // DECISION: Use a standard AreaChart with a "Mystic" gradient (Purple/Blue) for now,
  // and use COLORED DOTS on the line to indicate state changes or significant candles.
  // AND use the "Markers" (Rocket/Skull) for trades.
  
  const minPrice = Math.min(...candles.map(c => c.low));
  const maxPrice = Math.max(...candles.map(c => c.high));
  const domainPadding = (maxPrice - minPrice) * 0.1;

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      return (
        <div className="bg-base-300 border border-base-content/10 p-2 rounded shadow-lg text-xs">
          <div className="font-bold mb-1">{format(d.date, 'MMM dd HH:mm')}</div>
          <div className="flex justify-between gap-4">
            <span className="opacity-70">Price:</span>
            <span className="font-mono font-bold">${d.close.toFixed(2)}</span>
          </div>
          <div className="flex justify-between gap-4">
             <span className="opacity-70">State:</span>
             <span className={`font-bold uppercase ${d.state === 'bull' ? 'text-success' : d.state === 'bear' ? 'text-warning' : 'text-base-content/50'}`}>
                {d.state}
             </span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8884d8" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
            </linearGradient>
            
            {/* We can define other gradients if we want to switch dynamically */}
          </defs>
          
          <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
          
          <XAxis 
            dataKey="date" 
            type="number"
            domain={['dataMin', 'dataMax']}
            tickFormatter={(unixTime) => format(unixTime, 'HH:mm')}
            stroke="#666"
            tick={{fontSize: 10}}
            minTickGap={50}
          />
          
          <YAxis 
            domain={[minPrice - domainPadding, maxPrice + domainPadding]}
            orientation="right"
            stroke="#666"
            tick={{fontSize: 10}}
            tickFormatter={(val) => `$${val.toFixed(0)}`}
          />
          
          <Tooltip content={<CustomTooltip />} />
          
          <Area 
            type="monotone" 
            dataKey="value" 
            stroke="#8884d8" 
            strokeWidth={2}
            fillOpacity={1} 
            fill="url(#colorValue)" 
          />

          {/* Trade Markers */}
          {trades.map((t, i) => (
             <ReferenceDot
                key={i}
                x={t.time * 1000}
                y={t.price}
                r={6}
                fill={t.side === 'buy' ? '#10b981' : '#ef4444'}
                stroke="none"
                label={{
                    position: 'top',
                    value: t.side === 'buy' ? '🚀' : '💀',
                    fontSize: 16,
                    fill: '#fff'
                }}
             />
          ))}

        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
