export function RunningDeliveryMan({ className = "w-[280px]" }: { className?: string }) {
  return (
    <div className={className}>
      <svg viewBox="0 0 200 320" className="w-full h-full drop-shadow-xl" xmlns="http://www.w3.org/2000/svg">
        {/* Big delivery box */}
        <rect x="18" y="58" width="72" height="92" rx="5" fill="#0ea5e9" stroke="#0284c7" strokeWidth="2"/>
        <line x1="18" y1="104" x2="90" y2="104" stroke="#0369a1" strokeWidth="1.5"/>
        <line x1="54" y1="58" x2="54" y2="150" stroke="#0369a1" strokeWidth="1.5"/>
        <rect x="22" y="68" width="28" height="14" rx="3" fill="#0284c7" opacity="0.7"/>
        <text x="24" y="79" fill="white" fontSize="7.5" fontWeight="bold" fontFamily="sans-serif">GIG</text>
        <text x="20" y="95" fill="white" fontSize="6.5" fontFamily="sans-serif">SHIELD</text>
        <text x="30" y="108" fill="#bae6fd" fontSize="6" fontFamily="sans-serif">AI</text>

        {/* Box shoulder straps */}
        <path d="M90 68 C108 62 114 76 110 90" stroke="#374151" strokeWidth="6" strokeLinecap="round" fill="none"/>
        <path d="M90 82 C104 76 107 90 103 102" stroke="#4b5563" strokeWidth="4" strokeLinecap="round" fill="none"/>

        {/* Neck */}
        <rect x="101" y="116" width="14" height="14" rx="4" fill="#fbbf24"/>

        {/* Head */}
        <circle cx="108" cy="97" r="22" fill="#fbbf24"/>
        <circle cx="86" cy="99" r="5.5" fill="#f59e0b"/>
        <circle cx="130" cy="99" r="5.5" fill="#f59e0b"/>

        {/* Cap */}
        <path d="M86 88 A22 22 0 0 1 130 88 Z" fill="#ef4444"/>
        <rect x="82" y="86" width="52" height="7" rx="3.5" fill="#dc2626"/>
        <path d="M82 91 L66 91 Q63 97 70 98 L82 95 Z" fill="#dc2626"/>

        {/* Face */}
        <circle cx="102" cy="101" r="3" fill="#92400e"/>
        <circle cx="116" cy="101" r="3" fill="#92400e"/>
        <path d="M101 111 Q108 117 115 111" stroke="#92400e" strokeWidth="2" fill="none" strokeLinecap="round"/>
        <circle cx="104" cy="96" r="1.5" fill="white" opacity="0.7"/>
        <circle cx="118" cy="96" r="1.5" fill="white" opacity="0.7"/>

        {/* Body */}
        <rect x="83" y="128" width="50" height="65" rx="9" fill="#ef4444"/>
        {/* GS logo on shirt */}
        <circle cx="108" cy="154" r="13" fill="#dc2626"/>
        <text x="101" y="158" fill="white" fontSize="9" fontWeight="bold" fontFamily="sans-serif">GS</text>

        {/* Right arm (holding phone) */}
        <path d="M133 138 C152 132 160 146 157 160" stroke="#ef4444" strokeWidth="14" strokeLinecap="round" fill="none"/>
        <rect x="150" y="156" width="14" height="23" rx="3" fill="#111827"/>
        <rect x="152" y="159" width="10" height="16" rx="2" fill="#60a5fa"/>
        <circle cx="157" cy="177" r="2" fill="#374151"/>

        {/* Left arm (thumbs up) */}
        <path d="M83 138 C66 128 60 115 67 105" stroke="#ef4444" strokeWidth="14" strokeLinecap="round" fill="none"/>
        <circle cx="68" cy="103" r="9" fill="#fbbf24"/>
        <path d="M63 97 L65 91 L71 91 L71 97 Z" fill="#fbbf24"/>
        <path d="M62 99 L62 107 L74 107 L74 99 Z" fill="#fbbf24"/>

        {/* Belt */}
        <rect x="81" y="191" width="54" height="8" rx="3" fill="#374151"/>
        <rect x="104" y="192" width="8" height="6" rx="1.5" fill="#d97706"/>

        {/* Pants */}
        <rect x="83" y="196" width="50" height="60" rx="5" fill="#1e1b4b"/>

        {/* Left leg */}
        <path d="M86 252 L82 294" stroke="#1e1b4b" strokeWidth="22" strokeLinecap="round"/>
        <ellipse cx="78" cy="298" rx="17" ry="9" fill="#111827"/>
        <ellipse cx="74" cy="296" rx="11" ry="5.5" fill="#374151"/>

        {/* Right leg */}
        <path d="M114 252 L118 294" stroke="#1e1b4b" strokeWidth="22" strokeLinecap="round"/>
        <ellipse cx="122" cy="298" rx="17" ry="9" fill="#111827"/>
        <ellipse cx="118" cy="296" rx="11" ry="5.5" fill="#374151"/>
      </svg>
    </div>
  );
}
