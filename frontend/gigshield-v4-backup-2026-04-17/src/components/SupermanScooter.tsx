export function SupermanScooter({ className = "w-[280px]" }: { className?: string }) {
  return (
    <div className={className}>
      <svg width="280" height="170" viewBox="0 0 280 170" fill="none" xmlns="http://www.w3.org/2000/svg">
        <style>{`
          #back-wheel { animation: wheelSpin 0.4s linear infinite; transform-origin: 58px 130px; }
          #front-wheel { animation: wheelSpin 0.4s linear infinite; transform-origin: 222px 130px; }
          @keyframes wheelSpin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        `}</style>

        {/* Delivery box */}
        <rect x="12" y="55" width="68" height="58" rx="5" fill="#f97316" stroke="#c2410c" strokeWidth="2"/>
        <line x1="12" y1="84" x2="80" y2="84" stroke="#c2410c" strokeWidth="1.5"/>
        <line x1="46" y1="55" x2="46" y2="113" stroke="#c2410c" strokeWidth="1.5"/>
        <text x="20" y="76" fill="white" fontSize="8" fontWeight="bold" fontFamily="sans-serif">GIG</text>
        <text x="16" y="100" fill="white" fontSize="6" fontFamily="sans-serif">SHIELD</text>

        {/* Scooter chassis */}
        <path d="M58 118 L100 106 L178 106 L212 116 L222 116" stroke="#374151" strokeWidth="4" fill="none" strokeLinecap="round"/>
        <rect x="88" y="98" width="118" height="22" rx="10" fill="#f97316"/>
        <rect x="98" y="88" width="72" height="16" rx="8" fill="#1f2937"/>
        <rect x="98" y="116" width="82" height="6" rx="3" fill="#ea580c"/>

        {/* Handlebar */}
        <path d="M183 108 L188 70 L180 68" stroke="#374151" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M173 66 L204 66" stroke="#374151" strokeWidth="5" strokeLinecap="round"/>
        <circle cx="173" cy="66" r="4" fill="#6b7280"/>
        <circle cx="204" cy="66" r="4" fill="#6b7280"/>

        {/* Headlight */}
        <circle cx="213" cy="107" r="8" fill="#fef08a" stroke="#d97706" strokeWidth="1.5"/>
        <path d="M220 102 L258 92 L258 122 L220 112 Z" fill="#fef08a" opacity="0.25"/>

        {/* Rider legs */}
        <path d="M148 94 L140 118 L156 118" fill="#1e1b4b" stroke="#1e1b4b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M173 94 L178 118 L164 118" fill="#1e1b4b" stroke="#1e1b4b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>

        {/* Rider body */}
        <rect x="147" y="60" width="32" height="38" rx="7" fill="#ef4444"/>

        {/* Rider arm forward */}
        <path d="M175 70 L196 65" stroke="#ef4444" strokeWidth="11" strokeLinecap="round"/>
        <circle cx="198" cy="64" r="6" fill="#fbbf24"/>

        {/* Rider arm back */}
        <path d="M149 72 L134 78" stroke="#ef4444" strokeWidth="9" strokeLinecap="round"/>

        {/* Head */}
        <circle cx="163" cy="48" r="17" fill="#fbbf24"/>
        {/* Helmet dome */}
        <path d="M146 47 A17 19 0 0 1 180 47 Z" fill="#ef4444"/>
        {/* Helmet stripe */}
        <path d="M146 50 L180 50" stroke="#dc2626" strokeWidth="3" strokeLinecap="round"/>
        {/* Visor accent */}
        <path d="M177 42 L182 54" stroke="#dc2626" strokeWidth="4" strokeLinecap="round"/>
        {/* Face */}
        <circle cx="170" cy="53" r="2.5" fill="#92400e"/>
        <path d="M157 56 Q163 60 169 56" stroke="#92400e" strokeWidth="1.5" fill="none" strokeLinecap="round"/>

        {/* Speed lines */}
        <line x1="8" y1="108" x2="0" y2="108" stroke="white" strokeWidth="1.5" opacity="0.5"/>
        <line x1="12" y1="118" x2="1" y2="118" stroke="white" strokeWidth="1" opacity="0.35"/>
        <line x1="8" y1="128" x2="0" y2="128" stroke="white" strokeWidth="1.5" opacity="0.5"/>

        {/* Back wheel */}
        <g id="back-wheel">
          <circle cx="58" cy="130" r="26" fill="#111827"/>
          <circle cx="58" cy="130" r="19" fill="#374151"/>
          <circle cx="58" cy="130" r="8" fill="#6b7280"/>
          <circle cx="58" cy="130" r="3" fill="#9ca3af"/>
          <line x1="58" y1="104" x2="58" y2="156" stroke="#111827" strokeWidth="3"/>
          <line x1="32" y1="130" x2="84" y2="130" stroke="#111827" strokeWidth="3"/>
          <line x1="39" y1="111" x2="77" y2="149" stroke="#111827" strokeWidth="2.5"/>
          <line x1="77" y1="111" x2="39" y2="149" stroke="#111827" strokeWidth="2.5"/>
        </g>

        {/* Front wheel */}
        <g id="front-wheel">
          <circle cx="222" cy="130" r="26" fill="#111827"/>
          <circle cx="222" cy="130" r="19" fill="#374151"/>
          <circle cx="222" cy="130" r="8" fill="#6b7280"/>
          <circle cx="222" cy="130" r="3" fill="#9ca3af"/>
          <line x1="222" y1="104" x2="222" y2="156" stroke="#111827" strokeWidth="3"/>
          <line x1="196" y1="130" x2="248" y2="130" stroke="#111827" strokeWidth="3"/>
          <line x1="203" y1="111" x2="241" y2="149" stroke="#111827" strokeWidth="2.5"/>
          <line x1="241" y1="111" x2="203" y2="149" stroke="#111827" strokeWidth="2.5"/>
        </g>
      </svg>
    </div>
  );
}
