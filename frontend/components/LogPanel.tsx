import React, { useEffect, useState, useRef } from 'react';
import { ScrollText, Terminal, AlertTriangle, CheckCircle, Activity } from 'lucide-react';

interface LogEntry {
  time: string;
  type: 'SYS' | 'RISK' | 'TRADE' | 'STRAT' | 'ERROR';
  message: string;
}

export const LogPanel = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filter, setFilter] = useState<string>('ALL');
  const [autoScroll, setAutoScroll] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);

  const fetchLogs = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/v2/logs?limit=50&type=${filter}`);
      if (res.ok) {
        const data = await res.json();
        setLogs(data);
      }
    } catch (e) {
      console.error("Failed to fetch logs", e);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 2000);
    return () => clearInterval(interval);
  }, [filter]);

  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const getLogIcon = (type: string) => {
    switch (type) {
      case 'TRADE': return <div className="w-2 h-2 rounded-full bg-success animate-pulse"></div>;
      case 'RISK': return <span className="text-warning text-[10px] font-bold">| RISK |</span>;
      case 'ERROR': return <span className="text-error text-[10px] font-bold">| ERR |</span>;
      case 'STRAT': return <span className="text-info text-[10px] font-bold">| STRAT |</span>;
      default: return <span className="opacity-50 text-[10px] font-bold">| SYS |</span>;
    }
  };

  return (
    <div className="card bg-base-100 shadow-sm border border-base-200 h-full flex flex-col">
      <div className="card-body p-4 flex flex-col h-full">
        <div className="flex justify-between items-center mb-2">
          <h3 className="font-bold text-sm">Bot Controls & Logs</h3>
        </div>
        
        <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-bold opacity-70">Auto-Confirm Trades</span>
            <input type="checkbox" className="toggle toggle-sm" />
        </div>

        {/* Filters */}
        <div className="flex gap-2 mb-2 text-[10px] font-bold uppercase">
          {['ALL', 'TRADE', 'ERROR'].map(f => (
            <button 
              key={f}
              onClick={() => setFilter(f)}
              className={`hover:opacity-100 ${filter === f ? 'opacity-100 underline' : 'opacity-40'}`}
            >
              [{f}]
            </button>
          ))}
        </div>

        {/* Log Area */}
        <div 
          ref={scrollRef}
          className="flex-1 bg-base-200/50 rounded border border-base-300 overflow-y-auto p-2 font-mono text-[10px] leading-relaxed"
          onScroll={(e) => {
            const target = e.target as HTMLDivElement;
            const isBottom = target.scrollHeight - target.scrollTop === target.clientHeight;
            setAutoScroll(isBottom);
          }}
        >
          {logs.map((log, idx) => (
            <div key={idx} className="mb-1 break-words">
              <span className="opacity-40 mr-1">
                [{new Date(log.time).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}]
              </span>
              <span className="mr-1">{getLogIcon(log.type)}</span>
              <span className={log.type === 'TRADE' ? 'font-bold' : 'opacity-80'}>
                {log.message}
              </span>
            </div>
          ))}
          {logs.length === 0 && (
            <div className="text-center opacity-30 mt-10">No logs available</div>
          )}
        </div>
      </div>
    </div>
  );
};
