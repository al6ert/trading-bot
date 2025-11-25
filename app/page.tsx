'use client';

import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useAccount } from 'wagmi';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Wallet } from 'lucide-react';

export default function LandingPage() {
  const { isConnected } = useAccount();
  const router = useRouter();
  const [isMounted, setIsMounted] = useState(false);

  // Prevent hydration mismatch
  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (isConnected) {
      router.push('/dashboard');
    }
  }, [isConnected, router]);

  if (!isMounted) return null;

  return (
    <div className="min-h-screen bg-base-200 flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 rounded-full blur-[100px]"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary/20 rounded-full blur-[100px]"></div>
      </div>

      <div className="card bg-base-100 shadow-2xl border border-base-200 max-w-md w-full z-10">
        <div className="card-body items-center text-center py-12">
          <div className="w-16 h-16 bg-base-200 rounded-full flex items-center justify-center mb-6">
            <span className="text-4xl">🤖</span>
          </div>
          
          <h1 className="text-3xl font-bold mb-2">Hyperliquid Bot</h1>
          <p className="text-base-content/60 mb-8">
            Professional Trading Cockpit & Analytics Suite
          </p>

          <div className="flex flex-col gap-4 w-full max-w-xs">
            <div className="flex justify-center">
              <ConnectButton label="Connect Wallet" />
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-8 text-xs text-base-content/40 font-mono">
        v2.0.0 | System Status: Online
      </div>
    </div>
  );
}
