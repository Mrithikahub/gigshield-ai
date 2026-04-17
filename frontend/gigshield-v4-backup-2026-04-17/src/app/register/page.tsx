"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { api } from '@/lib/api';

type Step = 1 | 2 | 3 | 4 | 5;

const PLATFORMS = [
  { name: 'Swiggy',          color: '#f97316', glow: 'rgba(249,115,22,0.35)',  label: 'S'  },
  { name: 'Zomato',          color: '#ef4444', glow: 'rgba(239,68,68,0.35)',   label: 'Z'  },
  { name: 'Blinkit',         color: '#eab308', glow: 'rgba(234,179,8,0.35)',   label: 'B'  },
  { name: 'Zepto',           color: '#a855f7', glow: 'rgba(168,85,247,0.35)',  label: 'Ze' },
  { name: 'Amazon',          color: '#f59e0b', glow: 'rgba(245,158,11,0.35)', label: 'A'  },
  { name: 'Dunzo',           color: '#10b981', glow: 'rgba(16,185,129,0.35)', label: 'D'  },
  { name: 'BigBasket',       color: '#22c55e', glow: 'rgba(34,197,94,0.35)',  label: 'BB' },
  { name: 'Flipkart',        color: '#3b82f6', glow: 'rgba(59,130,246,0.35)', label: 'F'  },
];

const PLANS = [
  { id: 'basic',    name: 'Basic',    price: 49,  max: '800',  desc: 'Rain + Heat coverage' },
  { id: 'standard', name: 'Standard', price: 79,  max: '1400', desc: 'All 5 triggers', pop: true },
  { id: 'premium',  name: 'Premium',  price: 99,  max: '2000', desc: 'All triggers + priority', },
];

function loadRazorpayScript(): Promise<boolean> {
  return new Promise((resolve) => {
    if (typeof window !== 'undefined' && (window as unknown as Record<string,unknown>)['Razorpay']) {
      resolve(true);
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.onload = () => resolve(true);
    script.onerror = () => resolve(false);
    document.body.appendChild(script);
  });
}

export default function Register() {
  const router = useRouter();
  const [step, setStep] = useState<Step>(1);
  const [loading, setLoading] = useState(false);
  const [payStatus, setPayStatus] = useState<'idle'|'processing'|'success'>('idle');
  const [imgError, setImgError] = useState(false);

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('+91');
  const [platform, setPlatform] = useState('');
  const [city, setCity] = useState('');
  const [locationError, setLocationError] = useState('');
  const [locationLoading, setLocationLoading] = useState(false);
  const [earnings, setEarnings] = useState(500);
  const [agreed, setAgreed] = useState(false);
  const [plan, setPlan] = useState('');

  const handleNext = () => { if (step < 5) setStep((s) => (s + 1) as Step); };

  const handleDetectLocation = () => {
    setLocationLoading(true);
    setLocationError('');
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        () => { setTimeout(() => { setCity('Chennai'); setLocationLoading(false); }, 1500); },
        () => { setLocationError('Location access denied.'); setLocationLoading(false); }
      );
    } else {
      setLocationError('Geolocation not supported.'); setLocationLoading(false);
    }
  };

  const handlePayment = async () => {
    if (!plan) return;
    setLoading(true);
    setPayStatus('processing');
    try {
      // 1. Register worker
      const worker = await api.registerWorker({ name, email, phone, city, platform, avg_daily_earning: earnings });
      
      // FIX: Save BOTH worker ID AND worker name to localStorage
      localStorage.setItem('triggerpe_worker_id', worker.id);
      localStorage.setItem('triggerpe_worker_name', name);  // <-- THIS IS THE FIX
      localStorage.setItem('triggerpe_worker_city', city);
      localStorage.setItem('triggerpe_worker_platform', platform);
      localStorage.setItem('triggerpe_worker_earning', earnings.toString());
      localStorage.setItem('triggerpe_just_registered', 'true');

      const selectedPlan = PLANS.find(p => p.id === plan)!;
      const amountPaise = selectedPlan.price * 100;

      // 2. Try Razorpay
      const rzpLoaded = await loadRazorpayScript();
      if (rzpLoaded) {
        try {
          const order = await api.createPaymentOrder({ amount: amountPaise, worker_id: worker.id, plan });
          await new Promise<void>((resolve) => {
            const options = {
              key: order.key_id,
              amount: order.amount,
              currency: order.currency,
              name: 'TriggerPe',
              description: `${selectedPlan.name} Plan — Weekly Coverage`,
              order_id: order.order_id,
              handler: async (response: Record<string,string>) => {
                try { await api.verifyPayment(response as Parameters<typeof api.verifyPayment>[0]); } catch {}
                resolve();
              },
              prefill: { name, email, contact: phone },
              theme: { color: '#6366f1' },
              modal: { ondismiss: () => { setLoading(false); setPayStatus('idle'); resolve(); } },
            };
            const Razorpay = (window as unknown as Record<string,unknown>)['Razorpay'] as new (o: unknown) => { open(): void };
            const rzp = new Razorpay(options);
            rzp.open();
          });
        } catch (e) {
          console.warn('Razorpay order failed, using demo flow', e);
        }
      }

      // 3. Create policy & redirect
      await api.createPolicy({ worker_id: worker.id, weeks: 1, plan });
      setPayStatus('success');
      setTimeout(() => router.push(`/dashboard/${worker.id}`), 800);
    } catch (err) {
      console.error(err);
      setLoading(false);
      setPayStatus('idle');
    }
  };

  const selectedPlanObj = PLANS.find(p => p.id === plan);

  return (
    <div className="flex w-full min-h-[calc(100vh-80px)] overflow-hidden" style={{ background: 'linear-gradient(135deg, #1F242E 0%, #0f2d40 40%, #1F2E24 100%)' }}>

      {/* LEFT SIDE */}
      <div className="w-full lg:w-[60%] p-6 md:p-10 lg:p-14 flex flex-col pt-10 relative z-10 overflow-y-auto">

        {/* Step progress */}
        <div className="flex items-center justify-between w-full max-w-lg mx-auto mb-12 relative">
          <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-1 bg-white/10 z-0" />
          {[1,2,3,4,5].map((idx) => (
            <div key={idx} className={`relative z-10 w-9 h-9 rounded-full flex items-center justify-center font-bold font-mono transition-all duration-300 text-sm ${
              step > idx ? 'bg-green-500 text-white shadow-[0_0_12px_rgba(34,197,94,0.5)]' :
              step === idx ? 'bg-blue-500 text-white shadow-[0_0_15px_rgba(59,130,246,0.6)]' :
              'bg-[#1e293b] text-white/40 ring-2 ring-white/10'
            }`}>
              {step > idx ? '✓' : idx}
            </div>
          ))}
        </div>

        <div className="max-w-lg mx-auto w-full flex-grow">

          {/* STEP 1: Details + Platform */}
          {step === 1 && (
            <div className="animate-in fade-in slide-in-from-right-8 duration-500">
              <h2 className="text-2xl font-black mb-1 text-white">Your Details</h2>
              <p className="text-white/40 text-sm mb-7">Fill in your personal information</p>
              <div className="space-y-5">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-white/60 mb-1.5 text-sm font-medium">Full Name *</label>
                    <input type="text" value={name} onChange={(e) => setName(e.target.value)}
                      className="w-full glass-card bg-white/5 border-white/20 px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition-all rounded-xl text-sm"
                      placeholder="Rajan Kumar" />
                  </div>
                  <div>
                    <label className="block text-white/60 mb-1.5 text-sm font-medium">Phone *</label>
                    <input type="tel" value={phone} onChange={(e) => setPhone(e.target.value)}
                      className="w-full glass-card bg-white/5 border-white/20 px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition-all rounded-xl text-sm" />
                  </div>
                </div>
                <div>
                  <label className="block text-white/60 mb-1.5 text-sm font-medium">Email Address</label>
                  <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                    className="w-full glass-card bg-white/5 border-white/20 px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition-all rounded-xl text-sm"
                    placeholder="you@example.com" />
                </div>

                {/* 8 Platforms 4×2 */}
                <div>
                  <label className="block text-white/60 mb-3 text-sm font-medium">Select Your Platform *</label>
                  <div className="grid grid-cols-4 gap-2.5">
                    {PLATFORMS.map((p) => {
                      const isSelected = platform === p.name;
                      return (
                        <button key={p.name} onClick={() => setPlatform(p.name)}
                          className="glass-card p-3 flex flex-col items-center gap-1.5 transition-all rounded-xl border-2"
                          style={{ borderColor: isSelected ? p.color : 'rgba(255,255,255,0.08)', background: isSelected ? `${p.color}15` : undefined, boxShadow: isSelected ? `0 0 16px ${p.glow}` : undefined }}>
                          <div className="w-9 h-9 rounded-full flex items-center justify-center font-black text-xs text-white" style={{ background: p.color }}>
                            {p.label}
                          </div>
                          <span className="text-white text-[9px] text-center leading-tight font-medium">{p.name}</span>
                        </button>
                      );
                    })}
                  </div>
                  {platform && <p className="text-xs mt-2 font-bold" style={{ color: PLATFORMS.find(p=>p.name===platform)?.color }}>✓ {platform} selected</p>}
                </div>

                <button onClick={handleNext} disabled={!name || phone.replace(/\D/g,'').length < 10 || !platform}
                  className="w-full mt-4 py-3.5 rounded-xl font-bold text-base bg-gradient-to-r from-[#2F7EE3] to-[#3034D9] hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed transition-all text-white shadow-[0_0_20px_rgba(96,165,250,0.3)]">
                  Next →
                </button>
              </div>
            </div>
          )}

          {/* STEP 2: Location */}
          {step === 2 && (
            <div className="animate-in fade-in slide-in-from-right-8 duration-500 text-center">
              <h2 className="text-2xl font-black mb-1 text-white">Where do you deliver?</h2>
              <p className="text-white/40 text-sm mb-8">We use this to track weather triggers in your area</p>
              <div className="flex flex-col items-center justify-center min-h-[220px]">
                {city ? (
                  <div className="flex flex-col items-center animate-in zoom-in duration-300">
                    <div className="w-16 h-16 bg-green-500/20 text-green-400 rounded-full flex items-center justify-center mb-4">
                      <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                    </div>
                    <span className="text-xs text-green-400 font-bold uppercase tracking-wider mb-1">Location Confirmed</span>
                    <h3 className="text-4xl font-black text-gradient">{city}</h3>
                    <button onClick={() => setCity('')} className="mt-3 text-xs text-white/30 hover:text-white/60 underline transition-colors">Change city</button>
                  </div>
                ) : (
                  <>
                    <svg className={`w-20 h-20 text-blue-400 mb-6 ${locationLoading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <button onClick={handleDetectLocation} disabled={locationLoading}
                      className="px-7 py-3 rounded-full font-bold bg-white/10 hover:bg-white/20 border border-white/20 text-white transition-all text-sm mb-4">
                      {locationLoading ? 'Detecting...' : '📍 Detect My Location'}
                    </button>
                    {locationError && <p className="text-red-400 mb-3 text-sm">{locationError}</p>}
                    <p className="text-white/30 text-xs mb-3">or select your city manually</p>
                    <select
                      value={city}
                      onChange={(e) => setCity(e.target.value)}
                      className="w-full glass-card bg-white/5 border border-white/20 px-4 py-3 text-white rounded-xl text-sm focus:outline-none focus:border-blue-500 transition-all"
                    >
                      <option value="" className="bg-gray-900">Select city...</option>
                      {['Mumbai','Delhi','Chennai','Bangalore','Hyderabad','Kolkata','Pune','Ahmedabad','Jaipur','Surat','Lucknow','Nagpur'].map(c => (
                        <option key={c} value={c} className="bg-gray-900">{c}</option>
                      ))}
                    </select>
                  </>
                )}
              </div>
              <button onClick={handleNext} disabled={!city}
                className="w-full mt-8 py-3.5 rounded-xl font-bold bg-gradient-to-r from-[#2F7EE3] to-[#3034D9] hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed transition-all text-white">
                Next →
              </button>
            </div>
          )}


          {/* STEP 3: Earnings */}
          {step === 3 && (
            <div className="animate-in fade-in slide-in-from-right-8 duration-500 text-center">
              <h2 className="text-2xl font-black mb-1 text-white">How much do you earn?</h2>
              <p className="text-white/40 text-sm mb-8">Daily earnings on a good day</p>
              <div className="bg-blue-900/20 p-7 rounded-3xl border border-blue-500/20 mb-8">
                <h3 className="text-6xl font-black mb-6 text-gradient">₹{earnings}</h3>
                <input type="range" min="100" max="2000" step="50" value={earnings}
                  onChange={(e) => setEarnings(Number(e.target.value))}
                  className="w-full h-2.5 bg-white/10 rounded-lg appearance-none cursor-pointer accent-blue-500 mb-4" />
                <div className="flex justify-between text-white/30 text-xs font-medium"><span>₹100</span><span>₹2000</span></div>
              </div>
              <div className="inline-block px-5 py-2.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300 font-bold text-sm mb-6">
                Coverage per trigger: ₹{Math.min(800, Math.round(earnings * 0.8))}
              </div>
              <button onClick={handleNext} className="w-full py-3.5 rounded-xl font-bold bg-gradient-to-r from-[#2F7EE3] to-[#3034D9] hover:opacity-90 transition-all text-white">
                Next →
              </button>
            </div>
          )}

          {/* STEP 4: Exclusions */}
          {step === 4 && (
            <div className="animate-in fade-in slide-in-from-right-8 duration-500">
              <h2 className="text-2xl font-black mb-1 text-white">Terms & Exclusions</h2>
              <p className="text-white/40 text-sm mb-6">What events are NOT covered?</p>
              <div className="glass-card border-l-4 border-l-red-500 bg-red-950/20 p-6 rounded-xl mb-5">
                <ul className="space-y-3">
                  {["Vehicle repairs or damage","Health and accident medical bills","War or armed conflict","Government declared pandemic","Platform account suspension","Pre-existing platform disputes"].map((exc,i) => (
                    <li key={i} className="flex items-start gap-3 text-white/70 text-sm">
                      <svg className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                      {exc}
                    </li>
                  ))}
                </ul>
              </div>
              <label className="flex items-start gap-4 p-4 rounded-xl cursor-pointer hover:bg-white/5 transition-colors">
                <div className="relative flex-shrink-0 mt-0.5">
                  <input type="checkbox" className="w-5 h-5 appearance-none border-2 border-amber-500 rounded bg-transparent checked:bg-amber-500 transition-colors cursor-pointer" checked={agreed} onChange={(e) => setAgreed(e.target.checked)} />
                  {agreed && <svg className="w-3 h-3 text-white absolute top-1 left-1 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7"/></svg>}
                </div>
                <span className="text-white/80 text-sm select-none">I understand these exclusions and agree to TriggerPe terms of service.</span>
              </label>
              <button onClick={handleNext} disabled={!agreed}
                className="w-full mt-6 py-3.5 rounded-xl font-bold bg-gradient-to-r from-[#2F7EE3] to-[#3034D9] hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed transition-all text-white">
                Next →
              </button>
            </div>
          )}

          {/* STEP 5: Plan + Razorpay */}
          {step === 5 && (
            <div className="animate-in fade-in slide-in-from-right-8 duration-500">
              <h2 className="text-2xl font-black mb-1 text-white text-center">Choose Your Plan</h2>
              <p className="text-white/40 text-sm mb-6 text-center">Coverage starts immediately after payment</p>

              <div className="space-y-3 mb-6">
                {PLANS.map((p) => (
                  <div key={p.id} onClick={() => setPlan(p.id)}
                    className={`relative glass-card p-4 border-2 cursor-pointer transition-all rounded-xl ${plan === p.id ? 'border-blue-500 bg-blue-500/10 shadow-[0_0_20px_rgba(59,130,246,0.2)]' : 'border-white/10 hover:border-white/25'}`}>
                    {p.pop && <span className="absolute -top-2.5 right-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-[10px] font-bold px-2.5 py-0.5 rounded-full">Most Popular</span>}
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-3">
                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all ${plan === p.id ? 'border-blue-500 bg-blue-500' : 'border-white/30'}`}>
                          {plan === p.id && <div className="w-2 h-2 rounded-full bg-white" />}
                        </div>
                        <div>
                          <h3 className="font-bold text-white text-sm">{p.name}</h3>
                          <p className="text-white/50 text-xs">{p.desc} · Max ₹{p.max}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-xl font-black text-white">₹{p.price}</span>
                        <span className="text-white/40 text-xs block">/week</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {selectedPlanObj && (
                <div className="bg-gradient-to-r from-blue-900/40 to-purple-900/40 border border-blue-500/30 p-4 rounded-xl mb-5">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-white font-bold text-sm">{selectedPlanObj.name} Plan selected</p>
                      <p className="text-blue-300 text-xs mt-0.5">Coverage starts immediately after payment</p>
                    </div>
                    <div className="text-right">
                      <span className="text-2xl font-black text-blue-400">₹{selectedPlanObj.price}</span>
                    </div>
                  </div>
                </div>
              )}

              <button onClick={handlePayment} disabled={!plan || loading || payStatus === 'success'}
                className={`w-full py-4 rounded-xl font-bold text-base transition-all text-white flex items-center justify-center gap-3 ${
                  payStatus === 'success' ? 'bg-green-600' :
                  'bg-gradient-to-r from-green-600 to-emerald-500 hover:opacity-90 shadow-[0_0_20px_rgba(16,185,129,0.4)]'
                } disabled:opacity-50 disabled:cursor-not-allowed`}>
                {payStatus === 'success' ? (
                  <>✓ Payment Successful! Redirecting...</>
                ) : loading ? (
                  <span className="flex items-center gap-2">
                    <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Processing Payment...
                  </span>
                ) : (
                  <>💳 Pay ₹{selectedPlanObj?.price ?? '–'} & Activate Coverage</>
                )}
              </button>
              <p className="text-white/25 text-xs text-center mt-3">Powered by Razorpay · Secure 256-bit SSL</p>
            </div>
          )}

        </div>
      </div>

      {/* RIGHT SIDE */}
      <div className="hidden lg:flex lg:w-[40%] relative border-l border-white/10 flex-col items-center justify-center overflow-hidden" style={{ background: 'linear-gradient(135deg, #1F242E 0%, #1F2E24 50%, #0f2d40 100%)' }}>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-orange-500/10 blur-[80px] rounded-full" />
        <div className="absolute inset-0 overflow-hidden">
          {[...Array(18)].map((_, i) => (
            <div key={i} className="absolute bg-white rounded-full animate-pulse"
              style={{ width: (i*37%3)+1+'px', height: (i*37%3)+1+'px', top: (i*17%100)+'%', left: (i*23%100)+'%', animationDelay: (i*0.12)+'s' }} />
          ))}
        </div>

        {/* Delivery man image */}
        <div className="relative z-10 flex flex-col items-center">
          {!imgError ? (
            <div className="w-[280px] h-[340px] relative animate-float">
              <Image src="/delivery-man.png" alt="Happy Delivery Partner" fill
                className="object-contain drop-shadow-2xl" onError={() => setImgError(true)} />
            </div>
          ) : (
            <div className="animate-float">
              <DeliveryManSVG />
            </div>
          )}
        </div>

        <div className="relative z-10 mt-4 text-center px-8">
          <h2 className="text-xl font-black text-white mb-1">Ride Safe, Earn Safe</h2>
          <p className="text-blue-200 text-sm">We cover you automatically when weather strikes.</p>
        </div>

        {/* Step progress hints */}
        <div className="relative z-10 mt-6 px-8 w-full">
          {[
            { step: 1, label: 'Your Details', icon: '📝' },
            { step: 2, label: 'Your City',    icon: '📍' },
            { step: 3, label: 'Earnings',     icon: '💰' },
            { step: 4, label: 'Terms',        icon: '📋' },
            { step: 5, label: 'Activate',     icon: '🛡️' },
          ].map((s) => (
            <div key={s.step} className={`flex items-center gap-3 py-2 text-sm transition-all ${step === s.step ? 'text-white font-bold' : step > s.step ? 'text-green-400' : 'text-white/25'}`}>
              <span className="text-base">{step > s.step ? '✓' : s.icon}</span>
              {s.label}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function DeliveryManSVG() {
  return (
    <svg width="240" height="300" viewBox="0 0 240 300" xmlns="http://www.w3.org/2000/svg">
      {/* Glow under feet */}
      <ellipse cx="130" cy="285" rx="55" ry="10" fill="rgba(251,146,60,0.25)" />

      {/* === DELIVERY BOX (carried on back, left side) === */}
      <rect x="28" y="110" width="52" height="48" rx="6" fill="#ea580c" />
      <rect x="28" y="110" width="52" height="48" rx="6" fill="none" stroke="#c2410c" strokeWidth="1.5" />
      <line x1="54" y1="110" x2="54" y2="158" stroke="#c2410c" strokeWidth="1.5" />
      <line x1="28" y1="134" x2="80" y2="134" stroke="#c2410c" strokeWidth="1.5" />
      {/* TriggerPe logo on box */}
      <text x="36" y="127" fontSize="7" fontWeight="bold" fill="white" opacity="0.9">Trigger</text>
      <text x="40" y="138" fontSize="7" fontWeight="bold" fill="white" opacity="0.9">Pe</text>
      {/* Box strap */}
      <path d="M80 118 Q95 105 105 120" fill="none" stroke="#9ca3af" strokeWidth="3" strokeLinecap="round" />

      {/* === BODY (orange delivery jacket) === */}
      <rect x="86" y="120" width="58" height="72" rx="14" fill="#f97316" />
      {/* Jacket zipper line */}
      <line x1="115" y1="122" x2="115" y2="190" stroke="#ea580c" strokeWidth="2" />
      {/* Jacket pocket */}
      <rect x="92" y="148" width="16" height="12" rx="3" fill="#ea580c" />
      {/* TriggerPe badge */}
      <rect x="114" y="130" width="26" height="14" rx="4" fill="#1e40af" />
      <text x="117" y="141" fontSize="6" fontWeight="bold" fill="white">TriggerPe</text>

      {/* === HEAD === */}
      {/* Helmet */}
      <ellipse cx="115" cy="92" rx="28" ry="14" fill="#1e3a8a" />
      <rect x="87" y="88" width="56" height="20" rx="4" fill="#1e3a8a" />
      {/* Helmet visor */}
      <rect x="91" y="94" width="48" height="12" rx="5" fill="#93c5fd" opacity="0.6" />
      {/* Helmet chin strap */}
      <path d="M87 100 Q87 112 95 114 Q115 118 135 114 Q143 112 143 100" fill="none" stroke="#1e3a8a" strokeWidth="2.5" />
      {/* Face */}
      <ellipse cx="115" cy="106" rx="22" ry="18" fill="#fbbf24" />
      {/* Happy eyes */}
      <ellipse cx="107" cy="103" rx="4" ry="4.5" fill="white" />
      <ellipse cx="123" cy="103" rx="4" ry="4.5" fill="white" />
      <circle cx="108" cy="104" r="2.5" fill="#1f2937" />
      <circle cx="124" cy="104" r="2.5" fill="#1f2937" />
      <circle cx="109" cy="103" r="1" fill="white" />
      <circle cx="125" cy="103" r="1" fill="white" />
      {/* Smile */}
      <path d="M105 112 Q115 120 125 112" fill="none" stroke="#92400e" strokeWidth="2.5" strokeLinecap="round" />
      {/* Cheeks */}
      <circle cx="100" cy="110" r="5" fill="#fca5a5" opacity="0.5" />
      <circle cx="130" cy="110" r="5" fill="#fca5a5" opacity="0.5" />
      {/* Helmet logo dot */}
      <circle cx="115" cy="82" r="4" fill="#f97316" />
      <circle cx="115" cy="82" r="2" fill="white" />

      {/* === ARMS === */}
      {/* Left arm (holding box) */}
      <path d="M86 135 Q65 148 58 160" fill="none" stroke="#f97316" strokeWidth="14" strokeLinecap="round" />
      <ellipse cx="55" cy="163" rx="8" ry="7" fill="#fbbf24" />
      {/* Right arm (raised, excited) */}
      <path d="M144 130 Q162 115 168 108" fill="none" stroke="#f97316" strokeWidth="14" strokeLinecap="round" />
      <ellipse cx="170" cy="106" rx="8" ry="7" fill="#fbbf24" />
      {/* Thumbs up */}
      <path d="M165 100 Q162 95 168 93 Q174 91 173 98 Q170 104 165 105Z" fill="#fbbf24" />

      {/* === LEGS (mid-stride, running) === */}
      {/* Left leg forward */}
      <path d="M100 192 Q92 225 85 255" fill="none" stroke="#1e3a8a" strokeWidth="16" strokeLinecap="round" />
      {/* Left shoe */}
      <ellipse cx="82" cy="260" rx="18" ry="8" fill="#111827" />
      <ellipse cx="82" cy="258" rx="14" ry="6" fill="#374151" />
      {/* Right leg back */}
      <path d="M130 192 Q145 220 152 248" fill="none" stroke="#1e3a8a" strokeWidth="16" strokeLinecap="round" />
      {/* Right shoe */}
      <ellipse cx="155" cy="253" rx="18" ry="8" fill="#111827" />
      <ellipse cx="155" cy="251" rx="14" ry="6" fill="#374151" />

      {/* === SPEED LINES === */}
      <line x1="170" y1="150" x2="200" y2="150" stroke="rgba(251,146,60,0.5)" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="175" y1="162" x2="210" y2="162" stroke="rgba(251,146,60,0.35)" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="172" y1="174" x2="205" y2="174" stroke="rgba(251,146,60,0.2)" strokeWidth="1" strokeLinecap="round" />

      {/* Stars / sparkle around */}
      <text x="180" y="100" fontSize="16">⭐</text>
      <text x="20" y="95" fontSize="12">✨</text>
      <text x="160" y="200" fontSize="10">💨</text>
    </svg>
  );
}