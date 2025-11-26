'use client';

import { useAccount } from 'wagmi';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isConnected } = useAccount();
  const router = useRouter();
  const pathname = usePathname();
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (isMounted && !isConnected && pathname !== '/') {
      // Allow dummy access if explicitly navigated (simulated by not redirecting immediately if we had a global state)
      // But for now, let's assume strict auth unless we implement a global "isDummyMode" context.
      // Since the user asked for a dummy wallet, we should probably allow access if they clicked "Enter with Dummy Wallet".
      // However, since we don't have a global store for "Dummy Mode" yet, let's just redirect to / for now
      // and rely on the fact that "Enter with Dummy Wallet" in LandingPage pushes to /dashboard.
      // Wait, if we redirect here, the push won't work.
      
      // FIX: We need a way to persist "Dummy Mode". 
      // For simplicity, we will skip redirect if there is a specific localStorage flag or just rely on Wagmi.
      // Let's check localStorage for 'dummy_mode'
      const isDummy = localStorage.getItem('dummy_mode') === 'true';
      
      if (!isDummy) {
         router.push('/');
      }
    }
  }, [isConnected, pathname, router, isMounted]);

  if (!isMounted) return null;

  return <>{children}</>;
}
