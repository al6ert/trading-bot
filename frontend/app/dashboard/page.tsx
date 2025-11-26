'use client';

import { useEffect, useState, useRef } from 'react';
import dynamic from 'next/dynamic';
import { IndicatorPanel } from '@/components/IndicatorPanel';
import { PositionsTable } from '@/components/PositionsTable';
import { LogPanel } from '@/components/LogPanel';
import { CapitalAllocationBar } from '@/components/CapitalAllocationBar';
import { AlphaCluster } from '@/components/AlphaCluster';
import { Zap } from 'lucide-react';

import { NarrativeLineChart } from '@/components/charts/NarrativeLineChart';

export default function DashboardPage() {
  const [summary, setSummary] = useState<any>(null);
  const [bags, setBags] = useState<any>(null);
  const [candles, setCandles] = useState<any[]>([]);
  const [trades, setTrades] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('1h');
  const [usdcLock, setUsdcLock] = useState(20);
  const [btcLock, setBtcLock] = useState(20);
  const mounted = useRef(true);

  // Fetch allocation locks on mount
  useEffect(() => {
    fetch('http://localhost:8000/api/v2/bot/allocation')
      .then(res => res.json())
      .then(data => {
        setUsdcLock(data.usdc_lock);
        setBtcLock(data.btc_lock);
      })
      .catch(e => console.error("Failed to fetch allocation", e));
  }, []);

  // Update allocation handler
  const handleAllocationChange = async (usdc: number, btc: number) => {
    setUsdcLock(usdc);
    setBtcLock(btc);
    
    try {
      await fetch('http://localhost:8000/api/v2/bot/allocation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ usdc_lock: usdc, btc_lock: btc })
      });
    } catch (e) {
      console.error("Failed to update allocation", e);
    }
  };

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
                <div className="text-xs font-bold opacity-50 uppercase mb-1">Total Equity</div>
                <div className="text-3xl font-black tracking-tight mb-3">
                    ${summary.total_equity.toLocaleString(undefined, {minimumFractionDigits: 2})}
                </div>
                
                {/* Breakdown - Stacked */}
                <div className="space-y-1.5 text-sm">
                    <div className="flex justify-between items-center">
                        <span className="text-success font-medium">USDC:</span>
                        <div className="text-right">
                            <span className="font-bold">${summary.available_balance.toLocaleString(undefined, {maximumFractionDigits: 0})}</span>
                            <span className="opacity-50 ml-1.5 text-xs">
                                ({((summary.available_balance / summary.total_equity) * 100).toFixed(0)}%)
                            </span>
                        </div>
                    </div>
                    <div className="flex justify-between items-center">
                        <span className="text-warning font-medium">BTC:</span>
                        <div className="text-right">
                            <span className="font-bold">
                                {(() => {
                                    // Calculate BTC amount from positions
                                    const btcPosition = bags?.positions?.find((p: any) => p.symbol === 'BTC');
                                    const btcAmount = btcPosition?.size || 0;
                                    return `${btcAmount.toFixed(6)} BTC`;
                                })()}
                            </span>
                            <span className="opacity-50 ml-1.5 text-xs">
                                (${(summary.total_equity - summary.available_balance).toLocaleString(undefined, {maximumFractionDigits: 0})})
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        
        {/* Alpha Cluster (Benchmarks) */}
        <AlphaCluster 
            botPerformance={5.2} 
            benchmarkBtc={2.1} 
            benchmarkDca={3.4} 
        />

        {/* Capital Allocation (Safety Locks) */}
        <div className="card bg-base-100 shadow-sm border border-base-200 md:col-span-2">
            <div className="card-body p-4">
                <CapitalAllocationBar 
                    totalValue={summary.total_equity} 
                    currentUsdcPct={Math.round((summary.available_balance / summary.total_equity) * 100)}
                    currentBtcPct={Math.round(((summary.total_equity - summary.available_balance) / summary.total_equity) * 100)}
                    initialUsdcLock={usdcLock}
                    initialBtcLock={btcLock}
                    onAllocationChange={handleAllocationChange}
                />
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
                <NarrativeLineChart 
                    candles={candles} 
                    trades={trades} 
                    height={450}
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
