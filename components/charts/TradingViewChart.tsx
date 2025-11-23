'use client';

import React, { useEffect, useRef } from 'react';

interface CandleData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

interface TradeMarker {
  time: number;
  position: 'aboveBar' | 'belowBar' | 'inBar';
  color: string;
  shape: 'circle' | 'square' | 'arrowUp' | 'arrowDown';
  text: string;
}

interface TradingViewChartProps {
  candles: CandleData[];
  markers?: TradeMarker[];
  height?: number;
  onLoadMore?: (startTime: number) => void;
}

export const TradingViewChart: React.FC<TradingViewChartProps> = ({ 
  candles, 
  markers = [], 
  height = 300,
  onLoadMore
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const seriesRef = useRef<any>(null);
  const [isLibraryLoaded, setIsLibraryLoaded] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const loadingMoreRef = useRef(false);

  // 1. Initialize Chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    let chart: any;
    let resizeObserver: ResizeObserver;

    const initChart = async () => {
      try {
        const { createChart, ColorType, CrosshairMode } = await import('lightweight-charts');
        setIsLibraryLoaded(true);

        if (!chartContainerRef.current) return;

        // Clear any existing content
        chartContainerRef.current.innerHTML = '';

        chart = createChart(chartContainerRef.current, {
          layout: {
            background: { type: ColorType.Solid, color: 'transparent' },
            textColor: '#6b7280', // gray-500
          },
          width: chartContainerRef.current.clientWidth,
          height: height,
          grid: {
            vertLines: { color: '#e5e7eb' }, // gray-200
            horzLines: { color: '#e5e7eb' },
          },
          timeScale: {
            timeVisible: true,
            secondsVisible: false,
            borderColor: '#e5e7eb',
          },
          rightPriceScale: {
            borderColor: '#e5e7eb',
          },
          handleScroll: {
            mouseWheel: true,
            pressedMouseMove: true,
            horzTouchDrag: true,
            vertTouchDrag: true,
          },
          handleScale: {
            axisPressedMouseMove: true,
            mouseWheel: true,
            pinch: true,
          },
          crosshair: {
            mode: 1, // CrosshairMode.Normal
          },
        });

        const candlestickSeries = chart.addCandlestickSeries({
          upColor: '#10b981', // success/green
          downColor: '#ef4444', // error/red
          borderVisible: false,
          wickUpColor: '#10b981',
          wickDownColor: '#ef4444',
        });

        seriesRef.current = candlestickSeries;
        chartRef.current = chart;

        // Initial data set
        if (candles && candles.length > 0) {
            candlestickSeries.setData(candles);
            chart.timeScale().fitContent();
        }

        if (markers && markers.length > 0) {
          candlestickSeries.setMarkers(markers as any);
        }

        // Infinite Scroll Logic
        chart.timeScale().subscribeVisibleLogicalRangeChange((newVisibleLogicalRange: any) => {
            if (loadingMoreRef.current) return;
            
            const logicalRange = chart.timeScale().getVisibleLogicalRange();
            if (logicalRange && logicalRange.from < 10) { // Near the beginning
                // Trigger load more
                if (onLoadMore && candles.length > 0) {
                    const oldestCandleTime = candles[0].time;
                    loadingMoreRef.current = true;
                    onLoadMore(oldestCandleTime);
                    
                    // Reset loading flag after a delay (simple debounce/cooldown)
                    setTimeout(() => {
                        loadingMoreRef.current = false;
                    }, 1000);
                }
            }
        });

        // Resize Observer
        resizeObserver = new ResizeObserver((entries) => {
            if (entries.length === 0 || !entries[0].contentRect) return;
            const newRect = entries[0].contentRect;
            chart.applyOptions({ width: newRect.width, height: newRect.height });
        });
        
        resizeObserver.observe(chartContainerRef.current);

      } catch (err) {
        console.error("Failed to load lightweight-charts", err);
        setError("Failed to load chart library");
      }
    };

    initChart();

    return () => {
      if (resizeObserver) resizeObserver.disconnect();
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
        seriesRef.current = null;
      }
    };
  }, [height]); // Only re-init if height changes

  // 2. Update Data
  useEffect(() => {
    if (seriesRef.current && candles && candles.length > 0) {
        try {
            // Ensure candles are sorted by time (required by library)
            // This is a safety check in case the merge logic produced unsorted data
            const sortedCandles = [...candles].sort((a, b) => a.time - b.time);
            
            // Remove duplicates if any
            const uniqueCandles = sortedCandles.filter((candle, index, self) => 
                index === 0 || candle.time !== self[index - 1].time
            );

            // Capture current visible time range to preserve scroll position
            const chart = chartRef.current;
            const visibleRange = chart ? chart.timeScale().getVisibleRange() : null;
            
            seriesRef.current.setData(uniqueCandles);
            
            // Restore visible range if it existed (and we are not in the initial load)
            if (visibleRange && loadingMoreRef.current) {
                 chart.timeScale().setVisibleRange(visibleRange);
            }
        } catch (err) {
            console.error("Error updating chart data:", err);
        } finally {
            loadingMoreRef.current = false;
        }
    }
  }, [candles]);

  // 3. Update Markers
  useEffect(() => {
      if (seriesRef.current && markers) {
          seriesRef.current.setMarkers(markers as any);
      }
  }, [markers]);

  return (
    <div className="relative w-full h-full min-h-[300px]">
        {!isLibraryLoaded && !error && (
            <div className="absolute inset-0 flex items-center justify-center bg-base-100 z-10">
                <span className="loading loading-spinner loading-md"></span>
            </div>
        )}
        {error && (
            <div className="absolute inset-0 flex items-center justify-center bg-base-100 z-10 text-error">
                {error}
            </div>
        )}
        <div ref={chartContainerRef} className="w-full h-full" />
    </div>
  );
};
