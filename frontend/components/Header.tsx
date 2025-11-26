'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { HealthIndicator } from './HealthIndicator';
import { useState, useEffect } from 'react';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { LayoutDashboard, LineChart } from 'lucide-react';

export function Header() {
  const pathname = usePathname();
  const [isRunning, setIsRunning] = useState(true); // Default to ON for visual match

  const toggleBot = async () => {
    try {
      const endpoint = isRunning ? 'stop' : 'start';
      const res = await fetch(`http://localhost:8000/api/v2/${endpoint}`, { method: 'POST' });
      const data = await res.json();
      // Backend returns { status: "running" | "stopped" } usually, or we check success
      if (endpoint === 'start') {
          setIsRunning(true);
      } else {
          setIsRunning(false);
      }
    } catch (e) {
      console.error("Failed to toggle bot", e);
      // Optimistic toggle for now if backend fails
      setIsRunning(!isRunning);
    }
  };

  const handlePanic = async () => {
      if (!confirm("⚠️ EMERGENCY: Are you sure you want to STOP the bot and CLOSE ALL positions?")) return;
      
      try {
          const res = await fetch('http://localhost:8000/api/v2/panic', { method: 'POST' });
          if (res.ok) {
              setIsRunning(false);
              alert("🚨 PANIC MODE ACTIVATED: Bot stopped and positions closing.");
          }
      } catch (e) {
          console.error("Panic failed", e);
          alert("Failed to execute Panic Mode. Check console.");
      }
  };

  useEffect(() => {
      // Check initial status
      fetch('http://localhost:8000/api/v2/status')
          .then(res => res.json())
          .then(data => {
              if (data.status === 'running') setIsRunning(true);
              else setIsRunning(false);
          })
          .catch(e => console.error("Failed to fetch status", e));
  }, []);

  return (
    <div className="navbar bg-base-100 px-6 h-20 border-b border-base-200/50">
      <div className="flex-1 flex items-center gap-8">
        {/* Logo */}
        <Link href="/dashboard" className="text-xl font-black tracking-tight flex items-center gap-2 hover:opacity-80 transition-opacity">
          Hyperliquid Bot <span className="text-2xl">🤖</span>
        </Link>
        
        {/* Navigation */}
        <div className="flex items-center gap-1">
          <Link 
            href="/dashboard" 
            className={`btn btn-sm border-0 font-bold gap-2 ${pathname === '/dashboard' ? 'btn-ghost bg-base-200/50 text-base-content' : 'btn-ghost text-base-content/60'}`}
          >
            <LayoutDashboard className="w-4 h-4" />
            Cockpit
          </Link>
          <Link 
            href="/analytics" 
            className={`btn btn-sm border-0 font-bold gap-2 ${pathname === '/analytics' ? 'btn-ghost bg-base-200/50 text-base-content' : 'btn-ghost text-base-content/60'}`}
          >
            <LineChart className="w-4 h-4" />
            Analytics
          </Link>
        </div>
      </div>
      
      <div className="flex-none flex items-center gap-6">
        {/* Panic Button */}
        <button onClick={handlePanic} className="btn btn-error btn-sm font-bold text-white animate-pulse">
            🚨 PANIC
        </button>

        {/* Status Toggle */}
        <div className="flex items-center gap-3">
          <span className={`text-xs font-bold uppercase tracking-wide ${isRunning ? 'text-success' : 'text-base-content/50'}`}>
            Status: {isRunning ? 'ON' : 'OFF'}
          </span>
          <input 
            type="checkbox" 
            className="toggle toggle-success toggle-md border-2" 
            checked={isRunning} 
            onChange={toggleBot}
          />
        </div>
        
        {/* Separator */}
        <div className="h-6 w-px bg-base-200"></div>

        {/* Health Indicator */}
        <HealthIndicator />
        
        {/* Wallet */}
        <ConnectButton showBalance={false} accountStatus="address" chainStatus="none" />
      </div>
    </div>
  );
}
