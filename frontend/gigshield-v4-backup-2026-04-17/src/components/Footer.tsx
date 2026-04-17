import Link from 'next/link';

export function Footer() {
  return (
    <footer className="border-t border-white/10 py-8 mt-12 relative z-50" style={{ background: 'rgba(31,36,46,0.95)' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row sm:justify-between text-white/60 gap-4">
        <div className="text-left">
          <p className="font-black text-white/80 mb-1 text-lg tracking-tight">TriggerPe</p>
          <p className="text-sm text-white/50 mb-1">When it triggers, you get paid.</p>
          <p className="text-sm">Zero-touch parametric insurance for delivery partners in India.</p>
          <p className="text-xs text-white/30 mt-3">© {new Date().getFullYear()} TriggerPe. All rights reserved.</p>
        </div>
        <div className="text-sm flex flex-col gap-2">
          <Link href="/admin" className="text-white/30 hover:text-white/60 transition-colors">Admin Panel</Link>
          <span className="text-white/20 text-xs">Built for Guidewire DEVTrails 2026</span>
        </div>
      </div>
    </footer>
  );
}
