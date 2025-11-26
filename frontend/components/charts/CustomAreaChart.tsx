import React from 'react';

interface AreaDataPoint {
  label: string;
  series1: number; // Bottom layer (e.g. Stable)
  series2: number; // Middle layer (e.g. Short Term)
  series3: number; // Top layer (e.g. Long Term)
}

interface StackedAreaChartProps {
  data: AreaDataPoint[];
  height?: number;
  colors?: string[];
}

export const CustomStackedAreaChart: React.FC<StackedAreaChartProps> = ({
  data,
  height = 250,
  colors = ['#3b82f6', '#f59e0b', '#a855f7'] // Blue, Orange, Purple
}) => {
  if (!data || data.length === 0) return null;

  const padding = { top: 10, right: 0, bottom: 20, left: 0 };
  const width = 800;
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Assuming percentage data (0-100)
  const minVal = 0;
  const maxVal = 100;
  const range = 100;

  const getX = (index: number) => padding.left + (index / (data.length - 1)) * chartWidth;
  const getY = (val: number) => padding.top + chartHeight - ((val - minVal) / range) * chartHeight;

  // Create paths for stacked areas
  // Layer 1: 0 to series1
  // Layer 2: series1 to series1+series2
  // Layer 3: series1+series2 to 100 (or total)
  
  // Actually, better to draw from top to bottom to handle overlapping if needed, 
  // but for stacked area we usually draw shapes.
  
  // Shape 1 (Bottom - Stable): Points from (x, 0) to (x, s1)
  const createAreaPath = (lowerValues: number[], upperValues: number[]) => {
    let path = `M ${getX(0)} ${getY(lowerValues[0])}`;
    
    // Top line (forward)
    for (let i = 0; i < data.length; i++) {
      path += ` L ${getX(i)} ${getY(upperValues[i])}`;
    }
    
    // Right edge down
    path += ` L ${getX(data.length - 1)} ${getY(lowerValues[data.length - 1])}`;
    
    // Bottom line (backward)
    for (let i = data.length - 1; i >= 0; i--) {
      path += ` L ${getX(i)} ${getY(lowerValues[i])}`;
    }
    
    path += ' Z';
    return path;
  };

  const zeros = data.map(() => 0);
  const s1 = data.map(d => d.series1);
  const s1s2 = data.map(d => d.series1 + d.series2);
  const total = data.map(d => d.series1 + d.series2 + d.series3); // Should be ~100

  const area1 = createAreaPath(zeros, s1);
  const area2 = createAreaPath(s1, s1s2);
  const area3 = createAreaPath(s1s2, total);

  // Generate X Axis Labels
  const xLabels = data.filter((_, i) => i % Math.ceil(data.length / 6) === 0);

  return (
    <div className="w-full h-full">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full overflow-visible">
        {/* Areas */}
        <path d={area1} fill={colors[0]} opacity="0.8" />
        <path d={area2} fill={colors[1]} opacity="0.8" />
        <path d={area3} fill={colors[2]} opacity="0.8" />

        {/* X Axis Labels */}
        {xLabels.map((d, i) => {
            const index = data.indexOf(d);
            return (
                <text
                key={i}
                x={getX(index)}
                y={height - 5}
                textAnchor="middle"
                className="text-[10px] fill-base-content/60"
                >
                {d.label}
                </text>
            )
        })}
      </svg>
    </div>
  );
};
