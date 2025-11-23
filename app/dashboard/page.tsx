'use client';

import { useEffect, useState, useRef } from 'react';
import dynamic from 'next/dynamic';
import { PortfolioProgressBar } from '@/components/PortfolioProgressBar';
import { LogPanel } from '@/components/LogPanel';
import { Zap, Landmark } from 'lucide-react';

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
    <div className="space-y-6">
      {/* Top Row: Total Portfolio Value */}
      <div className="card bg-base-100 shadow-sm border border-base-200">
        <div className="card-body p-6">
          <PortfolioProgressBar 
            totalValue={summary.total_equity}
            cryptoPct={summary.crypto_pct}
            stablePct={summary.stable_pct}
          />
        </div>
      </div>

      {/* Middle Row: Bags */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Short Term Bag */}
        <div className="card bg-base-100 shadow-sm border border-base-200">
          <div className="card-body p-5">
            <div className="flex justify-between items-start mb-4">
              <h3 className="font-bold text-sm flex items-center gap-2 uppercase">
                <Zap className="w-4 h-4 text-warning" fill="currentColor" />
                CORTO PLAZO (Trading Bag)
              </h3>
              <span className="badge badge-sm bg-base-200 border-0 text-xs font-mono opacity-70">Active: {bags.short_term.active_strategy}</span>
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="opacity-70">Valor USD:</span>
                <span className="font-bold font-mono">${bags.short_term.value_usd.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
              </div>
              <div className="flex justify-between">
                <span className="opacity-70">USDT Disp:</span>
                <span className="font-bold font-mono">${bags.short_term.available_usdt.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
              </div>
              <div className="flex justify-between">
                <span className="opacity-70">BTC Asignado:</span>
                <span className="font-bold font-mono">{bags.short_term.assigned_btc} BTC</span>
              </div>
              <div className="flex justify-between">
                <span className="opacity-70">Rendimiento 24h:</span>
                <span className={`font-bold font-mono ${bags.short_term.pnl_24h >= 0 ? 'text-success' : 'text-error'}`}>
                    {bags.short_term.pnl_24h >= 0 ? '+' : ''}${bags.short_term.pnl_24h.toLocaleString(undefined, {minimumFractionDigits: 2})}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Long Term Bag */}
        <div className="card bg-base-100 shadow-sm border border-base-200">
          <div className="card-body p-5">
            <div className="flex justify-between items-start mb-4">
              <h3 className="font-bold text-sm flex items-center gap-2 uppercase">
                <Landmark className="w-4 h-4 text-base-content" />
                LARGO PLAZO (HODL Bag)
              </h3>
              <span className="badge badge-sm bg-base-200 border-0 text-xs font-mono opacity-70">Active: {bags.long_term.active_strategy}</span>
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="opacity-70">Valor BTC Total:</span>
                <span className="font-bold font-mono text-base-content">{bags.long_term.value_btc} BTC <span className="opacity-50 text-xs">(${bags.long_term.value_usd.toLocaleString()})</span></span>
              </div>
              <div className="flex justify-between">
                <span className="opacity-70">BTC Acumulado:</span>
                <span className="font-bold font-mono">{bags.long_term.accumulated_btc} BTC</span>
              </div>
              <div className="flex justify-between">
                <span className="opacity-70">USDT Reserva:</span>
                <span className="font-bold font-mono">${bags.long_term.reserved_usdt.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
              </div>
              <div className="flex justify-between">
                <span className="opacity-70">Rendimiento Total:</span>
                <span className="font-bold font-mono text-success">+{bags.long_term.total_yield_btc} BTC</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Row: Chart & Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[400px]">
        {/* Chart */}
        <div className="lg:col-span-2 card bg-base-100 shadow-sm border border-base-200 h-full overflow-hidden">
            <div className="card-body p-4 flex flex-col h-full">
                <div className="flex justify-between items-center mb-2">
                    <h3 className="font-bold text-sm flex items-center gap-2">
                        BTC/USDT 
                        <span className="badge badge-xs badge-success">LIVE</span>
                    </h3>
                    <div className="flex gap-2">
                        {(['15m', '1h', '4h', '1d', '1w', '1M'] as const).map((tf) => (
                            <button
                                key={tf}
                                onClick={() => setTimeframe(tf)}
                                className={`btn btn-sm ${timeframe === tf ? 'btn-primary' : 'btn-ghost'}`}
                            >
                                {tf}
                            </button>
                        ))}
                    </div>
                </div>
                <div className="flex-1 w-full h-full min-h-0">
                    <TradingViewChart 
                        candles={candles} 
                        markers={trades} 
                        height={320} 
                        onLoadMore={async (startTime) => {
                            console.log("Loading more history before:", startTime);
                            try {
                                // Calculate approximate start time to fetch ~1000 candles
                                // 15m = 900s, 1h = 3600s, 4h = 14400s, 1d = 86400s, 1w = 604800s, 1M = 2592000s
                                const secondsPerCandle = {
                                    '15m': 900,
                                    '1h': 3600,
                                    '4h': 14400,
                                    '1d': 86400,
                                    '1w': 604800,
                                    '1M': 2592000
                                }[timeframe] || 3600;
                                
                                const limit = 1000;
                                const rangeSeconds = limit * secondsPerCandle;
                                const fetchStartTime = startTime - rangeSeconds;

                                const res = await fetch(`http://localhost:8000/api/v2/market/candles?timeframe=${timeframe}&start=${fetchStartTime}&end=${startTime - 1}`);
                                if (res.ok) {
                                    const newCandles = await res.json();
                                    if (newCandles.length > 0) {
                                        console.log(`Loaded ${newCandles.length} older candles`);
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
        </div>

        {/* Logs */}
        <div className="lg:col-span-1 h-full">
            <LogPanel />
        </div>
      </div>
    </div>
  );
}
