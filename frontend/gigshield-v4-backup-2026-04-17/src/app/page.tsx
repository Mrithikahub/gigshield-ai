"use client";

import Link from 'next/link';
import Image from 'next/image';
import { useEffect, useState, useRef } from 'react';

function CountUp({ end, suffix = '', prefix = '' }: { end: number; suffix?: string; prefix?: string }) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        let start = 0;
        const t = setInterval(() => {
          start += Math.ceil(end / 50);
          if (start > end) start = end;
          setCount(start);
          if (start === end) clearInterval(t);
        }, 30);
        observer.disconnect();
      }
    }, { threshold: 0.1 });
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [end]);
  return <span ref={ref}>{prefix}{count.toLocaleString()}{suffix}</span>;
}

export default function Home() {
  const [scooterErr, setScooterErr] = useState(false);
  const [activeCard, setActiveCard] = useState<string | null>(null);

  const rainDrops = Array.from({ length: 100 }).map((_, i) => ({
    id: i,
    left: `${(i * 1.39) % 100}vw`,
    delay: `${(i * 0.43) % 3}s`,
    duration: `${0.55 + ((i * 0.17) % 0.45)}s`,
    width: `${1 + ((i * 37) % 100) / 100}px`,
    height: `${15 + Math.floor((i * 17) % 15)}px`,
  }));

  return (
    <div className="flex flex-col w-full" style={{ background: 'linear-gradient(180deg, #000080 0%, #3034D9 25%, #B8E3E9 55%, #B298E7 80%, #000080 100%)' }}>

      {/* ── HERO ── */}
      <section className="relative w-full min-h-screen overflow-hidden flex flex-col" style={{ background: 'linear-gradient(135deg, #000080 0%, #3034D9 50%, #069494 100%)' }}>

        {/* Lightning flashes */}
        <div className="absolute inset-0 bg-blue-100 pointer-events-none z-[1]" style={{ animation: 'screenFlash 7s infinite', opacity: 0 }} />
        <div className="absolute inset-0 bg-blue-100 pointer-events-none z-[1]" style={{ animation: 'screenFlash2 11s infinite', opacity: 0 }} />

        {/* Bolt 1 */}
        <div className="absolute top-10 right-[10%] w-40 h-52 pointer-events-none z-[5]" style={{ animation: 'boltFlash1 7s infinite', opacity: 0 }}>
          <svg viewBox="0 0 80 140" className="w-full h-full" style={{ filter: 'drop-shadow(0 0 10px #93c5fd) drop-shadow(0 0 30px white)' }}>
            <path d="M50 0 L10 65 L40 65 L25 140 L80 48 L48 48 Z" fill="white" />
          </svg>
        </div>
        {/* Bolt 2 */}
        <div className="absolute top-20 left-[8%] w-24 h-36 pointer-events-none z-[5]" style={{ animation: 'boltFlash2 11s infinite', opacity: 0 }}>
          <svg viewBox="0 0 60 110" className="w-full h-full" style={{ filter: 'drop-shadow(0 0 8px #93c5fd) drop-shadow(0 0 20px white)' }}>
            <path d="M38 0 L8 50 L30 50 L20 110 L60 38 L36 38 Z" fill="white" />
          </svg>
        </div>

        {/* Rain */}
        <div className="absolute inset-0 z-[2] pointer-events-none">
          {rainDrops.map((drop) => (
            <div key={drop.id} className="absolute top-0 animate-rainFall"
              style={{ left: drop.left, animationDelay: drop.delay, animationDuration: drop.duration, width: drop.width, height: drop.height, background: 'rgba(147,197,253,0.55)', filter: 'blur(0.5px)', borderRadius: '0 0 2px 2px', transform: 'rotate(-12deg)' }} />
          ))}
        </div>

        {/* ── HERO CONTENT — centered, all text above scooter ── */}
        <div className="relative z-[30] flex flex-col items-center text-center px-4 pt-28 pb-12 flex-1">
          <span className="text-xs font-bold bg-blue-500/15 border border-blue-500/25 px-4 py-1.5 rounded-full tracking-widest uppercase mb-6" style={{ color: '#16C3C6' }}>
            India's First Zero-Touch Parametric Insurance
          </span>

          <h1 className="text-5xl md:text-7xl font-black mb-4 text-gradient leading-tight tracking-tight">
            TriggerPe
          </h1>
          <p className="text-2xl md:text-3xl text-white font-bold mb-3">
            When storms stop you, we pay you instantly
          </p>
          <p className="text-base md:text-lg text-white/60 mb-10 max-w-2xl">
            Auto-claim parametric insurance for Swiggy, Zomato & Blinkit delivery partners.<br className="hidden md:block" />
            Rain triggers. Heat triggers. You get paid automatically. No forms. No waiting.
          </p>

          {/* Buttons — clearly below text, above the scooter */}
          <div className="flex flex-col sm:flex-row items-center gap-4 mb-16 z-[30]">
            <Link href="/register"
              className="px-8 py-4 rounded-full font-bold text-lg hover:scale-105 transition-transform text-white shadow-[0_0_25px_rgba(47,126,227,0.5)]"
              style={{ background: 'linear-gradient(135deg, #2F7EE3, #3034D9)' }}>
              Get Protected Now →
            </Link>
            <Link href="#how-it-works"
              className="px-8 py-4 rounded-full font-bold text-lg border-2 border-white/30 text-white hover:bg-white/10 transition-all">
              See How It Works
            </Link>
          </div>

          {/* Quick badges */}
          <div className="flex flex-wrap gap-3 justify-center">
            {['✓ Zero Forms', '✓ Auto Payout', '✓ 5 Triggers', '✓ Fraud Protected'].map(b => (
              <span key={b} className="text-xs font-bold text-green-400 bg-green-500/10 border border-green-500/20 px-3 py-1 rounded-full">{b}</span>
            ))}
          </div>
        </div>

        {/* ── Scooter at bottom (decorative) — BELOW all content ── */}
        <div className="relative w-full h-[160px] overflow-hidden pointer-events-none z-[10] flex-shrink-0">
          {/* Road line */}
          <div className="absolute bottom-0 w-full h-[3px] bg-white/10" />
          {/* Animated scooter */}
          <div className="absolute bottom-4 left-0 w-full" style={{ animation: 'slowRide 16s linear infinite' }}>
            {!scooterErr ? (
              <div className="relative w-[220px] h-[130px]">
                <Image src="/delivery-scooter.png" alt="Delivery Partner" fill
                  className="object-contain drop-shadow-[0_4px_20px_rgba(249,115,22,0.5)]"
                  onError={() => setScooterErr(true)} />
              </div>
            ) : (
              /* Fallback SVG scooter if image missing */
              <ScooterSVG />
            )}
          </div>
        </div>
      </section>

      {/* ── STATS ── */}
      <section className="py-16 px-4" style={{ background: 'linear-gradient(135deg, #B8E3E9 0%, #FCE883 50%, #B298E7 100%)' }}>
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { icon: '🛡️', value: <CountUp end={2847} />, label: 'Delivery Partners Protected', val: '#000080', accent: '#069494' },
            { icon: '₹',  value: <><CountUp end={12} />+ Lakhs</>,  label: 'Auto-Paid to Workers',       val: '#000080', accent: '#FF8243' },
            { icon: '⚡', value: <><CountUp end={99} />% Uptime</>, label: 'Always Monitoring',           val: '#000080', accent: '#069494' },
          ].map((s, i) => (
            <div key={i} className="p-8 flex items-center gap-4 group rounded-[2rem] shadow-xl hover:scale-[1.02] transition-all"
              style={{ background: 'rgba(255,255,255,0.82)', border: '1px solid rgba(0,0,128,0.12)', backdropFilter: 'blur(12px)' }}>
              <div className="w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0 text-2xl group-hover:scale-110 transition-transform"
                style={{ background: `${s.accent}20` }}>{s.icon}</div>
              <div>
                <h3 className="text-3xl font-black mb-0.5" style={{ color: s.val }}>{s.value}</h3>
                <p className="text-sm font-medium" style={{ color: s.accent }}>{s.label}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section id="how-it-works" className="py-24 px-4 max-w-6xl mx-auto w-full" style={{ background: 'transparent' }}>
        <h2 className="text-4xl font-black text-center mb-4 text-gradient">How It Works</h2>
        <p className="text-center text-sm mb-16 max-w-xl mx-auto" style={{ color: '#718096' }}>Three simple steps — register once, get paid automatically every time weather disrupts your work.</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 relative items-start">
          <div className="hidden md:block absolute top-[56px] left-[16%] right-[16%] h-[2px] z-0"
            style={{ background: 'linear-gradient(90deg, #069494, #B298E7, #069494)', opacity: 0.5 }} />
          {[
            { step: 1, icon: '📝', title: 'Register in 2 min',  desc: 'Sign up, choose your platform and city. Policy activates instantly after payment.',          color: '#069494' },
            { step: 2, icon: '🛡️', title: 'We Monitor 24/7',   desc: 'Our AI watches live weather, AQI, wind speed for your city every single hour.',               color: '#B298E7' },
            { step: 3, icon: '💰', title: 'Auto Payout',        desc: 'When triggers fire, claims are created and payout transfers to your UPI instantly.',           color: '#FF8243' },
          ].map((s) => (
            <div key={s.step} className="p-8 relative flex flex-col items-center text-center z-10 hover:-translate-y-2 transition-transform rounded-[1.5rem]"
              style={{ background: 'rgba(255,255,255,0.82)', border: `1.5px solid ${s.color}30`, backdropFilter: 'blur(12px)', boxShadow: `0 4px 24px ${s.color}15` }}>
              <div className="absolute -top-6 w-12 h-12 rounded-full flex items-center justify-center font-black text-xl text-white ring-4 ring-white"
                style={{ background: s.color }}>{s.step}</div>
              <div className="w-20 h-20 rounded-2xl flex items-center justify-center mb-5 mt-4 text-4xl"
                style={{ background: `${s.color}15` }}>{s.icon}</div>
              <h3 className="text-lg font-black mb-2" style={{ color: '#000080' }}>{s.title}</h3>
              <p className="text-sm leading-relaxed" style={{ color: '#718096' }}>{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── COVERAGE TRIGGERS ── */}
      <section className="py-20 px-4 max-w-6xl mx-auto w-full">
        <h2 className="text-4xl font-black text-center mb-4 text-gradient">What We Cover</h2>
        <p className="text-center text-sm mb-14 max-w-lg mx-auto" style={{ color: '#718096' }}>5 parametric triggers — when conditions cross the threshold, your claim fires automatically.</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            { emoji: '🌧️', title: 'Heavy Rain',      desc: 'Rainfall > 50mm',     payout: '₹800', color: '#2F7EE3' },
            { emoji: '🔥', title: 'Extreme Heat',     desc: 'Temperature > 42°C',  payout: '₹600', color: '#FF8243' },
            { emoji: '💨', title: 'High AQI',         desc: 'Air Quality > 300',   payout: '₹600', color: '#069494' },
            { emoji: '🌊', title: 'Flood Alert',      desc: 'Rainfall > 100mm',    payout: '₹800', color: '#3034D9' },
            { emoji: '🌬️', title: 'Strong Wind',     desc: 'Wind > 45 km/h',      payout: '₹480', color: '#7B5EA7' },
            { emoji: '🚨', title: 'Curfew / Strike',  desc: 'Official shutdown',   payout: '₹800', color: '#ef4444' },
          ].map((t) => {
            const isActive = activeCard === t.title;
            return (
              <div key={t.title}
                className="p-6 flex flex-col items-center text-center transition-all hover:scale-[1.03] cursor-pointer rounded-2xl select-none"
                style={{
                  background: isActive ? `${t.color}18` : 'rgba(255,255,255,0.88)',
                  border: `2px solid ${isActive ? t.color : `${t.color}35`}`,
                  boxShadow: isActive ? `0 8px 32px ${t.color}40` : '0 2px 12px rgba(0,0,0,0.08)',
                  backdropFilter: 'blur(12px)',
                }}
                onClick={() => setActiveCard(isActive ? null : t.title)}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.borderColor = t.color;
                  (e.currentTarget as HTMLElement).style.boxShadow = `0 8px 28px ${t.color}35`;
                  (e.currentTarget as HTMLElement).style.background = `${t.color}12`;
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    (e.currentTarget as HTMLElement).style.borderColor = `${t.color}35`;
                    (e.currentTarget as HTMLElement).style.boxShadow = '0 2px 12px rgba(0,0,0,0.08)';
                    (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.88)';
                  }
                }}>
                <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4 text-4xl"
                  style={{ background: `${t.color}18`, border: `2px solid ${t.color}40` }}>
                  {t.emoji}
                </div>
                <h3 className="text-lg font-black mb-1" style={{ color: '#000080' }}>{t.title}</h3>
                <p className="text-xs mb-5" style={{ color: '#4a5568' }}>{t.desc}</p>
                <div className="mt-auto px-5 py-2 rounded-full font-black text-sm text-white"
                  style={{ background: t.color }}>
                  {t.payout} Payout
                </div>
                {isActive && <p className="text-xs mt-3 font-bold" style={{ color: t.color }}>✓ Auto-claim fires when threshold crossed</p>}
              </div>
            );
          })}
        </div>
      </section>

      {/* ── FLOOD WAVES ── */}
      <section className="relative w-full overflow-hidden flex items-start justify-center pt-14"
        style={{ height: '380px', background: 'linear-gradient(180deg, #000080 0%, #3034D9 100%)' }}>
        <h2 className="relative z-10 text-3xl md:text-4xl font-black text-white text-center px-4 max-w-3xl drop-shadow-md leading-tight">
          Floods, Storms, Extreme Heat —<br />All Covered Automatically
        </h2>
        {/* Ripples */}
        {[{ l: '15%', b: '95px', delay: '0s' }, { l: '15%', b: '95px', delay: '0.9s' }, { r: '18%', b: '105px', delay: '0.4s' }, { r: '18%', b: '105px', delay: '1.3s' }].map((r, i) => (
          <div key={i} className="absolute w-20 h-20 rounded-full border-2 border-blue-400/25 pointer-events-none z-[5]"
            style={{ bottom: r.b, left: (r as {l?:string}).l, right: (r as {r?:string}).r, animation: `rippleOut 2.2s ease-out ${r.delay} infinite` }} />
        ))}
        {/* Scooter riding through flood */}
        <div className="absolute bottom-[54px] left-0 pointer-events-none z-[8]" style={{ animation: 'floodRide 14s linear infinite' }}>
          {!scooterErr ? (
            <div className="relative w-[200px] h-[120px]">
              <Image src="/delivery-scooter.png" alt="" fill className="object-contain drop-shadow-[0_2px_12px_rgba(59,130,246,0.6)]" onError={() => setScooterErr(true)} />
            </div>
          ) : <ScooterSVG />}
        </div>
        {/* 3 wave layers */}
        <div className="absolute bottom-0 left-0 w-[200%] h-full pointer-events-none z-0">
          <div className="absolute bottom-0 w-full h-[55%] animate-wave1">
            <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="w-full h-full fill-[#1e3a8a]">
              <path d="M0,40 C200,120 400,0 600,40 C800,80 1000,-20 1200,40 L1200,120 L0,120 Z" />
            </svg>
          </div>
          <div className="absolute bottom-0 w-full h-[44%] animate-wave2">
            <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="w-full h-full fill-[#1d4ed8]">
              <path d="M0,20 C300,-60 600,100 900,20 C1050,-20 1150,60 1200,20 L1200,120 L0,120 Z" />
            </svg>
          </div>
          <div className="absolute bottom-0 w-full h-[34%] animate-wave3">
            <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="w-full h-full fill-[#3b82f6]">
              <path d="M0,60 C150,120 350,0 600,60 C850,120 1050,20 1200,60 L1200,120 L0,120 Z" />
            </svg>
          </div>
        </div>
      </section>

    </div>
  );
}

/* Clean fallback scooter SVG */
function ScooterSVG() {
  return (
    <svg width="200" height="120" viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg">
      {/* Body */}
      <ellipse cx="100" cy="75" rx="70" ry="18" fill="#f97316" />
      <rect x="50" y="58" width="100" height="20" rx="10" fill="#f97316" />
      {/* Seat */}
      <rect x="75" y="48" width="45" height="12" rx="6" fill="#1f2937" />
      {/* Handlebar */}
      <rect x="135" y="38" width="4" height="22" rx="2" fill="#374151" />
      <rect x="128" y="38" width="18" height="4" rx="2" fill="#374151" />
      {/* Headlight */}
      <circle cx="153" cy="68" r="7" fill="#fef08a" />
      {/* Delivery box */}
      <rect x="30" y="38" width="40" height="32" rx="4" fill="#ea580c" />
      <line x1="50" y1="38" x2="50" y2="70" stroke="#c2410c" strokeWidth="1.5" />
      {/* Rider body */}
      <rect x="88" y="30" width="22" height="28" rx="6" fill="#ef4444" />
      {/* Head */}
      <circle cx="99" cy="22" r="12" fill="#fbbf24" />
      <path d="M87 20 A12 13 0 0 1 111 20 Z" fill="#dc2626" />
      {/* Back wheel */}
      <g style={{ animation: 'wheelSpin 0.4s linear infinite', transformOrigin: '40px 88px' }}>
        <circle cx="40" cy="88" r="18" fill="#111827" />
        <circle cx="40" cy="88" r="10" fill="#374151" />
        <circle cx="40" cy="88" r="3" fill="#9ca3af" />
        <line x1="40" y1="70" x2="40" y2="106" stroke="#1f2937" strokeWidth="2.5" />
        <line x1="22" y1="88" x2="58" y2="88" stroke="#1f2937" strokeWidth="2.5" />
      </g>
      {/* Front wheel */}
      <g style={{ animation: 'wheelSpin 0.4s linear infinite', transformOrigin: '160px 88px' }}>
        <circle cx="160" cy="88" r="18" fill="#111827" />
        <circle cx="160" cy="88" r="10" fill="#374151" />
        <circle cx="160" cy="88" r="3" fill="#9ca3af" />
        <line x1="160" y1="70" x2="160" y2="106" stroke="#1f2937" strokeWidth="2.5" />
        <line x1="142" y1="88" x2="178" y2="88" stroke="#1f2937" strokeWidth="2.5" />
      </g>
      {/* Speed lines */}
      <line x1="14" y1="72" x2="0" y2="72" stroke="rgba(255,255,255,0.4)" strokeWidth="1.5" />
      <line x1="10" y1="82" x2="0" y2="82" stroke="rgba(255,255,255,0.25)" strokeWidth="1" />
    </svg>
  );
}
