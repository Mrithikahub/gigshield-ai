const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface WorkerData {
  id: string;
  worker_id: string;
  name: string;
  email?: string;
  phone?: string;
  city: string;
  platform: string;
  avg_daily_earning: number;
  risk_level?: string;
  risk_score?: number;
}

export interface Policy {
  id: string;
  policy_id: string;
  worker_id: string;
  start_date: string;
  end_date: string;
  coverage_amount: number;
  coverage_per_event?: number;
  weekly_premium?: number;
  premium_paid: number;
  status: 'active' | 'expired';
}

export interface Claim {
  id: string;
  claim_id: string;
  worker_id: string;
  policy_id: string;
  trigger_type: string;
  amount: number;
  status: 'pending' | 'approved' | 'rejected' | 'paid' | 'review';
  date: string;
  created_at?: string;
  is_auto?: boolean;
  fraud_score?: number;
}

export interface WeatherData {
  city: string;
  temperature: number;
  rainfall: number;
  aqi: number;
  wind_speed?: number;
  condition?: string;
  trigger_fired?: boolean;
  timestamp: string;
}

export interface Analytics {
  total_workers: number;
  active_policies: number;
  claims_today: number;
  total_payout: number;
  loss_ratio: number;
  claims_by_day: { date: string; amount: number }[];
  total_claims?: number;
  policies?: { active: number };
  financials?: { premium_in: number; payouts_out: number; net_position: number };
  fraud?: { fraud_rate: number };
  claims?: { auto_triggered: number; review: number };
}

// Normalize backend worker response (worker_id → id)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function normalizeWorker(w: any): WorkerData {
  return { ...w, id: w.worker_id ?? w.id, worker_id: w.worker_id ?? w.id };
}

// Normalize backend policy response (policy_id → id)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function normalizePolicy(p: any): Policy {
  return {
    ...p,
    id: p.policy_id ?? p.id,
    policy_id: p.policy_id ?? p.id,
    coverage_amount: p.coverage_per_event ?? p.coverage_amount ?? 800,
    premium_paid: p.weekly_premium ?? p.premium_paid ?? 79,
  };
}

// Normalize backend claim response (claim_id → id)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function normalizeClaim(c: any): Claim {
  return {
    ...c,
    id: c.claim_id ?? c.id,
    claim_id: c.claim_id ?? c.id,
    date: c.created_at ?? c.date ?? new Date().toISOString(),
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function fetchApi<T>(url: string, options: RequestInit = {}, mockData: T, normalize?: (d: any) => any): Promise<T> {
  try {
    const res = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...options });
    if (!res.ok) {
      console.warn(`API ${url} returned ${res.status}, using mock`);
      return mockData;
    }
    const data = await res.json();
    if (normalize) {
      if (Array.isArray(data)) return data.map(normalize) as T;
      return normalize(data) as T;
    }
    return data as T;
  } catch {
    console.warn(`API unavailable for ${url}, using mock`);
    return mockData;
  }
}

export const api = {
  registerWorker: async (data: Omit<WorkerData, 'id' | 'worker_id'>): Promise<WorkerData> => {
    return fetchApi<WorkerData>(
      `${BASE_URL}/workers/register`,
      { method: 'POST', body: JSON.stringify(data) },
      { ...data, id: 'W-MOCK', worker_id: 'W-MOCK' },
      normalizeWorker,
    );
  },

  getWorker: async (worker_id: string): Promise<WorkerData> => {
    return fetchApi<WorkerData>(
      `${BASE_URL}/workers/${worker_id}`,
      {},
      { id: worker_id, worker_id, name: 'Demo Worker', city: 'Chennai', platform: 'Swiggy', avg_daily_earning: 800 },
      normalizeWorker,
    );
  },

  getAllWorkers: async (): Promise<WorkerData[]> => {
    const mockWorkers: WorkerData[] = [
      { id: 'W-1001', worker_id: 'W-1001', name: 'Rahul Sharma', city: 'Chennai', platform: 'Swiggy', avg_daily_earning: 800 },
    ];
    try {
      const res = await fetch(`${BASE_URL}/workers/`);
      if (!res.ok) return mockWorkers;
      const data = await res.json();
      // Backend returns {"total": N, "workers": [...]} — unwrap before normalizing
      const arr = data.workers ?? data;
      return Array.isArray(arr) ? arr.map(normalizeWorker) : mockWorkers;
    } catch { return mockWorkers; }
  },

  createPolicy: async (data: { worker_id: string; weeks: number; plan?: string }): Promise<Policy> => {
    return fetchApi<Policy>(
      `${BASE_URL}/policies/create`,
      { method: 'POST', body: JSON.stringify({ worker_id: data.worker_id, weeks: data.weeks }) },
      {
        id: 'P-MOCK', policy_id: 'P-MOCK', worker_id: data.worker_id,
        start_date: new Date().toISOString(),
        end_date: new Date(Date.now() + data.weeks * 7 * 86400000).toISOString(),
        coverage_amount: 800, premium_paid: 79, status: 'active',
      },
      normalizePolicy,
    );
  },

  getPolicy: async (worker_id: string): Promise<Policy> => {
    const mockPolicy: Policy = {
      id: `P-${worker_id}`, policy_id: `P-${worker_id}`, worker_id,
      start_date: new Date().toISOString(),
      end_date: new Date(Date.now() + 7 * 86400000).toISOString(),
      coverage_amount: 800, premium_paid: 79, status: 'active',
    };
    try {
      const res = await fetch(`${BASE_URL}/policies/${worker_id}`);
      if (!res.ok) return mockPolicy;
      const data = await res.json();
      const p = data.active_policy ?? data;
      return p ? normalizePolicy(p) : mockPolicy;
    } catch { return mockPolicy; }
  },

  getPremium: async (worker_id: string): Promise<{ premium: number }> => {
    return fetchApi<{ premium: number }>(
      `${BASE_URL}/premium/${worker_id}`,
      {},
      { premium: 79 },
    );
  },

  triggerAuto: async (city: string): Promise<{ success: boolean; message: string }> => {
    return fetchApi<{ success: boolean; message: string }>(
      `${BASE_URL}/trigger/auto/${city}`,
      { method: 'POST' },
      { success: true, message: `Trigger fired for ${city}!` },
    );
  },

  getWeather: async (city: string): Promise<WeatherData> => {
    try {
      const res = await fetch(`${BASE_URL}/trigger/weather/${city}`);
      if (!res.ok) throw new Error();
      const data = await res.json();
      // Backend wraps weather fields under a 'weather' key
      const w = data.weather ?? data;
      return {
        city: data.city ?? city,
        temperature: w.temperature ?? 31,
        rainfall: w.rainfall ?? 0,
        aqi: w.aqi ?? 150,
        wind_speed: w.wind_speed ?? 0,
        condition: w.condition ?? 'Clear',
        trigger_fired: data.disrupted ?? false,
        timestamp: new Date().toISOString(),
      };
    } catch {
      // Demo fallback with realistic Chennai summer values
      return { city, temperature: 36, rainfall: 2.4, aqi: 148, wind_speed: 14, condition: 'Partly Cloudy', timestamp: new Date().toISOString() };
    }
  },

  getAllClaims: async (): Promise<Claim[]> => {
    try {
      const res = await fetch(`${BASE_URL}/claims/all`);
      if (!res.ok) return [];
      const data = await res.json();
      const arr = data.claims ?? data;
      return Array.isArray(arr) ? arr.map(normalizeClaim) : [];
    } catch { return []; }
  },

  getWorkerClaims: async (worker_id: string): Promise<Claim[]> => {
    const demoClaims: Claim[] = [
      { id: 'C-001', claim_id: 'C-001', worker_id, policy_id: 'P-DEMO', trigger_type: 'HEAVY_RAIN', amount: 800, status: 'paid', date: new Date(Date.now() - 2 * 86400000).toISOString(), is_auto: true, fraud_score: 0.05 },
      { id: 'C-002', claim_id: 'C-002', worker_id, policy_id: 'P-DEMO', trigger_type: 'EXTREME_HEAT', amount: 600, status: 'paid', date: new Date(Date.now() - 5 * 86400000).toISOString(), is_auto: true, fraud_score: 0.08 },
      { id: 'C-003', claim_id: 'C-003', worker_id, policy_id: 'P-DEMO', trigger_type: 'HIGH_AQI', amount: 600, status: 'approved', date: new Date(Date.now() - 1 * 86400000).toISOString(), is_auto: true, fraud_score: 0.12 },
      { id: 'C-004', claim_id: 'C-004', worker_id, policy_id: 'P-DEMO', trigger_type: 'STRONG_WIND', amount: 480, status: 'pending', date: new Date(Date.now() - 3600000).toISOString(), is_auto: true, fraud_score: 0.03 },
    ];
    try {
      const res = await fetch(`${BASE_URL}/claims/${worker_id}`);
      if (!res.ok) return demoClaims;
      const data = await res.json();
      const arr = data.claims ?? data;
      const result = Array.isArray(arr) ? arr.map(normalizeClaim) : [];
      const isDemoUser = worker_id.startsWith('DEMO') || worker_id === 'W1001';
      return result.length > 0 ? result : (isDemoUser ? demoClaims : []);
    } catch {
      const isDemoUser = worker_id.startsWith('DEMO') || worker_id === 'W1001';
      return isDemoUser ? demoClaims : [];
    }
  },

  approveClaim: async (claim_id: string): Promise<void> => {
    await fetch(`${BASE_URL}/claims/${claim_id}/approve`, { method: 'PATCH' });
  },

  rejectClaim: async (claim_id: string): Promise<void> => {
    await fetch(`${BASE_URL}/claims/${claim_id}/reject`, { method: 'PATCH' });
  },

  getAnalytics: async (): Promise<Analytics> => {
    try {
      const res = await fetch(`${BASE_URL}/analytics`);
      if (!res.ok) throw new Error();
      const d = await res.json();
      return {
        total_workers:   d.total_workers ?? 0,
        active_policies: d.policies?.active ?? 0,
        claims_today:    d.total_claims ?? 0,
        total_payout:    d.financials?.payouts_out ?? 0,
        loss_ratio:      d.financials ? (d.financials.payouts_out / Math.max(d.financials.premium_in, 1)) * 100 : 0,
        claims_by_day:   [],
        ...d,
      };
    } catch {
      return { total_workers: 0, active_policies: 0, claims_today: 0, total_payout: 0, loss_ratio: 0, claims_by_day: [] };
    }
  },

  createPaymentOrder: async (data: { amount: number; worker_id: string; plan: string }) => {
    const res = await fetch(`${BASE_URL}/payments/create-order`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create order');
    return res.json() as Promise<{ order_id: string; amount: number; currency: string; key_id: string }>;
  },

  verifyPayment: async (data: { razorpay_order_id: string; razorpay_payment_id: string; razorpay_signature: string }) => {
    const res = await fetch(`${BASE_URL}/payments/verify`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Payment verification failed');
    return res.json() as Promise<{ success: boolean; payment_id: string }>;
  },
};
