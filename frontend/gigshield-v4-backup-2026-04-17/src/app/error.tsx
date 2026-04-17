"use client";

import Link from 'next/link';
import { useEffect } from 'react';

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center px-4"
      style={{ background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 100%)' }}>
      <p className="text-6xl mb-6">⚡</p>
      <h1 className="text-3xl font-black text-white mb-3">Something went wrong</h1>
      <p className="text-white/40 text-sm mb-6 max-w-sm">
        {error.message || 'An unexpected error occurred.'}
      </p>
      <div className="flex gap-3">
        <button onClick={reset}
          className="px-6 py-2.5 rounded-full font-bold bg-blue-600 text-white hover:opacity-90 transition-all text-sm">
          Try Again
        </button>
        <Link href="/"
          className="px-6 py-2.5 rounded-full font-bold border border-white/30 text-white hover:bg-white/10 transition-all text-sm">
          Go Home
        </Link>
      </div>
    </div>
  );
}
