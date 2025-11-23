'use client';

import { useEffect, useState } from 'react';

export function HealthIndicator() {
  const [latency, setLatency] = useState<number | null>(null);
  const [isHealthy, setIsHealthy] = useState(false);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const start = Date.now();
        const res = await fetch('http://localhost:8000/api/v2/status/health');
        const data = await res.json();
        const end = Date.now();
        
        if (data.status === 'healthy') {
          setIsHealthy(true);
          setLatency(end - start); // Real latency from fetch
        } else {
          setIsHealthy(false);
        }
      } catch (e) {
        setIsHealthy(false);
        setLatency(null);
      }
    };

    const interval = setInterval(checkHealth, 5000);
    checkHealth(); // Initial check
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center gap-2 px-3 py-1 bg-base-200 rounded-full text-xs font-mono">
      <div className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-success' : 'bg-error'}`} />
      <span>Data Feed: {isHealthy ? 'Healthy' : 'Disconnected'}</span>
      {latency !== null && <span className="opacity-50">({latency}ms)</span>}
    </div>
  );
}
