'use client';

import { useEffect, useState, useRef } from 'react';
import dynamic from 'next/dynamic';
import { IndicatorPanel } from '@/components/IndicatorPanel';
import { PositionsTable } from '@/components/PositionsTable';
import { LogPanel } from '@/components/LogPanel';
import { Zap } from 'lucide-react';

const TradingViewChart = dynamic(
  () => import('@/components/charts/TradingViewChart').then((mod) => mod.TradingViewChart),
  { ssr: false }
);

export default function DashboardPage() {
  const [summary, setSummary] = useState<any>(null);
  const [bags, setBags] = useState<any>(null);
  const [candles, setCandles] = useState<any[]>([]);
  const [trades, setTrades] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('1h');
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    
    const fetchData = async () => {
      try {
        const [resSummary, resBags, resCandles, resTrades] = await Promise.all([
          fetch('http://localhost:8000/api/v2/portfolio/summary'),
          fetch('http://localhost:8000/api/v2/portfolio/bags'),
          fetch(`http://localhost:8000/api/v2/market/candles?timeframe=${timeframe}`),
          fetch('http://localhost:8000/api/v2/market/trades')
        ]);
        
        if (resSummary.ok && resBags.ok && resCandles.ok && resTrades.ok) {
            const s = await resSummary.json();
            const b = await resBags.json();
            const c = await resCandles.json();
            const t = await resTrades.json();
            
            if (mounted.current) {
                setSummary(s);
                setBags(b);
                setCandles(c);
                setTrades(t);
            }
        }
      } catch (e) {
        console.error("Failed to fetch dashboard data", e);
      } finally {
        if (mounted.current) setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // Slower updates for candles
    
    return () => {
      mounted.current = false;
      clearInterval(interval);
    };
  }, [timeframe]);

  if (loading || !summary || !bags) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-32 bg-base-200 rounded-xl w-full"></div>
        <div className="grid grid-cols-2 gap-6">
            <div className="h-40 bg-base-200 rounded-xl"></div>
            <div className="h-40 bg-base-200 rounded-xl"></div>
        </div>
        <div className="grid grid-cols-3 gap-6 h-[300px]">
            <div className="col-span-2 bg-base-200 rounded-xl"></div>
            <div className="bg-base-200 rounded-xl"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* KPI Header (The Vitals) */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Total Equity */}
        <div className="card bg-base-100 shadow-sm border border-base-200">
            <div className="card-body p-4">
                <div className="text-xs font-bold opacity-50 uppercase">Total Equity</div>
                <div className="text-2xl font-black tracking-tight">
                    ${summary.total_equity.toLocaleString(undefined, {minimumFractionDigits: 2})}
                </div>
            </div>
        </div>
        
        {/* 24h PnL (Mocked for now as 0, backend needs to provide this) */}
        <div className="card bg-base-100 shadow-sm border border-base-200">
            <div className="card-body p-4">
                <div className="text-xs font-bold opacity-50 uppercase">24h PnL</div>
                <div className="text-2xl font-bold font-mono text-base-content opacity-50">
                    $0.00 <span className="text-xs font-normal">(0.00%)</span>
                </div>
            </div>
        </div>

        {/* Active Strategy */}
        <div className="card bg-base-100 shadow-sm border border-base-200 md:col-span-2">
            <div className="card-body p-4 flex flex-row items-center justify-between">
                <div>
                    <div className="text-xs font-bold opacity-50 uppercase">Active Strategy</div>
                    <div className="text-lg font-bold flex items-center gap-2">
                        <Zap className="w-4 h-4 text-warning" />
                        {bags.active_strategy}
                    </div>
                </div>
                <div className="text-right">
                     <div className="text-xs font-bold opacity-50 uppercase">Exposure</div>
                     <div className="font-mono font-bold">{summary.crypto_pct}%</div>
                </div>
            </div>
        </div>
      </div>

      {/* Main Cockpit Area */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 h-[500px]">
        {/* Main Chart (The Battlefield) */}
        <div className="lg:col-span-3 card bg-base-100 shadow-sm border border-base-200 h-full overflow-hidden flex flex-col">
            <div className="p-2 border-b border-base-200 flex justify-between items-center bg-base-100 z-10">
                 <div className="flex items-center gap-2 px-2">
                    <span className="font-bold text-sm">BTC/USDT</span>
                    <span className="badge badge-xs badge-success animate-pulse">LIVE</span>
                 </div>
                 <div className="flex gap-1">
                    {(['15m', '1h', '4h', '1d'] as const).map((tf) => (
                        <button
                            key={tf}
                            onClick={() => setTimeframe(tf)}
                            className={`btn btn-xs ${timeframe === tf ? 'btn-primary' : 'btn-ghost'}`}
                        >
                            {tf}
                        </button>
                    ))}
                 </div>
            </div>
            <div className="flex-1 w-full min-h-0 relative">
                <TradingViewChart 
                    candles={candles} 
                    markers={trades} 
                    height={450}
                    onLoadMore={async (startTime) => {
                        console.log("Loading more history before:", startTime);
                        try {
                            const secondsPerCandle = {
                                '15m': 900, '1h': 3600, '4h': 14400, '1d': 86400, '1w': 604800, '1M': 2592000
                            }[timeframe] || 3600;
                            
                            const limit = 1000;
                            const rangeSeconds = limit * secondsPerCandle;
                            const fetchStartTime = startTime - rangeSeconds;

                            const res = await fetch(`http://localhost:8000/api/v2/market/candles?timeframe=${timeframe}&start=${fetchStartTime}&end=${startTime - 1}`);
                            if (res.ok) {
                                const newCandles = await res.json();
                                if (newCandles.length > 0) {
                                    setCandles(prev => [...newCandles, ...prev]);
                                }
                            }
                        } catch (e) {
                            console.error("Failed to load more history", e);
                        }
                    }}
                />
            </div>
        </div>

        {/* Right Column: Indicators & Logs */}
        <div className="lg:col-span-1 flex flex-col gap-4 h-full">
            {/* Indicator Panel (The Brain) */}
            <div className="h-1/3">
                <IndicatorPanel strategy={bags.active_strategy} />
            </div>
            
            {/* Logs (The Voice) */}
            <div className="h-2/3">
                <LogPanel />
            </div>
        </div>
      </div>

      {/* Bottom Row: Positions (The Bag) */}
      <div className="card bg-base-100 shadow-sm border border-base-200">
        <div className="card-body p-4">
            <h3 className="font-bold text-sm uppercase opacity-70 mb-2">Active Positions</h3>
            <PositionsTable positions={bags.positions} />
        </div>
      </div>
    </div>
  );
}
