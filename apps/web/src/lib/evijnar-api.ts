export type HospitalCard = {
  id: string;
  name: string;
  country: string;
  city: string;
  price: number;
  success: number;
  complication: number;
  quality: number;
  score: number;
  savingsUsd?: number;
};

export type HospitalSearchResponse = {
  connected: boolean;
  cards: HospitalCard[];
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';
const RECOVERY_ALERT_ID = process.env.NEXT_PUBLIC_RECOVERY_ALERT_ID;
const RECOVERY_TOKEN = process.env.NEXT_PUBLIC_RECOVERY_TOKEN;

const fallbackCards: HospitalCard[] = [
  { id: 'apollo', name: 'Apollo Hospitals, Delhi', country: 'IN', city: 'New Delhi', price: 11300, success: 0.987, complication: 0.013, quality: 98.4, score: 91.2, savingsUsd: 46100 },
  { id: 'charite', name: 'Charité University Hospital', country: 'DE', city: 'Berlin', price: 21600, success: 0.978, complication: 0.015, quality: 97.1, score: 88.8, savingsUsd: 35800 },
  { id: 'mayo', name: 'Mayo Clinic Rochester', country: 'US', city: 'Rochester', price: 57400, success: 0.968, complication: 0.021, quality: 95.5, score: 78.1, savingsUsd: 0 },
];

function toHospitalCard(item: any, index: number): HospitalCard {
  return {
    id: String(item?.hospital_id ?? item?.id ?? index),
    name: String(item?.hospital_name ?? item?.name ?? 'Unknown Hospital'),
    country: String(item?.country_code ?? item?.country ?? 'US'),
    city: String(item?.city ?? item?.location ?? 'Unknown City'),
    price: Number(item?.price ?? item?.estimated_total_usd ?? item?.base_price ?? 0),
    success: Number(item?.success_rate ?? item?.success ?? 0),
    complication: Number(item?.complication_rate ?? item?.complication ?? 0),
    quality: Number(item?.quality ?? item?.avg_quality_score ?? 0),
    score: Number(item?.value_score ?? item?.score ?? 0),
    savingsUsd: Number(item?.estimated_savings_usd ?? item?.savings_usd ?? 0),
  };
}

async function apiFetch(path: string, init: RequestInit = {}) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 8000);

  try {
    const response = await fetch(new URL(path, API_BASE_URL), {
      ...init,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...(init.headers ?? {}),
      },
    });

    if (!response.ok) {
      throw new Error(`Request failed with ${response.status}`);
    }

    return await response.json();
  } finally {
    window.clearTimeout(timeout);
  }
}

export async function fetchHospitalSearch(procedureCode: string, country?: string): Promise<HospitalSearchResponse> {
  try {
    const url = new URL('/api/v1/hospitals/search', API_BASE_URL);
    url.searchParams.set('procedure_code', procedureCode);
    if (country && country !== 'All') {
      url.searchParams.set('country', country);
    }

    const data = await apiFetch(url.pathname + url.search, { method: 'GET' });
    const cards = Array.isArray(data?.hospitals) ? data.hospitals.map(toHospitalCard).slice(0, 6) : fallbackCards;
    return { connected: true, cards };
  } catch {
    return { connected: false, cards: fallbackCards };
  }
}

export async function fetchDashboardOverview(): Promise<Record<string, unknown> | null> {
  try {
    const response = await fetch(new URL('/api/v1/dashboard/overview', API_BASE_URL), {
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error(`Request failed with ${response.status}`);
    }

    return await response.json();
  } catch {
    return null;
  }
}

export async function escalateRecoveryAlert(): Promise<boolean> {
  if (!RECOVERY_ALERT_ID || !RECOVERY_TOKEN) {
    return false;
  }

  try {
    await apiFetch(`/api/v1/recovery/alerts/${RECOVERY_ALERT_ID}/escalate`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${RECOVERY_TOKEN}`,
      },
    });

    return true;
  } catch {
    return false;
  }
}
