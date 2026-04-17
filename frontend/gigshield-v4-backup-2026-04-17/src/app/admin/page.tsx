"use client";

import { useEffect, useState } from 'react';
import { api, Analytics, Claim, WorkerData } from '@/lib/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function AdminPage() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [workers, setWorkers] = useState<WorkerData[]>([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<{ show: boolean; msg: string }>({ show: false, msg: '' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [aData, cData, wData] = await Promise.all([
        api.getAnalytics(),
        api.getAllClaims(),
        api.getAllWorkers()
      ]);
      setAnalytics(aData);
      setClaims(cData);
      setWorkers(wData);
    } catch {
      console.error("fetch failed");
    } finally {
      setLoading(false);
    }
  };

  const showToast = (msg: string) => {
    setToast({ show: true, msg });
    setTimeout(() => setToast({ show: false, msg: '' }), 3000);
  };

  const handleSimulateTrigger = async () => {
    try {
      const res = await api.triggerAuto('Chennai');
      showToast(res.message);
      fetchData(); // Refresh data immediately
    } catch {
      showToast('Failed to trigger auto system');
    }
  };

  const handleApprove = async (id: string) => {
    await api.approveClaim(id);
    fetchData();
  };

  const handleReject = async (id: string) => {
    await api.rejectClaim(id);
    fetchData();
  };

  if (loading && !analytics) return <div className="pt-24 min-h-screen flex justify-center text-white" style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%)' }}><div className="animate-spin w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full mt-20"></div></div>;
  if (!analytics) return <div className="pt-24 text-center text-white min-h-screen" style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%)' }}>Error loading admin</div>;

  return (
    <div className="w-full min-h-screen px-4 py-8 relative pt-20" style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%)' }}>
      
      {toast.show && (
        <div className="fixed top-24 right-4 z-[9999] bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-3 rounded-lg shadow-2xl animate-in slide-in-from-top-10 fade-in duration-300 flex items-center gap-2">
          <svg className="w-5 h-5 block" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
          <span className="font-bold">{toast.msg}</span>
        </div>
      )}

      <div className="max-w-7xl mx-auto w-full">
        
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Admin Control Center</h1>
            <p className="text-white/60">Monitor and manage automated parametric payouts.</p>
          </div>
          
          <button 
            onClick={handleSimulateTrigger}
            className="px-6 py-3 rounded-xl font-bold bg-gradient-to-r from-orange-500 to-red-500 hover:opacity-90 text-white shadow-[0_0_15px_rgba(249,115,22,0.4)] flex items-center gap-2 transition-all hover:scale-105 select-none"
          >
            <span className="text-xl grayscale-[0.8] brightness-[0.7]">🌩️</span>
            Simulate Rain Trigger — Chennai
          </button>
        </div>

        {/* 5 Stat Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <div className="glass-card p-6 border-t-4 border-t-blue-500 relative overflow-hidden group">
            <div className="absolute inset-x-0 bottom-0 h-1 bg-blue-500/20 group-hover:h-full transition-all duration-500 -z-10" />
            <p className="text-white/60 text-sm font-semibold mb-1 uppercase tracking-wider">Total Workers</p>
            <p className="text-3xl font-bold text-white">{analytics.total_workers.toLocaleString()}</p>
          </div>
          <div className="glass-card p-6 border-t-4 border-t-green-500 relative overflow-hidden group">
            <div className="absolute inset-x-0 bottom-0 h-1 bg-green-500/20 group-hover:h-full transition-all duration-500 -z-10" />
            <p className="text-white/60 text-sm font-semibold mb-1 uppercase tracking-wider">Active Policies</p>
            <p className="text-3xl font-bold text-white">{analytics.active_policies.toLocaleString()}</p>
          </div>
          <div className="glass-card p-6 border-t-4 border-t-amber-500 relative overflow-hidden group">
            <div className="absolute inset-x-0 bottom-0 h-1 bg-amber-500/20 group-hover:h-full transition-all duration-500 -z-10" />
            <p className="text-white/60 text-sm font-semibold mb-1 uppercase tracking-wider">Claims Today</p>
            <p className="text-3xl font-bold text-white">{analytics.claims_today}</p>
          </div>
          <div className="glass-card p-6 border-t-4 border-t-purple-500 relative overflow-hidden group">
            <div className="absolute inset-x-0 bottom-0 h-1 bg-purple-500/20 group-hover:h-full transition-all duration-500 -z-10" />
            <p className="text-white/60 text-sm font-semibold mb-1 uppercase tracking-wider">Total Payout</p>
            <p className="text-3xl font-bold text-white">₹{(analytics.total_payout/100000).toFixed(1)}L</p>
          </div>
          <div className="glass-card p-6 border-t-4 border-t-red-500 relative overflow-hidden group">
            <div className="absolute inset-x-0 bottom-0 h-1 bg-red-500/20 group-hover:h-full transition-all duration-500 -z-10" />
            <p className="text-white/60 text-sm font-semibold mb-1 uppercase tracking-wider">Loss Ratio</p>
            <p className="text-3xl font-bold text-white">{analytics.loss_ratio}%</p>
          </div>
        </div>

        {/* Charts & Graphs */}
        <div className="glass-card p-6 mb-8 h-[350px]">
          <h3 className="text-xl font-bold text-white mb-6">Claims Last 7 Days</h3>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={analytics.claims_by_day}>
              <defs>
                <linearGradient id="colorAmount" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.8}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="date" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} contentStyle={{backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px'}} />
              <Bar dataKey="amount" fill="url(#colorAmount)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Claims Table */}
          <div className="lg:col-span-2 glass-card p-6 overflow-hidden flex flex-col">
            <h3 className="text-xl font-bold text-white mb-6">Recent Claims</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-white/10 text-white/50 text-sm">
                    <th className="pb-3 font-semibold">Worker</th>
                    <th className="pb-3 font-semibold">Trigger</th>
                    <th className="pb-3 font-semibold text-right">Amount</th>
                    <th className="pb-3 font-semibold text-center">Status</th>
                    <th className="pb-3 font-semibold text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  {claims.map((claim) => (
                    <tr key={claim.id} className="border-b border-white/5 last:border-0 hover:bg-white/5 transition-colors">
                      <td className="py-4 text-white font-medium">{claim.worker_id}</td>
                      <td className="py-4 text-white/80">{claim.trigger_type}</td>
                      <td className="py-4 text-green-400 font-bold text-right">₹{claim.amount}</td>
                      <td className="py-4 text-center">
                        <span className={`px-3 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider ${
                          claim.status === 'paid' ? 'bg-green-500/20 text-green-400' :
                          claim.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                          claim.status === 'approved' ? 'bg-blue-500/20 text-blue-400' :
                          'bg-red-500/20 text-red-400'
                        }`}>
                          {claim.status}
                        </span>
                      </td>
                      <td className="py-4 text-right">
                        {claim.status === 'pending' ? (
                          <div className="flex items-center justify-end gap-2">
                            <button onClick={() => handleApprove(claim.id)} className="w-8 h-8 rounded bg-green-500/20 text-green-400 hover:bg-green-500 hover:text-white transition-colors flex items-center justify-center">✓</button>
                            <button onClick={() => handleReject(claim.id)} className="w-8 h-8 rounded bg-red-500/20 text-red-400 hover:bg-red-500 hover:text-white transition-colors flex items-center justify-center">✕</button>
                          </div>
                        ) : (
                          <span className="text-white/20 px-3">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Connected Workers */}
          <div className="glass-card p-6">
            <h3 className="text-xl font-bold text-white mb-6">Online Workers</h3>
            <div className="space-y-4">
              {workers.map((w) => (
                <div key={w.id} className="bg-white/5 border border-white/5 rounded-xl p-4 flex items-center gap-4 hover:border-white/20 transition-colors">
                  <div className={`w-10 h-10 flex-shrink-0 rounded-full flex items-center justify-center text-white font-bold border-2 ${w.platform === 'Swiggy' ? 'border-orange-500 bg-orange-500/20 text-orange-400' : 'border-red-500 bg-red-500/20 text-red-400'}`}>
                    {w.platform.charAt(0)}
                  </div>
                  <div className="flex-1 w-full overflow-hidden">
                    <h4 className="text-white font-bold block leading-none truncate">{w.name}</h4>
                    <span className="text-white/50 text-xs block truncate mt-1">{w.city}</span>
                  </div>
                  <div className="w-2 h-2 rounded-full bg-green-500 flex-shrink-0 animate-pulse shadow-[0_0_5px_#22c55e]" />
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
