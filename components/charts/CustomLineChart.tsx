import React from 'react';

interface DataPoint {
  label: string;
  value: number;
  value2?: number; // For benchmark or second line
  value3?: number; // For DCA or third line
}

interface LineChartProps {
  data: DataPoint[];
  height?: number;
  color1?: string;
  color2?: string;
  color3?: string;
  showBenchmark?: boolean;
  stepped?: boolean;
  valuePrefix?: string;
  valueSuffix?: string;
}

export const CustomLineChart: React.FC<LineChartProps> = ({
  data,
  height = 300,
  color1 = '#10b981', // Green default (Bot)
  color2 = '#9ca3af', // Grey default (Benchmark)
  color3 = '#3b82f6', // Blue default (DCA)
  showBenchmark = false,
  stepped = false,
  valuePrefix = '',
  valueSuffix = ''
}) => {
  if (!data || data.length === 0) return null;

  const padding = { top: 20, right: 20, bottom: 30, left: 50 };
  const width = 800; // SVG internal coordinate system width
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Calculate Min/Max
  const allValues = data.flatMap(d => {
      const vals = [d.value];
      if (showBenchmark && d.value2 !== undefined) vals.push(d.value2);
      if (showBenchmark && d.value3 !== undefined) vals.push(d.value3);
      return vals;
  });
  
  const minVal = Math.min(...allValues);
  const maxVal = Math.max(...allValues);
  const range = maxVal - minVal || 1;

  // Scaling functions
  const getX = (index: number) => padding.left + (index / (data.length - 1)) * chartWidth;
  const getY = (val: number) => padding.top + chartHeight - ((val - minVal) / range) * chartHeight;

  // Generate Paths
  const createPath = (values: number[], isStepped: boolean) => {
    return values.map((val, i) => {
      const x = getX(i);
      const y = getY(val);
      if (i === 0) return `M ${x} ${y}`;
      if (isStepped) {
        const prevX = getX(i - 1);
        return `L ${x} ${getY(values[i-1])} L ${x} ${y}`;
      }
      return `L ${x} ${y}`;
    }).join(' ');
  };

  const line1Path = createPath(data.map(d => d.value), stepped);
  const line2Path = showBenchmark ? createPath(data.map(d => d.value2 || 0), false) : '';
  const line3Path = showBenchmark && data.some(d => d.value3 !== undefined) ? createPath(data.map(d => d.value3 || 0), false) : '';

  // Generate X Axis Labels (show ~6 labels)
  const xLabels = data.filter((_, i) => i % Math.ceil(data.length / 6) === 0);

  // Generate Y Axis Labels (5 ticks)
  const yTicks = Array.from({ length: 5 }, (_, i) => minVal + (range * i) / 4);

  return (
    <div className="w-full h-full">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full overflow-visible">
        {/* Grid Lines */}
        {yTicks.map((tick, i) => (
          <g key={i}>
            <line
              x1={padding.left}
              y1={getY(tick)}
              x2={width - padding.right}
              y2={getY(tick)}
              stroke="#e5e7eb"
              strokeWidth="1"
              strokeDasharray="4 4"
            />
            <text
              x={padding.left - 10}
              y={getY(tick) + 4}
              textAnchor="end"
              className="text-[10px] fill-base-content/60"
            >
              {valuePrefix}{tick.toLocaleString(undefined, { maximumFractionDigits: 2, notation: "compact" })}{valueSuffix}
            </text>
          </g>
        ))}

        {/* Benchmark Line (Dotted) - Value 2 */}
        {showBenchmark && line2Path && (
          <path
            d={line2Path}
            fill="none"
            stroke={color2}
            strokeWidth="2"
            strokeDasharray="5 5"
          />
        )}

        {/* DCA Line (Dashed) - Value 3 */}
        {showBenchmark && line3Path && (
          <path
            d={line3Path}
            fill="none"
            stroke={color3}
            strokeWidth="2"
            strokeDasharray="2 2"
          />
        )}

        {/* Main Line */}
        <path
          d={line1Path}
          fill="none"
          stroke={color1}
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

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
