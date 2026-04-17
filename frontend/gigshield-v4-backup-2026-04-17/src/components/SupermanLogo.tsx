export function SupermanLogo({ className = "h-[44px]" }: { className?: string }) {
  return (
    <svg viewBox="0 0 100 100" className={className} xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="cape2" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#ef4444" />
          <stop offset="100%" stopColor="#991b1b" />
        </linearGradient>
      </defs>
      {/* Flowing Cape (to the right) */}
      <path d="M50 40 Q80 30 95 65 Q60 85 55 60 Z" fill="url(#cape2)" className="animate-capeFly" style={{ transformOrigin: '50px 40px' }} />
      {/* Suit Main (Yellow body) */}
      <path d="M45 40 Q30 30 25 40 L30 85 L60 85 Z" fill="#facc15" />
      
      {/* Face/Head (Skin color) */}
      <circle cx="40" cy="25" r="12" fill="#fcd34d" />
      {/* Hair */}
      <path d="M50 20 Q40 10 30 20 L28 25 Q35 15 50 25 Z" fill="#111827" />
      
      {/* Shield on Chest */}
      <path d="M35 45 L50 45 L50 55 Q45 70 35 65 Q30 70 30 55 L30 45 Z" fill="#ffffff" stroke="#ef4444" strokeWidth="2" />
      <text x="40" y="58" fill="#3b82f6" fontSize="14" fontWeight="bold" textAnchor="middle" fontFamily="sans-serif">G</text>
      
      {/* Heroic Arm Raised up left */}
      <path d="M25 40 Q10 30 5 15 L15 10 Q30 25 30 35 Z" fill="#facc15" />
      <circle cx="10" cy="15" r="8" fill="#111827" />
    </svg>
  );
}
