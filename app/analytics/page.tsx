'use client';

import { useEffect, useState, useRef } from 'react';
import { CustomLineChart } from '@/components/charts/CustomLineChart';
import { CustomStackedAreaChart } from '@/components/charts/CustomAreaChart';

interface EquityData {
  series: Array<{date: string; equity: number; benchmark: number; dca_benchmark?: number}>;
}

interface CompositionData {
  series: Array<{date: string; stable: number; short_term: number; long_term: number}>;
}

interface ShortTermPerf {
  pnl_history: Array<{date: string; pnl: number}>;
  total_pnl: number;
}

interface LongTermPerf {
  growth_history: Array<{date: string; btc: number}>;
  total_accumulated: number;
}

export default function AnalyticsPage() {
  const [equityData, setEquityData] = useState<EquityData | null>(null);
  const [compositionData, setCompositionData] = useState<CompositionData | null>(null);
  const [shortTermPerf, setShortTermPerf] = useState<ShortTermPerf | null>(null);
  const [longTermPerf, setLongTermPerf] = useState<LongTermPerf | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    
    const fetchData = async () => {
      try {
        const [resEquity, resComp, resShort, resLong] = await Promise.all([
          fetch('http://localhost:8000/api/v2/analytics/equity-curve'),
          fetch('http://localhost:8000/api/v2/analytics/composition'),
          fetch('http://localhost:8000/api/v2/analytics/performance/short-term'),
          fetch('http://localhost:8000/api/v2/analytics/performance/long-term')
        ]);
        
        if (!resEquity.ok || !resComp.ok || !resShort.ok || !resLong.ok) {
          throw new Error('One or more API requests failed');
        }
        
        const equity = await resEquity.json();
        const comp = await resComp.json();
        const short = await resShort.json();
        const long = await resLong.json();
        
        if (mounted.current) {
          setEquityData(equity);
          setCompositionData(comp);
          setShortTermPerf(short);
          setLongTermPerf(long);
        }
      } catch (e) {
        console.error("Failed to fetch analytics data", e);
        if (mounted.current) {
          setError(e instanceof Error ? e.message : 'Unknown error');
        }
      } finally {
        if (mounted.current) {
          setLoading(false);
        }
      }
    };

    fetchData();
    
    return () => {
      mounted.current = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center">
          <span className="loading loading-spinner loading-lg"></span>
          <p className="mt-4 text-base-content/70">Loading Analytics...</p>
        </div>
      </div>
    );
  }

  if (error) return <div className="alert alert-error">Error: {error}</div>;
  if (!equityData || !compositionData || !shortTermPerf || !longTermPerf) return null;

  // Prepare Data for Charts
  const equityChartData = equityData.series.map(d => ({
    label: new Date(d.date).toLocaleDateString('en-US', { month: 'short' }),
    value: d.equity,
    value2: d.benchmark,
    value3: d.dca_benchmark
  }));

  const compositionChartData = compositionData.series.map(d => ({
    label: new Date(d.date).toLocaleDateString('en-US', { month: 'short' }),
    series1: d.stable,
    series2: d.short_term,
    series3: d.long_term
  }));

  const shortTermData = shortTermPerf.pnl_history.map(d => ({
    label: new Date(d.date).toLocaleDateString('en-US', { month: 'short' }),
    value: d.pnl
  }));

  const longTermData = longTermPerf.growth_history.map(d => ({
    label: new Date(d.date).toLocaleDateString('en-US', { month: 'short' }),
    value: d.btc
  }));

  const latestEquity = equityData.series[equityData.series.length - 1];
  const startEquity = equityData.series[0];
  const totalReturn = ((latestEquity.equity - startEquity.equity) / startEquity.equity) * 100;
  const totalReturnUsd = latestEquity.equity - startEquity.equity;

  return (
    <div className="space-y-6">
      {/* Equity Curve */}
      <div className="card bg-base-100 shadow-sm border border-base-200">
        <div className="card-body p-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="text-sm font-bold uppercase opacity-70">TOTAL EQUITY VS. BENCHMARK</h2>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-sm">Total Return (YTD):</span>
                <span className="text-success font-bold">+{totalReturn.toFixed(1)}% (${totalReturnUsd.toLocaleString()})</span>
                <span className="text-sm opacity-70">| vs Benchmark: +4.2%</span>
              </div>
            </div>
            <div className="flex gap-4 text-xs font-bold">
               <div className="flex items-center gap-1">
                 <div className="w-3 h-1 bg-[#10b981] rounded-full"></div>
                 <span>Bot Equity</span>
               </div>
               <div className="flex items-center gap-1">
                 <div className="w-3 h-1 border-t-2 border-dotted border-gray-400"></div>
                 <span className="opacity-60">BTC Buy & Hold</span>
               </div>
               <div className="flex items-center gap-1">
                 <div className="w-3 h-1 border-t-2 border-dashed border-[#3b82f6]"></div>
                 <span className="opacity-60">BTC DCA</span>
               </div>
            </div>
          </div>
          
          <div className="h-[300px] w-full">
            <CustomLineChart 
              data={equityChartData} 
              showBenchmark={true} 
              valuePrefix="$"
              color3="#3b82f6"
            />
          </div>
        </div>
      </div>

      {/* Composition Chart */}
      <div className="card bg-base-100 shadow-sm border border-base-200">
        <div className="card-body p-6">
          <div className="flex justify-between items-start mb-4">
             <h2 className="text-sm font-bold uppercase opacity-70">HISTORICAL PORTFOLIO COMPOSITION (%)</h2>
             <div className="flex gap-4 text-xs font-bold">
               <div className="flex items-center gap-1">
                 <div className="w-3 h-3 bg-[#3b82f6] rounded-sm opacity-80"></div>
                 <span>Stablecoin Reserve</span>
               </div>
               <div className="flex items-center gap-1">
                 <div className="w-3 h-3 bg-[#f59e0b] rounded-sm opacity-80"></div>
                 <span>Short-Term Crypto</span>
               </div>
               <div className="flex items-center gap-1">
                 <div className="w-3 h-3 bg-[#a855f7] rounded-sm opacity-80"></div>
                 <span>Long-Term Crypto</span>
               </div>
            </div>
          </div>
          <div className="h-[250px] w-full">
            <CustomStackedAreaChart data={compositionChartData} />
          </div>
        </div>
      </div>

      {/* Performance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card bg-base-100 shadow-sm border border-base-200">
          <div className="card-body p-6">
             <div className="flex justify-between items-start">
                <div>
                    <h3 className="font-bold uppercase text-sm">SHORT-TERM BAG PERFORMANCE (USD P&L)</h3>
                    <div className="text-sm opacity-70">USD Profit</div>
                </div>
                <div className="text-right">
                    <div className="text-success font-bold text-xl">+${shortTermPerf.total_pnl.toLocaleString()}</div>
                    <div className="text-xs opacity-60">All-Time</div>
                </div>
             </div>
             <div className="h-[150px] mt-4">
                <CustomLineChart 
                    data={shortTermData} 
                    color1="#3b82f6" 
                    height={150}
                    valuePrefix="$"
                />
             </div>
          </div>
        </div>

        <div className="card bg-base-100 shadow-sm border border-base-200">
          <div className="card-body p-6">
             <div className="flex justify-between items-start">
                <div>
                    <h3 className="font-bold uppercase text-sm">LONG-TERM BAG GROWTH (BTC ACCUMULATED)</h3>
                    <div className="text-sm opacity-70">Total BTC Holdings</div>
                </div>
                <div className="text-right">
                    <div className="text-success font-bold text-xl">+{longTermPerf.total_accumulated} BTC</div>
                    <div className="text-xs opacity-60">Total Accumulated</div>
                </div>
             </div>
             <div className="h-[150px] mt-4">
                <CustomLineChart 
                    data={longTermData} 
                    color1="#3b82f6" 
                    stepped={true}
                    height={150}
                    valueSuffix=" BTC"
                />
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
