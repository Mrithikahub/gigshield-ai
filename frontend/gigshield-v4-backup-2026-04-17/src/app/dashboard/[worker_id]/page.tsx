"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { api, WorkerData, Policy, Claim, WeatherData } from '@/lib/api';

type Section = 'dashboard' | 'policy' | 'claims' | 'weather' | 'premium' | 'settings';

const NAV_ITEMS: { icon: string; label: string; id: Section }[] = [
  { icon: '📊', label: 'Dashboard',  id: 'dashboard' },
  { icon: '🛡️', label: 'My Policy',  id: 'policy'    },
  { icon: '💰', label: 'Claims',      id: 'claims'    },
  { icon: '🌤️', label: 'Weather',    id: 'weather'   },
  { icon: '📈', label: 'Premium AI', id: 'premium'   },
  { icon: '⚙️', label: 'Settings',   id: 'settings'  },
];

interface PremiumData {
  risk_level: string;
  risk_score: number;
  risk_zone: string;
  disruption_probability: number;
  weekly_premium: number;
  coverage_per_event: number;
  monthly_estimate: number;
  breakdown: {
    base_rate: number;
    zone_surcharge: number;
    platform_loading: number;
    disruption_loading: number;
    risk_loading: number;
  };
  live_weather?: { temperature: number; rainfall: number; aqi: number; condition: string };
}

export default function Dashboard() {
  const params = useParams() as { worker_id: string };
  const [worker, setWorker] = useState<WorkerData | null>(null);
  const [policy, setPolicy] = useState<Policy | null>(null);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [premiumData, setPremiumData] = useState<PremiumData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState<Section>('dashboard');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const workerId = params.worker_id;
        
        if (!workerId || workerId === 'loading') {
          setLoading(false);
          return;
        }
        
        const [wData, pData, cData] = await Promise.all([
          api.getWorker(workerId),
          api.getPolicy(workerId),
          api.getWorkerClaims(workerId),
        ]);
        
        setWorker(wData);
        setPolicy(pData);
        setClaims(cData);
        
        const justRegistered = localStorage.getItem('triggerpe_just_registered');
        if (justRegistered) {
          localStorage.removeItem('triggerpe_just_registered');
          setClaims([]);
        }
        
        const city = wData?.city;
        if (city) {
          const weth = await api.getWeather(city);
          setWeather(weth);
        }
        
        try {
          const premRes = await fetch(`http://localhost:8000/premium/${workerId}`);
          if (premRes.ok) {
            const premData = await premRes.json();
            setPremiumData(premData);
          }
        } catch (premErr) {
          console.log('Premium fetch failed, using defaults');
        }
        
      } catch (err) {
        console.error('Failed to fetch worker data:', err);
        // Try to get from localStorage as fallback
        const savedName = localStorage.getItem('triggerpe_worker_name');
        const savedCity = localStorage.getItem('triggerpe_worker_city');
        const savedPlatform = localStorage.getItem('triggerpe_worker_platform');
        const savedEarning = localStorage.getItem('triggerpe_worker_earning');
        
        if (savedName) {
          setWorker({
            id: params.worker_id,
            worker_id: params.worker_id,
            name: savedName,
            city: savedCity || 'Chennai',
            platform: (savedPlatform as any) || 'Swiggy',
            avg_daily_earning: parseInt(savedEarning || '800'),
            risk_level: 'Medium',
            risk_score: 45,
          });
        }
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [params.worker_id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-24" style={{ background: 'linear-gradient(135deg, #B8E3E9 0%, #B298E7 100%)' }}>
        <div className="flex flex-col items-center gap-4">
          <div className="w-14 h-14 border-4 border-t-transparent rounded-full animate-spin" style={{ borderColor: '#069494', borderTopColor: 'transparent' }} />
          <p className="text-sm" style={{ color: 'rgba(0,0,128,0.6)' }}>Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (!worker) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-24" style={{ background: 'linear-gradient(135deg, #B8E3E9 0%, #B298E7 100%)' }}>
        <div className="text-center p-8 rounded-2xl" style={{ background: 'rgba(255,255,255,0.9)' }}>
          <p className="text-4xl mb-4">⚠️</p>
          <h2 className="text-xl font-bold mb-2" style={{ color: '#000080' }}>Unable to load worker data</h2>
          <p className="text-gray-500 mb-4">Please make sure you are registered properly</p>
          <a href="/register" className="px-4 py-2 rounded-lg text-white" style={{ background: '#069494' }}>Go to Registration</a>
        </div>
      </div>
    );
  }

  const w = worker;
  const p = policy ?? {
    id: 'P-DEMO', policy_id: 'P-DEMO', worker_id: w.id,
    start_date: new Date().toISOString(),
    end_date: new Date(Date.now() + 7 * 86400000).toISOString(),
    coverage_amount: 800, premium_paid: 79, status: 'active' as const,
  };

  const isRainy = weather?.rainfall ? weather.rainfall > 5 : false;
  const isHot   = weather?.temperature ? weather.temperature > 40 : false;
  const isSmoky = weather?.aqi ? weather.aqi > 200 : false;

  const daysRemaining = Math.max(0, Math.ceil((new Date(p.end_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24)));
  const claimsThisWeek = claims.filter(c => (Date.now() - new Date(c.date).getTime()) < 7 * 24 * 60 * 60 * 1000).length;

  const platformColor: Record<string, string> = {
    Swiggy: '#f97316', Zomato: '#ef4444', Blinkit: '#eab308', Zepto: '#a855f7',
    Amazon: '#f59e0b', Dunzo: '#10b981', BigBasket: '#22c55e', Flipkart: '#3b82f6',
  };
  const pColor = platformColor[w.platform] ?? '#60a5fa';

  return (
    <div className="flex w-full min-h-screen" style={{ background: 'linear-gradient(135deg, #B8E3E9 0%, #B298E7 100%)' }}>

      {/* SIDEBAR */}
      <aside className="hidden lg:flex w-[240px] flex-shrink-0 flex-col fixed left-0 top-[72px] h-[calc(100vh-72px)] z-30 overflow-y-auto"
        style={{ background: '#000080', backdropFilter: 'blur(20px)', borderRight: '1px solid rgba(0,0,128,0.15)' }}>

        {/* Worker profile */}
        <div className="p-5 border-b border-white/10">
          <div className="w-12 h-12 rounded-full flex items-center justify-center text-lg font-black text-white mb-3 shadow-lg"
            style={{ background: `linear-gradient(135deg, ${pColor}, #7c3aed)` }}>
            {w.name?.charAt(0) || 'W'}
          </div>
          <p className="font-bold text-white text-sm truncate">{w.name || 'Worker'}</p>
          <p className="text-white/40 text-xs mt-0.5 truncate">{w.platform || 'Platform'} · {w.city || 'City'}</p>
        </div>

        {/* Nav items */}
        <nav className="flex-1 p-3 pt-4 space-y-1">
          {NAV_ITEMS.map((item) => (
            <button key={item.id} onClick={() => setActiveSection(item.id)}
              className={`w-full sidebar-item flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-left ${
                activeSection === item.id ? 'sidebar-item-active' : 'text-white/50 hover:text-white'
              }`}>
              <span className="text-base w-6 text-center">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        {/* Policy badge */}
        <div className="p-4 border-t border-white/10">
          <div className="p-3 text-center rounded-xl" style={{ background: 'rgba(255,255,255,0.1)' }}>
            <p className="text-white/30 text-xs mb-1">Policy</p>
            <div className="flex items-center justify-center gap-1.5 text-green-400 font-bold text-sm">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              ACTIVE
            </div>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <div className="flex-1 lg:ml-[240px] flex flex-col pb-24 pt-[40px]">

        {/* WEATHER BANNER */}
        <div className="relative w-full h-[200px] overflow-hidden -mt-1 rounded-b-[2.5rem] shadow-2xl">
          <div className="absolute inset-0 z-0">
            {isRainy ? (
              <div className="w-full h-full bg-[#0a1128]">
                <div className="absolute inset-0 animate-thunderFlash" />
                <div className="absolute inset-0" style={{ backgroundImage: 'linear-gradient(rgba(147,197,253,0) 0%, rgba(147,197,253,0.45) 100%)', backgroundSize: '1.5px 16px', animation: 'rainFall 0.5s linear infinite' }} />
                <div className="absolute bottom-0 w-full h-1/3 bg-blue-900/50" />
              </div>
            ) : isHot ? (
              <div className="w-full h-full bg-gradient-to-t from-orange-700 to-red-900">
                <div className="absolute top-6 left-16 w-32 h-32 bg-orange-400 rounded-full blur-[20px] shadow-[0_0_80px_#f97316]" />
              </div>
            ) : isSmoky ? (
              <div className="w-full h-full bg-gray-800">
                <div className="absolute inset-0 opacity-60" style={{ backgroundImage: 'radial-gradient(circle, #6b7280 10%, transparent 40%)', backgroundSize: '80px 80px', animation: 'float 5s infinite linear' }} />
              </div>
            ) : (
              <div className="w-full h-full" style={{ background: 'linear-gradient(180deg, #0f172a, #1e1b4b)' }}>
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.8)_1px,transparent_1px)] bg-[length:24px_24px] opacity-10" />
              </div>
            )}
          </div>
          <div className="relative z-10 h-full flex flex-col justify-end p-5 lg:p-7 max-w-7xl mx-auto w-full">
            <h2 className="text-2xl lg:text-3xl text-white font-black drop-shadow-lg flex items-center gap-2">
              {w.city || 'Your City'} Weather {isRainy && '⛈️'}{isHot && '🔥'}{isSmoky && '😷'}{!isRainy && !isHot && !isSmoky && '☀️'}
            </h2>
            <p className="text-white/60 text-xs">Monitoring 24/7 · Auto-claim fires when thresholds hit</p>
          </div>
        </div>

        {/* STATS BAR */}
        <div className="px-4 lg:px-6 -mt-4 relative z-20 max-w-7xl mx-auto w-full">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {[
              { label: 'Coverage',         value: `₹${p.coverage_amount}`, sub: 'per trigger'     },
              { label: 'Days Remaining',   value: `${daysRemaining}d`,     sub: 'of 7'             },
              { label: 'Weekly Premium',   value: `₹${p.premium_paid}`,    sub: 'auto-deducted'    },
              { label: 'Claims This Week', value: `${claimsThisWeek}`,     sub: claims.length + ' total' },
            ].map((stat) => (
              <div key={stat.label} className="p-3.5 text-center rounded-2xl" style={{ background: 'rgba(255,255,255,0.85)', border: '1px solid rgba(0,0,128,0.12)', backdropFilter: 'blur(12px)' }}>
                <p className="text-xs mb-1 font-medium text-gray-400">{stat.label}</p>
                <p className="text-lg font-black text-gradient">{stat.value}</p>
                <p className="text-[10px] mt-0.5 text-gray-400">{stat.sub}</p>
              </div>
            ))}
          </div>
        </div>

        {/* SECTION CONTENT */}
        <div className="max-w-7xl mx-auto w-full px-4 lg:px-6 mt-5">

          {/* === DASHBOARD SECTION === */}
          {activeSection === 'dashboard' && (
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
              {/* LEFT 60% */}
              <div className="lg:col-span-3 space-y-5">
                {/* Auto-claim Monitor */}
                <div className="overflow-hidden relative" style={{ background: 'rgba(255,255,255,0.85)', border: '1px solid rgba(0,0,128,0.1)', backdropFilter: 'blur(12px)', borderRadius: '1.5rem' }}>
                  <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-gradient-to-b from-green-400 to-green-600 animate-pulse" />
                  <div className="p-5">
                    <div className="flex items-center gap-3 mb-4">
                      <span className="relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500" />
                      </span>
                      <span className="text-green-400 font-bold text-xs bg-green-500/10 px-3 py-1 rounded border border-green-500/20 tracking-wide">TRIGGER MONITOR ACTIVE 24/7</span>
                    </div>
                    <h3 className="text-lg font-black mb-1" style={{ color: '#000080' }}>Claims fire automatically when triggers hit</h3>
                    <p className="text-gray-500 text-sm mb-5">No forms. No proofs. No delays.</p>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-5">
                      {[{l:'Rain > 50mm', v:'₹800', i:'🌧️'},{l:'Heat > 42°C', v:'₹600', i:'☀️'},{l:'AQI > 300', v:'₹600', i:'☁️'}].map(t=>(
                        <div key={t.l} className="p-3 rounded-xl flex items-center justify-between" style={{ background: 'rgba(0,0,128,0.05)', border: '1px solid rgba(0,0,128,0.08)' }}>
                          <span className="text-gray-600 text-xs flex items-center gap-1.5"><span>{t.i}</span>{t.l}</span>
                          <span className="text-green-400 font-bold text-sm">{t.v}</span>
                        </div>
                      ))}
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1.5">
                        <span className="text-gray-500">Earnings Protected</span>
                        <span className="text-gray-400">Up to ₹{p.coverage_amount}/week</span>
                      </div>
                      <div className="h-2 w-full rounded-full overflow-hidden" style={{ background: 'rgba(0,0,128,0.1)' }}>
                        <div className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full w-full" />
                      </div>
                    </div>
                  </div>
                </div>

                {/* AI/ML Engine Status */}
                <div className="p-4" style={{ background: 'rgba(6,148,148,0.08)', border: '1px solid rgba(6,148,148,0.25)', borderRadius: '1.5rem', backdropFilter: 'blur(12px)' }}>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="font-bold text-xs px-3 py-1 rounded-full text-white" style={{ background: '#069494' }}>🤖 AI / ML ENGINE</span>
                    <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: '#89F336' }} />
                    <span className="text-xs font-bold" style={{ color: '#1a7a1a' }}>ALL SYSTEMS ACTIVE</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    {[
                      { label: 'Fraud Detection', sub: 'RandomForest ML', icon: '🛡️', c: '#2F7EE3' },
                      { label: 'Risk Engine',     sub: 'Score: ' + (w.risk_score ?? 45), icon: '📊', c: '#7B5EA7' },
                      { label: 'Premium Calc',    sub: 'Dynamic pricing', icon: '💰', c: '#FF8243' },
                    ].map(m => (
                      <div key={m.label} className="rounded-xl p-2.5 text-center" style={{ background: `${m.c}15`, border: `1.5px solid ${m.c}40` }}>
                        <div className="text-xl mb-1">{m.icon}</div>
                        <p className="font-black text-[10px]" style={{ color: m.c }}>{m.label}</p>
                        <p className="text-[9px] mt-0.5 font-medium" style={{ color: '#4a5568' }}>{m.sub}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Claims preview */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-black" style={{ color: '#000080' }}>Recent Claims</h3>
                    <button onClick={() => setActiveSection('claims')} className="text-xs hover:opacity-80 transition-colors" style={{ color: '#069494' }}>View All →</button>
                  </div>
                  <div className="space-y-3">
                    {claims.slice(0, 4).map((claim) => {
                      const triggerIcon = claim.trigger_type?.includes('RAIN') ? '🌧️' : claim.trigger_type?.includes('HEAT') ? '🔥' : claim.trigger_type?.includes('AQI') ? '💨' : claim.trigger_type?.includes('WIND') ? '🌬️' : claim.trigger_type?.includes('FLOOD') ? '🌊' : '⚡';
                      return (
                        <div key={claim.id} className="p-4 flex items-center justify-between gap-4 transition-all" style={{ background: 'rgba(255,255,255,0.85)', border: '1px solid rgba(0,0,128,0.1)', backdropFilter: 'blur(12px)', borderRadius: '1.5rem' }}>
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center border border-blue-500/30 text-lg flex-shrink-0">
                              {triggerIcon}
                            </div>
                            <div>
                              <p className="font-bold text-sm" style={{ color: '#000080' }}>{(claim.trigger_type || 'Event').replace(/_/g, ' ')}</p>
                              <p className="text-gray-400 text-xs">{new Date(claim.date).toLocaleDateString('en-IN')} · Auto-triggered</p>
                              {claim.fraud_score !== undefined && <p className="text-[10px] text-gray-400 mt-0.5">Fraud score: {(claim.fraud_score * 100).toFixed(0)}% ✓ Passed</p>}
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-lg font-black text-green-400">+₹{claim.amount}</span>
                            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                              claim.status === 'paid' ? 'bg-green-500/20 text-green-400 border-green-500/30' :
                              claim.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' :
                              claim.status === 'approved' ? 'bg-blue-500/20 text-blue-400 border-blue-500/30' :
                              'bg-red-500/20 text-red-400 border-red-500/30'
                            }`}>{(claim.status || 'pending').toUpperCase()}</span>
                          </div>
                        </div>
                      );
                    })}
                    {claims.length === 0 && (
                      <div className="p-8 text-center rounded-2xl" style={{ background: 'rgba(255,255,255,0.85)', border: '1px solid rgba(0,0,128,0.1)' }}>
                        <p className="text-gray-400">No claims yet. Weather conditions are normal.</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* RIGHT 40% */}
              <div className="lg:col-span-2 space-y-5">
                {/* Worker card */}
                <div className="p-5" style={{ background: 'rgba(255,255,255,0.85)', border: '1px solid rgba(0,0,128,0.1)', backdropFilter: 'blur(12px)', borderRadius: '1.5rem' }}>
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-14 h-14 rounded-full flex items-center justify-center text-xl font-black text-white border-2 border-white/20 flex-shrink-0"
                      style={{ background: `linear-gradient(135deg, ${pColor}, #7c3aed)` }}>
                      {w.name?.charAt(0) || 'W'}
                    </div>
                    <div>
                      <h1 className="text-base font-black" style={{ color: '#000080' }}>{w.name || 'Worker'}</h1>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-gray-500 text-xs">{w.city || 'City'}</span>
                        <span className="text-gray-300">·</span>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold border" style={{ background: `${pColor}20`, color: pColor, borderColor: `${pColor}40` }}>{w.platform || 'Platform'}</span>
                      </div>
                    </div>
                  </div>
                  <div className="pt-3 grid grid-cols-2 gap-3 text-xs" style={{ borderTop: '1px solid rgba(0,0,128,0.1)' }}>
                    <div><p className="text-gray-400 mb-0.5">Daily Earnings</p><p className="font-bold" style={{ color: '#000080' }}>₹{w.avg_daily_earning || 800}</p></div>
                    <div><p className="text-gray-400 mb-0.5">Worker ID</p><p className="font-bold text-gray-600 font-mono text-[10px] truncate">{w.worker_id || w.id}</p></div>
                  </div>
                </div>

                {/* Policy card */}
                <div className="p-5" style={{ background: 'rgba(255,255,255,0.85)', border: '1px solid rgba(0,0,128,0.1)', backdropFilter: 'blur(12px)', borderRadius: '1.5rem' }}>
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <span className="flex items-center gap-1.5 text-xs font-bold text-green-400 bg-green-500/10 px-3 py-1 rounded-full border border-green-500/20 w-max mb-3">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" /> Active
                      </span>
                      <p className="text-gray-500 text-xs">Coverage Amount</p>
                      <h3 className="text-2xl font-black text-gradient">₹{p.coverage_amount}</h3>
                    </div>
                    <div className="relative w-14 h-14 flex-shrink-0">
                      <svg viewBox="0 0 36 36" className="w-14 h-14 -rotate-90">
                        <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="rgba(0,0,128,0.1)" strokeWidth="3"/>
                        <path strokeDasharray={`${(daysRemaining / 7) * 100}, 100`} d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#069494" strokeWidth="3"/>
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center font-black text-sm" style={{ color: '#000080' }}>{daysRemaining}d</div>
                    </div>
                  </div>
                  <div className="pt-3 flex justify-between text-xs" style={{ borderTop: '1px solid rgba(0,0,128,0.1)' }}>
                    <div><p className="text-gray-400 mb-0.5">Premium</p><p className="font-bold" style={{ color: '#000080' }}>₹{p.premium_paid}/week</p></div>
                    <div className="text-right"><p className="text-gray-400 mb-0.5">Expires</p><p className="font-bold text-gray-600">{new Date(p.end_date).toLocaleDateString()}</p></div>
                  </div>
                </div>

                {/* Live weather mini */}
                <div className="p-5" style={{ background: 'rgba(255,255,255,0.85)', border: '1px solid rgba(0,0,128,0.1)', backdropFilter: 'blur(12px)', borderRadius: '1.5rem' }}>
                  <h3 className="text-sm font-black mb-3 flex items-center gap-2" style={{ color: '#000080' }}>
                    Live Triggers <button onClick={() => setActiveSection('weather')} className="text-xs ml-auto hover:opacity-80" style={{ color: '#069494' }}>Details →</button>
                  </h3>
                  <div className="grid grid-cols-2 gap-2.5">
                    {[
                      { label: 'Temp', value: weather ? `${weather.temperature}°C` : '--', alert: (weather?.temperature ?? 0) > 42 },
                      { label: 'Rain', value: weather ? `${weather.rainfall}mm` : '--', alert: (weather?.rainfall ?? 0) > 50 },
                      { label: 'AQI',  value: weather ? `${weather.aqi}` : '--', alert: (weather?.aqi ?? 0) > 300 },
                      { label: 'Wind', value: weather?.wind_speed ? `${weather.wind_speed}km/h` : '--', alert: (weather?.wind_speed ?? 0) > 45 },
                    ].map(m => (
                      <div key={m.label} className={`rounded-xl p-3 ${m.alert ? 'border border-red-500/50 bg-red-500/5' : ''}`}
                        style={!m.alert ? { background: 'rgba(0,0,128,0.04)', border: '1px solid rgba(0,0,128,0.08)' } : {}}>
                        <p className="text-gray-500 text-xs mb-1">{m.label}</p>
                        <p className={`text-base font-black ${m.alert ? 'text-red-400' : ''}`} style={!m.alert ? { color: '#000080' } : {}}>{m.value}</p>
                        {m.alert && <p className="text-red-400 text-[10px] font-bold mt-0.5">⚡ TRIGGER</p>}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* === POLICY SECTION === */}
          {activeSection === 'policy' && (
            <div className="max-w-2xl">
              <h2 className="text-2xl font-black mb-6" style={{ color: '#000080' }}>Your Policy Details</h2>
              <div className="p-7 space-y-5" style={{ background: 'rgba(255,255,255,0.85)', border: '1px solid rgba(0,0,128,0.1)', backdropFilter: 'blur(12px)', borderRadius: '1.5rem' }}>
                {[
                  { label: 'Policy ID',       value: p.policy_id },
                  { label: 'Status',          value: p.status.toUpperCase(), green: true },
                  { label: 'Coverage Amount', value: `₹${p.coverage_amount} per trigger` },
                  { label: 'Weekly Premium',  value: `₹${p.premium_paid}` },
                  { label: 'Start Date',      value: new Date(p.start_date).toLocaleDateString('en-IN', {day:'numeric',month:'long',year:'numeric'}) },
                  { label: 'End Date',        value: new Date(p.end_date).toLocaleDateString('en-IN', {day:'numeric',month:'long',year:'numeric'}) },
                  { label: 'Days Remaining',  value: `${daysRemaining} days` },
                ].map(row => (
                  <div key={row.label} className="flex justify-between items-center py-3 last:border-0" style={{ borderBottom: '1px solid rgba(0,0,128,0.1)' }}>
                    <span className="text-gray-500 text-sm">{row.label}</span>
                    <span className={`font-bold text-sm ${row.green ? 'text-green-400' : ''}`} style={!row.green ? { color: '#000080' } : {}}>{row.value}</span>
                  </div>
                ))}
              </div>
              <div className="mt-5 p-5" style={{ background: 'rgba(255,255,255,0.85)', border: '1px solid rgba(0,0,128,0.1)', backdropFilter: 'blur(12px)', borderRadius: '1.5rem' }}>
                <h3 className="font-black mb-3 text-sm" style={{ color: '#000080' }}>Covered Triggers</h3>
                <div className="space-y-2 text-sm">
                  {[['🌧️','Heavy Rain > 50mm','₹800'],['☀️','Extreme Heat > 42°C','₹600'],['☁️','High AQI > 300','₹600'],['🌊','Flood Alert > 100mm','₹800'],['💨','Strong Wind > 45km/h','₹480']].map(([i,l,v])=>(
                    <div key={l} className="flex justify-between items-center">
                      <span className="text-gray-600 flex items-center gap-2"><span>{i}</span>{l}</span>
                      <span className="text-green-400 font-bold">{v}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* === CLAIMS SECTION === */}
          {activeSection === 'claims' && (
            <div>
              <h2 className="text-2xl font-black mb-6" style={{ color: '#000080' }}>Claims History</h2>
              {claims.length === 0 ? (
                <div className="p-12 text-center rounded-2xl border-dashed" style={{ background: 'rgba(255,255,255,0.85)', border: '1px dashed rgba(0,0,128,0.2)', backdropFilter: 'blur(12px)' }}>
                  <p className="text-4xl mb-3">🌤️</p>
                  <p className="text-gray-400">No claims yet. All conditions are currently normal.</p>
                  <p className="text-xs mt-2 text-gray-400">Claims fire automatically when weather thresholds are breached.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {claims.map((claim) => (
                    <div key={claim.id} className="p-5 flex flex-col sm:flex-row items-center justify-between gap-4 transition-all" style={{ background: 'rgba(255,255,255,0.85)', border: '1px solid rgba(0,0,128,0.1)', backdropFilter: 'blur(12px)', borderRadius: '1.5rem' }}>
                      <div className="flex items-center gap-4 w-full sm:w-auto">
                        <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center border border-blue-500/30 text-2xl flex-shrink-0">
                          {claim.trigger_type?.includes('Rain') ? '🌧️' : claim.trigger_type?.includes('Heat') ? '☀️' : '⚡'}
                        </div>
                        <div>
                          <h4 className="font-black" style={{ color: '#000080' }}>{claim.trigger_type || 'Event'} Event</h4>
                          <p className="text-gray-400 text-xs">{new Date(claim.date).toLocaleDateString()} · {new Date(claim.date).toLocaleTimeString()}</p>
                          {claim.is_auto && <span className="text-[10px] text-blue-400 font-bold bg-blue-500/10 px-2 py-0.5 rounded mt-1 inline-block">AUTO-TRIGGERED</span>}
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-xl font-black text-green-400">+₹{claim.amount}</span>
                        <span className={`px-3 py-1 rounded-full text-xs font-bold border ${
                          claim.status === 'paid' ? 'bg-green-500/20 text-green-400 border-green-500/30' :
                          claim.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' :
                          claim.status === 'approved' ? 'bg-blue-500/20 text-blue-400 border-blue-500/30' :
                          'bg-red-500/20 text-red-400 border-red-500/30'
                        }`}>{(claim.status || 'pending').toUpperCase()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* === WEATHER SECTION === */}
          {activeSection === 'weather' && (
            <div>
              <h2 className="text-2xl font-black mb-2" style={{ color: '#000080' }}>{w.city} Live Weather</h2>
              <p className="text-gray-500 text-sm mb-6">Real-time conditions from WeatherAPI · Updated every hour</p>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                {[
                  { label: 'Temperature', value: weather ? `${weather.temperature}°C` : '--', icon: '🌡️', threshold: '42°C', alert: (weather?.temperature ?? 0) > 42 },
                  { label: 'Rainfall',    value: weather ? `${weather.rainfall}mm` : '--',   icon: '🌧️', threshold: '50mm', alert: (weather?.rainfall ?? 0) > 50   },
                  { label: 'AQI',         value: weather ? `${weather.aqi}` : '--',          icon: '💨', threshold: '300',  alert: (weather?.aqi ?? 0) > 300        },
                  { label: 'Wind Speed',  value: weather?.wind_speed ? `${weather.wind_speed}km/h` : '--', icon: '🌬️', threshold: '45km/h', alert: (weather?.wind_speed ?? 0) > 45 },
                ].map(m => (
                  <div key={m.label} className={`p-5 text-center rounded-2xl ${m.alert ? 'border border-red-500/50 bg-red-500/5' : ''}`}
                    style={!m.alert ? { background: 'rgba(255,255,255,0.85)', border: '1px solid rgba(0,0,128,0.1)', backdropFilter: 'blur(12px)' } : { backdropFilter: 'blur(12px)' }}>
                    <p className="text-3xl mb-2">{m.icon}</p>
                    <p className="text-gray-500 text-xs mb-1">{m.label}</p>
                    <p className={`text-3xl font-black ${m.alert ? 'text-red-400' : ''}`} style={!m.alert ? { color: '#000080' } : {}}>{m.value}</p>
                    <p className={`text-xs mt-2 font-bold ${m.alert ? 'text-red-400' : 'text-gray-400'}`}>
                      {m.alert ? '⚡ TRIGGER ACTIVE' : `Threshold: ${m.threshold}`}
                    </p>
                  </div>
                ))}
              </div>
              <div className="p-5" style={{ background: 'rgba(255,255,255,0.85)', border: '1px solid rgba(0,0,128,0.1)', backdropFilter: 'blur(12px)', borderRadius: '1.5rem' }}>
                <h3 className="font-black text-sm mb-3" style={{ color: '#000080' }}>Trigger Status</h3>
                {[
                  { name: 'Heavy Rain', condition: (weather?.rainfall ?? 0) > 50,  desc: `Current: ${weather?.rainfall ?? 0}mm / Trigger: 50mm`   },
                  { name: 'Extreme Heat', condition: (weather?.temperature ?? 0) > 42, desc: `Current: ${weather?.temperature ?? 0}°C / Trigger: 42°C` },
                  { name: 'High AQI', condition: (weather?.aqi ?? 0) > 300, desc: `Current: ${weather?.aqi ?? 0} / Trigger: 300` },
                  { name: 'Flood Alert', condition: (weather?.rainfall ?? 0) > 100, desc: `Current: ${weather?.rainfall ?? 0}mm / Trigger: 100mm` },
                  { name: 'Strong Wind', condition: (weather?.wind_speed ?? 0) > 45, desc: `Current: ${weather?.wind_speed ?? 0}km/h / Trigger: 45km/h` },
                ].map(t => (
                  <div key={t.name} className="flex justify-between items-center py-3 last:border-0" style={{ borderBottom: '1px solid rgba(0,0,128,0.1)' }}>
                    <div>
                      <p className="font-bold text-sm" style={{ color: '#000080' }}>{t.name}</p>
                      <p className="text-gray-400 text-xs">{t.desc}</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold border ${t.condition ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-green-500/20 text-green-400 border-green-500/30'}`}>
                      {t.condition ? 'TRIGGERED' : 'NORMAL'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* === PREMIUM AI SECTION === */}
          {activeSection === 'premium' && (
            <div>
              <h2 className="text-2xl font-black mb-1" style={{ color: '#000080' }}>Dynamic Premium Calculation</h2>
              <p className="text-gray-500 text-sm mb-6">AI-powered pricing based on hyper-local risk factors — your premium adjusts weekly.</p>

              {/* Premium Summary */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                {[
                  { label: 'Weekly Premium', value: `₹${premiumData?.weekly_premium ?? p.premium_paid}`, icon: '💳', color: '#2F7EE3' },
                  { label: 'Monthly Est.', value: `₹${premiumData?.monthly_estimate ?? (p.premium_paid * 4)}`, icon: '📅', color: '#16C3C6' },
                  { label: 'Coverage/Event', value: `₹${premiumData?.coverage_per_event ?? p.coverage_amount}`, icon: '🛡️', color: '#21BE5B' },
                  { label: 'Disruption Risk', value: `${((premiumData?.disruption_probability ?? 0.2) * 100).toFixed(0)}%`, icon: '⚠️', color: '#F08D28' },
                ].map(m => (
                  <div key={m.label} className="p-5 text-center rounded-2xl" style={{ background: 'rgba(255,255,255,0.85)', border: '1px solid rgba(0,0,128,0.1)', backdropFilter: 'blur(12px)' }}>
                    <p className="text-2xl mb-2">{m.icon}</p>
                    <p className="text-gray-500 text-xs mb-1">{m.label}</p>
                    <p className="text-2xl font-black" style={{ color: m.color }}>{m.value}</p>
                  </div>
                ))}
              </div>

              {/* Risk Profile */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
                <div className="p-5" style={{ background: 'rgba(255,255,255,0.85)', border: '1px solid rgba(0,0,128,0.1)', backdropFilter: 'blur(12px)', borderRadius: '1.5rem' }}>
                  <h3 className="font-black text-sm mb-4" style={{ color: '#000080' }}>Risk Profile</h3>
                  <div className="space-y-3">
                    {[
                      { label: 'Risk Level', value: (premiumData?.risk_level ?? w.risk_level ?? 'medium').toUpperCase(), badge: true },
                      { label: 'Risk Score', value: `${((premiumData?.risk_score ?? (w.risk_score ?? 45) / 100) * 100).toFixed(0)}/100` },
                      { label: 'Zone', value: (premiumData?.risk_zone ?? 'medium').toUpperCase() },
                      { label: 'Platform', value: w.platform },
                    ].map(row => (
                      <div key={row.label} className="flex justify-between items-center py-2 last:border-0" style={{ borderBottom: '1px solid rgba(0,0,128,0.1)' }}>
                        <span className="text-gray-500 text-sm">{row.label}</span>
                        {row.badge ? (
                          <span className={`px-3 py-1 rounded-full text-xs font-bold border ${
                            (premiumData?.risk_level ?? 'medium') === 'high' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                            (premiumData?.risk_level ?? 'medium') === 'medium' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' :
                            'bg-green-500/20 text-green-400 border-green-500/30'
                          }`}>{row.value}</span>
                        ) : (
                          <span className="font-bold text-sm" style={{ color: '#000080' }}>{row.value}</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Premium Breakdown */}
                <div className="p-5" style={{ background: 'rgba(255,255,255,0.85)', border: '1px solid rgba(0,0,128,0.1)', backdropFilter: 'blur(12px)', borderRadius: '1.5rem' }}>
                  <h3 className="font-black text-sm mb-4" style={{ color: '#000080' }}>Premium Breakdown</h3>
                  <div className="space-y-3">
                    {[
                      { label: 'Base Rate', value: premiumData?.breakdown?.base_rate ?? 30, color: '#4a5568' },
                      { label: 'Zone Surcharge', value: premiumData?.breakdown?.zone_surcharge ?? 15, color: '#F08D28' },
                      { label: 'Platform Loading', value: premiumData?.breakdown?.platform_loading ?? 5, color: '#2F7EE3' },
                      { label: 'Risk Loading', value: premiumData?.breakdown?.risk_loading ?? 9, color: '#16C3C6' },
                      { label: 'Disruption Loading', value: premiumData?.breakdown?.disruption_loading ?? 6, color: '#F08D28' },
                    ].map(row => (
                      <div key={row.label} className="flex justify-between items-center">
                        <span className="text-gray-500 text-xs">{row.label}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-20 h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(0,0,128,0.1)' }}>
                            <div className="h-full rounded-full" style={{ width: `${Math.min((row.value / 30) * 100, 100)}%`, background: row.color }} />
                          </div>
                          <span className="font-bold text-xs w-8 text-right" style={{ color: '#000080' }}>₹{row.value}</span>
                        </div>
                      </div>
                    ))}
                    <div className="pt-2 flex justify-between items-center" style={{ borderTop: '1px solid rgba(0,0,128,0.1)' }}>
                      <span className="font-bold text-sm" style={{ color: '#000080' }}>Total Weekly</span>
                      <span className="font-black text-xl" style={{ color: '#2F7EE3' }}>₹{premiumData?.weekly_premium ?? p.premium_paid}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* ML Factors explanation */}
              <div className="p-5" style={{ background: 'rgba(6,148,148,0.06)', border: '1px solid rgba(6,148,148,0.2)', borderRadius: '1.5rem', backdropFilter: 'blur(12px)' }}>
                <h3 className="font-black text-sm mb-3" style={{ color: '#000080' }}>🤖 How AI adjusts your premium</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-gray-600">
                  <div className="flex items-start gap-2"><span>🌧️</span><span>Live rainfall data — higher rain risk = higher loading</span></div>
                  <div className="flex items-start gap-2"><span>📍</span><span>Zone risk history — flood-prone zones add ₹25 surcharge</span></div>
                  <div className="flex items-start gap-2"><span>🏍️</span><span>Platform sensitivity — food delivery is more weather-sensitive than e-commerce</span></div>
                  <div className="flex items-start gap-2"><span>💰</span><span>Earnings-linked coverage — 80% of daily earning, max ₹800/event</span></div>
                  <div className="flex items-start gap-2"><span>🌡️</span><span>Real-time weather modelling — AQI, temperature, wind factored live</span></div>
                  <div className="flex items-start gap-2"><span>⚡</span><span>Disruption probability — current weather predicts payout likelihood</span></div>
                </div>
              </div>
            </div>
          )}

          {/* === SETTINGS SECTION === */}
          {activeSection === 'settings' && (
            <div className="max-w-lg">
              <h2 className="text-2xl font-black mb-6" style={{ color: '#000080' }}>Settings</h2>
              <div className="p-6 space-y-5" style={{ background: 'rgba(255,255,255,0.85)', border: '1px solid rgba(0,0,128,0.1)', backdropFilter: 'blur(12px)', borderRadius: '1.5rem' }}>
                <div>
                  <p className="text-gray-500 text-xs mb-1">Worker ID</p>
                  <p className="font-mono text-gray-700 text-sm p-3 rounded-xl" style={{ background: 'rgba(0,0,128,0.05)', border: '1px solid rgba(0,0,128,0.1)' }}>{w.worker_id}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs mb-1">Platform</p>
                  <p className="font-bold" style={{ color: pColor }}>{w.platform}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs mb-1">City</p>
                  <p className="font-bold" style={{ color: '#000080' }}>{w.city}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs mb-1">Daily Earnings</p>
                  <p className="font-bold" style={{ color: '#000080' }}>₹{w.avg_daily_earning}</p>
                </div>
                <div className="pt-4" style={{ borderTop: '1px solid rgba(0,0,128,0.1)' }}>
                  <p className="text-gray-500 text-xs mb-3">SMS Notifications</p>
                  <div className="flex items-center justify-between p-3 rounded-xl" style={{ background: 'rgba(0,0,128,0.05)', border: '1px solid rgba(0,0,128,0.1)' }}>
                    <span className="text-gray-700 text-sm">Claim alerts via SMS</span>
                    <div className="w-10 h-5 bg-green-500 rounded-full relative cursor-pointer">
                      <div className="w-4 h-4 bg-white rounded-full absolute right-0.5 top-0.5" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}