"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { SupermanLogo } from './SupermanLogo';
import { api, WorkerData } from '@/lib/api';

export function Navigation() {
  const pathname = usePathname();
  const isDashboard = pathname.startsWith('/dashboard');
  const workerId = isDashboard ? pathname.split('/')[2] : null;
  const [worker, setWorker] = useState<WorkerData | null>(null);

  useEffect(() => {
    if (workerId) {
      api.getWorker(workerId).then(setWorker).catch(() => {});
    }
  }, [workerId]);

  return (
    <header className="sticky top-0 z-[100] glass-card border-x-0 border-t-0 rounded-none bg-[#1F242E]/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3">
          <SupermanLogo className="h-[44px] relative flex-shrink-0 drop-shadow-lg" />
          <div className="flex flex-col leading-none">
            <span className="text-xl font-black text-gradient tracking-tight">TriggerPe</span>
            <span className="text-[10px] text-white/40 tracking-widest font-medium uppercase">Auto-Claim Insurance</span>
          </div>
        </Link>

        {isDashboard ? (
          <div className="flex items-center gap-4">
            <span className="text-white font-bold hidden sm:block text-sm">{worker ? worker.name : ''}</span>
            <Link href="/login" className="px-5 py-2 rounded-full font-semibold border border-white/30 text-white hover:bg-white/10 transition-colors text-sm">
              Logout
            </Link>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-white hover:text-blue-300 transition-colors font-semibold border border-white/20 px-5 py-2 rounded-full hover:bg-white/5 text-sm">
              Login
            </Link>
            <Link href="/register" className="px-5 py-2 rounded-full font-semibold bg-gradient-to-r from-blue-500 to-purple-500 hover:scale-105 transition-transform text-white shadow-[0_0_15px_rgba(96,165,250,0.4)] text-sm">
              Get Protected
            </Link>
          </div>
        )}
      </div>
    </header>
  );
}
