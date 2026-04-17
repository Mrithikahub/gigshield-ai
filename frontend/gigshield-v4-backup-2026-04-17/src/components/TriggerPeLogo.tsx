export function TriggerPeLogo({ className = "h-[44px]" }: { className?: string }) {
  return (
    <svg viewBox="0 0 100 100" className={className} xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="tpGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#60a5fa" />
          <stop offset="100%" stopColor="#a78bfa" />
        </linearGradient>
        <linearGradient id="tpBolt" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#fde68a" />
          <stop offset="100%" stopColor="#f59e0b" />
        </linearGradient>
      </defs>
      {/* Circle background */}
      <circle cx="50" cy="50" r="46" fill="url(#tpGrad)" opacity="0.15" />
      <circle cx="50" cy="50" r="46" fill="none" stroke="url(#tpGrad)" strokeWidth="2.5" />
      {/* Lightning bolt */}
      <path d="M58 8 L28 52 L50 52 L42 92 L72 48 L50 48 Z" fill="url(#tpBolt)" />
      {/* T letter subtle overlay */}
      <text x="50" y="60" fill="white" fontSize="22" fontWeight="900" textAnchor="middle" fontFamily="sans-serif" opacity="0.12">T</text>
    </svg>
  );
}
