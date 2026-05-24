export type PlatformStatus = {
  connected: boolean;
  healthy: boolean;
  ready: boolean;
  label: string;
  detail: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

export async function fetchPlatformStatus(): Promise<PlatformStatus> {
  try {
    const [healthResponse, readyResponse] = await Promise.all([
      fetch(new URL('/health', API_BASE_URL), { cache: 'no-store' }),
      fetch(new URL('/ready', API_BASE_URL), { cache: 'no-store' }),
    ]);

    const health = await healthResponse.json();
    const ready = await readyResponse.json();

    return {
      connected: true,
      healthy: healthResponse.ok && health?.status === 'healthy',
      ready: readyResponse.ok && ready?.ready === true,
      label: readyResponse.ok ? 'Backend Live' : 'Backend Degraded',
      detail: readyResponse.ok ? 'API + DB reachable' : 'API status unavailable',
    };
  } catch {
    return {
      connected: false,
      healthy: false,
      ready: false,
      label: 'Demo Mode',
      detail: 'Using local fallback data',
    };
  }
}

export async function fetchDashboardOverview() {
  try {
    const response = await fetch(new URL('/api/v1/dashboard/overview', API_BASE_URL), { cache: 'no-store' });
    if (!response.ok) {
      throw new Error('Dashboard overview unavailable');
    }

    return await response.json();
  } catch {
    return null;
  }
}
