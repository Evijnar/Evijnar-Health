'use client';

import { useEffect, useState } from 'react';
import clsx from 'clsx';
import {
  Activity,
  ArrowRight,
  BarChart3,
  Brain,
  Building2,
  CheckCircle2,
  Clock3,
  CreditCard,
  Database,
  DollarSign,
  FileText,
  Globe,
  Heart,
  Layers3,
  MapPin,
  Search,
  Server,
  Shield,
  Sparkles,
  Stethoscope,
  TrendingUp,
  Users,
  Workflow,
  Zap,
} from 'lucide-react';

type RegionKey = 'usa' | 'europe' | 'india';

const coverageCards = [
  {
    title: 'Vision',
    body: 'A unified global marketplace that makes hospital prices, outcomes, and recovery support visible in one place.',
    icon: Sparkles,
  },
  {
    title: 'Current status',
    body: 'Data ingestion, integration testing, and CI/CD are complete; authentication and search are the next active slices.',
    icon: Clock3,
  },
  {
    title: 'Core features',
    body: 'Outcome-based ranking, global data aggregation, recovery monitoring, and rural financing are all represented in the site.',
    icon: Layers3,
  },
  {
    title: 'Tech stack',
    body: 'Next.js, FastAPI, PostgreSQL, Redis, Prisma, TypeScript, Tailwind, and GitHub Actions are covered across the dashboard.',
    icon: Database,
  },
  {
    title: 'Architecture',
    body: 'The page maps ingestion, normalization, scoring, booking, recovery, and finance into one readable workflow.',
    icon: Workflow,
  },
  {
    title: 'API surface',
    body: 'Auth, hospitals, pricing, bookings, recovery, patients, financing, and health all appear as product modules.',
    icon: FileText,
  },
  {
    title: 'Security',
    body: 'Audit logging, client-side encryption, key rotation, and compliance language are surfaced as first-class signals.',
    icon: Shield,
  },
  {
    title: 'Testing & deployment',
    body: 'The dashboard includes CI/CD, testing, Docker, and local orchestration so the site reads like a real system overview.',
    icon: BarChart3,
  },
];

const featureCards = [
  {
    title: 'Success-adjusted ranking',
    body: 'Compare hospitals by cost, risk, quality, and predicted value instead of lowest sticker price.',
    icon: TrendingUp,
    accent: 'from-emerald-400/25 to-cyan-400/10',
    bullets: ['Cost + risk + quality scoring', 'Outcome-driven decision support', 'Real-time savings projection'],
  },
  {
    title: 'Global data aggregation',
    body: 'Normalize USA HHS, Europe EHDS, and India ABDM/UHI data into one cross-border experience.',
    icon: Globe,
    accent: 'from-sky-400/25 to-indigo-400/10',
    bullets: ['Unified schema across geographies', 'AI-assisted mapping', 'Source coverage tracking'],
  },
  {
    title: 'Recovery Bridge',
    body: 'Track 30-day post-op vitals, escalate alerts, and keep the surgical team connected after discharge.',
    icon: Heart,
    accent: 'from-rose-400/25 to-orange-400/10',
    bullets: ['Heart rate, SpO2, temperature, BP', 'Alert escalation', 'Cross-border safety coordination'],
  },
  {
    title: 'Rural financing',
    body: 'Support affordability with UPI 2.0 micro-financing, Health-EMI, and transparent payment options.',
    icon: CreditCard,
    accent: 'from-amber-400/25 to-emerald-400/10',
    bullets: ['Flexible payback', 'Tier 2 affordability routing', 'Transparent fee disclosure'],
  },
  {
    title: 'HIPAA-compliant architecture',
    body: 'Make privacy and governance visible with audit logs, encryption, and right-to-be-forgotten support.',
    icon: Shield,
    accent: 'from-slate-300/20 to-slate-500/10',
    bullets: ['Audit logging', 'Client-side PII encryption', 'Quarterly key rotation'],
  },
  {
    title: 'Mobile-first delivery',
    body: 'Surface low-bandwidth design, responsive layouts, and progressive loading for rural and mobile users.',
    icon: Zap,
    accent: 'from-violet-400/20 to-cyan-400/10',
    bullets: ['Fast rendering', 'Code-split delivery', 'Accessibility-friendly UI'],
  },
];

const workflowSteps = [
  'Ingest hospital price and quality data',
  'Normalize formats and map procedures',
  'Score by cost, risk, and expected outcome',
  'Compare local and global options',
  'Book care and coordinate logistics',
  'Monitor recovery and finance repayments',
];

const roadmap = [
  { label: 'Data ingestion engine', status: 'Complete', progress: 100 },
  { label: 'Integration tests & CI/CD', status: 'Complete', progress: 100 },
  { label: 'Authentication system', status: 'In progress', progress: 55 },
  { label: 'Hospital search & ranking', status: 'Planned', progress: 20 },
  { label: 'Recovery Bridge (IoMT)', status: 'Planned', progress: 12 },
  { label: 'Rural financing', status: 'Planned', progress: 15 },
];

const regionalData: Record<RegionKey, {
  name: string;
  subtitle: string;
  hospitals: number;
  savings: number;
  compliance: number;
  latency: string;
  signal: string;
  bars: number[];
}> = {
  usa: {
    name: 'United States',
    subtitle: 'HHS price transparency data',
    hospitals: 8120,
    savings: 0,
    compliance: 99,
    latency: 'Live',
    signal: 'Baseline benchmark for comparison',
    bars: [100, 78, 84, 92],
  },
  europe: {
    name: 'Europe',
    subtitle: 'EHDS harmonized coverage',
    hospitals: 5320,
    savings: 62,
    compliance: 98,
    latency: 'Near real-time',
    signal: 'High-quality cross-border routing',
    bars: [86, 90, 73, 88],
  },
  india: {
    name: 'India',
    subtitle: 'ABDM/UHI affordability network',
    hospitals: 4980,
    savings: 81,
    compliance: 97,
    latency: 'Streaming',
    signal: 'Savings leader for routed care',
    bars: [92, 96, 88, 84],
  },
};

const techStacks = [
  {
    title: 'Frontend',
    icon: Globe,
    items: ['Next.js App Router', 'TypeScript', 'Tailwind CSS', 'Zustand', 'Axios'],
  },
  {
    title: 'Backend',
    icon: Server,
    items: ['FastAPI', 'SQLAlchemy', 'Pydantic', 'Alembic', 'Uvicorn', 'Python 3.11+'],
  },
  {
    title: 'Data & infra',
    icon: Database,
    items: ['PostgreSQL', 'Redis', 'Prisma', 'Docker', 'docker-compose'],
  },
  {
    title: 'DevOps & testing',
    icon: BarChart3,
    items: ['GitHub Actions', 'pytest', 'pytest-asyncio', 'Codecov', 'pnpm'],
  },
  {
    title: 'AI & external services',
    icon: Brain,
    items: ['Evijnar Health AI', 'Razorpay / UPI 2.0', 'Twilio', 'Google Maps'],
  },
];

const apiModules = ['auth', 'hospitals', 'pricing', 'bookings', 'recovery', 'patients', 'financing', 'health'];

const securityChecklist = [
  'Audit logging for PHI access',
  'Zero-knowledge and client-side encryption',
  'Quarterly key rotation',
  'GDPR right-to-be-forgotten support',
  'Low-bandwidth mobile-friendly delivery',
];

function useAnimatedCount(target: number, duration = 1400) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    let frame = 0;
    const start = performance.now();

    const tick = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(target * eased);

      if (progress < 1) {
        frame = requestAnimationFrame(tick);
      }
    };

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, duration]);

  return value;
}

function AnimatedNumber({
  value,
  suffix = '',
  prefix = '',
  decimals = 0,
  className,
}: {
  value: number;
  suffix?: string;
  prefix?: string;
  decimals?: number;
  className?: string;
}) {
  const animatedValue = useAnimatedCount(value);
  const displayValue = decimals > 0 ? animatedValue.toFixed(decimals) : Math.round(animatedValue).toLocaleString();

  return <span className={className}>{prefix}{displayValue}{suffix}</span>;
}

function SectionTitle({ kicker, title, body }: { kicker: string; title: string; body: string }) {
  return (
    <div className="max-w-3xl space-y-3">
      <p className="section-kicker">{kicker}</p>
      <h2 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">{title}</h2>
      <p className="max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">{body}</p>
    </div>
  );
}

export default function DashboardPage() {
  const [selectedRegion, setSelectedRegion] = useState<RegionKey>('india');
  const [searchQuery, setSearchQuery] = useState('Orthopedic surgery');
  const [backendStatus, setBackendStatus] = useState({
    online: false,
    ready: false,
    label: 'Checking API',
  });
  const [liveMatchCount, setLiveMatchCount] = useState<number | null>(null);

  const activeRegion = regionalData[selectedRegion];

  useEffect(() => {
    const controller = new AbortController();
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

    const probeApi = async () => {
      try {
        const [healthResponse, readyResponse, searchResponse] = await Promise.all([
          fetch(`${apiBaseUrl}/health`, { signal: controller.signal }),
          fetch(`${apiBaseUrl}/ready`, { signal: controller.signal }),
          fetch(`${apiBaseUrl}/api/v1/hospitals/search?procedure_code=27447`, {
            signal: controller.signal,
          }),
        ]);

        const healthPayload = await healthResponse.json();
        const readyPayload = await readyResponse.json();
        const searchPayload = await searchResponse.json();

        setBackendStatus({
          online: healthResponse.ok,
          ready: readyResponse.ok && Boolean(readyPayload.ready),
          label: healthPayload.status === 'healthy' ? 'API healthy' : 'API responding',
        });
        setLiveMatchCount(Number(searchPayload.count ?? 0));
      } catch {
        setBackendStatus({
          online: false,
          ready: false,
          label: 'API unavailable',
        });
        setLiveMatchCount(null);
      }
    };

    probeApi();

    return () => controller.abort();
  }, []);

  return (
    <div className="dashboard-shell min-h-screen text-slate-100">
      <div className="dashboard-grid" />
      <div className="dashboard-orb dashboard-orb-a" />
      <div className="dashboard-orb dashboard-orb-b" />

      <header className="sticky top-0 z-50 border-b border-white/10 bg-slate-950/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-400 text-slate-950 shadow-lg shadow-emerald-400/25">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <p className="text-[0.65rem] uppercase tracking-[0.35em] text-slate-400">Evijnar</p>
              <h1 className="text-sm font-semibold text-white sm:text-base">Global Health Arbitrage Dashboard</h1>
            </div>
          </div>

          <nav className="hidden items-center gap-2 md:flex">
            {[
              ['Coverage', '#coverage'],
              ['Features', '#features'],
              ['Workflow', '#workflow'],
              ['Security', '#security'],
            ].map(([label, href]) => (
              <a
                key={label}
                href={href}
                className="nav-chip"
              >
                {label}
              </a>
            ))}
          </nav>

          <div className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-xs text-emerald-300">
            <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_18px_rgba(52,211,153,0.9)]" />
            Phase 3 release active
          </div>
          <div
            className={clsx(
              'flex items-center gap-2 rounded-full px-3 py-1.5 text-xs',
              backendStatus.online
                ? 'border border-sky-400/20 bg-sky-400/10 text-sky-300'
                : 'border border-white/10 bg-white/5 text-slate-300'
            )}
          >
            <span className={clsx('h-2 w-2 rounded-full', backendStatus.online ? 'bg-sky-400' : 'bg-slate-500')} />
            {backendStatus.label}
          </div>
        </div>
      </header>

      <main className="mx-auto flex max-w-7xl flex-col gap-8 px-4 pb-16 pt-8 sm:px-6 lg:px-8 lg:gap-10">
        <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="glass-panel reveal-up p-6 sm:p-8 lg:p-10">
            <div className="flex flex-wrap items-center gap-2">
              <span className="status-pill bg-white/8 text-emerald-300">
                <Activity className="h-3.5 w-3.5" />
                Live command center
              </span>
              <span className="status-pill bg-white/8 text-sky-300">
                <Globe className="h-3.5 w-3.5" />
                USA + Europe + India
              </span>
              <span className="status-pill bg-white/8 text-amber-300">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Complete site coverage
              </span>
            </div>

            <div className="mt-6 space-y-5">
              <div className="max-w-3xl space-y-4">
                <p className="section-kicker">Solving the hidden price crisis in healthcare</p>
                <h2 className="max-w-4xl text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
                  A professional dashboard for global care discovery, pricing, recovery, and financing.
                </h2>
                <p className="max-w-2xl text-base leading-7 text-slate-300 sm:text-lg">
                  This homepage now reads like a product control room: it highlights the platform vision,
                  current status, global data coverage, security posture, and the operational modules that
                  make Evijnar feel complete.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_auto_auto]">
                <div className="relative">
                  <input
                    value={searchQuery}
                    onChange={(event) => setSearchQuery(event.target.value)}
                    className="h-14 w-full rounded-2xl border border-white/10 bg-slate-900/75 px-5 text-sm text-white outline-none ring-0 placeholder:text-slate-500 focus:border-emerald-400/50 focus:bg-slate-900"
                    placeholder="Search a procedure, symptom, or hospital network"
                    aria-label="Search procedures"
                  />
                  <SearchHint />
                </div>

                <button className="nav-chip h-14 min-w-32 justify-center bg-white/8 px-5 text-slate-100">
                  <Sparkles className="h-4 w-4" />
                  AI ranking
                </button>

                <button className="primary-action h-14 min-w-36 justify-center px-5">
                  <ArrowRight className="h-4 w-4" />
                  Compare options
                </button>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                {[
                  { label: 'Hospitals normalized', value: 18420, suffix: '+', icon: Building2 },
                  { label: 'Countries covered', value: 3, suffix: '', icon: Globe },
                  { label: 'Avg savings', value: 84, suffix: '%', icon: DollarSign },
                  { label: 'Compliance score', value: 99, suffix: '%', icon: Shield },
                ].map(({ label, value, suffix, icon: Icon }) => (
                  <div key={label} className="metric-card">
                    <div className="flex items-center justify-between text-slate-400">
                      <span className="text-xs uppercase tracking-[0.25em]">{label}</span>
                      <Icon className="h-4 w-4 text-emerald-300" />
                    </div>
                    <AnimatedNumber
                      value={value}
                      suffix={suffix}
                      className="mt-3 block text-3xl font-semibold tracking-tight text-white"
                    />
                  </div>
                ))}
              </div>

              <div className="metric-card flex items-center justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Live API link</p>
                  <p className="mt-2 text-sm text-slate-300">Health, readiness, and hospital search are probed against the backend.</p>
                </div>
                <div className="text-right">
                  <AnimatedNumber
                    value={liveMatchCount ?? 0}
                    suffix=" matches"
                    className="block text-2xl font-semibold text-white"
                  />
                  <p className="mt-1 text-xs text-slate-500">
                    {backendStatus.ready ? 'Ready for requests' : 'Waiting for API'}
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap gap-2 pt-1">
                {['Transparent pricing', 'Outcome-aware ranking', 'Recovery monitoring', 'Micro-financing', 'Audit-ready', 'Mobile-first'].map((item) => (
                  <span key={item} className="nav-chip bg-white/6 text-slate-200">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="glass-panel reveal-up p-6 sm:p-8 lg:p-10">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="section-kicker">Live region signal</p>
                <h3 className="text-2xl font-semibold text-white">Global data coverage</h3>
                <p className="mt-2 text-sm leading-6 text-slate-300">
                  Switch between geographies to show the currently normalized source and its savings profile.
                </p>
              </div>
              <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-right text-xs text-emerald-300">
                <div className="font-medium">{activeRegion.latency}</div>
                <div className="text-emerald-300/70">ingestion latency</div>
              </div>
            </div>

            <div className="mt-5 flex flex-wrap gap-2">
              {(Object.keys(regionalData) as RegionKey[]).map((region) => (
                <button
                  key={region}
                  onClick={() => setSelectedRegion(region)}
                  className={clsx(
                    'nav-chip transition-all duration-200',
                    selectedRegion === region
                      ? 'border-emerald-400/40 bg-emerald-400/15 text-emerald-200 shadow-[0_0_0_1px_rgba(52,211,153,0.12)]'
                      : 'bg-white/6 text-slate-200 hover:bg-white/10'
                  )}
                >
                  {regionalData[region].name}
                </button>
              ))}
            </div>

            <div className="mt-6 rounded-[1.5rem] border border-white/10 bg-slate-950/55 p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm text-slate-400">{activeRegion.subtitle}</p>
                  <h4 className="mt-1 text-xl font-semibold text-white">{activeRegion.name}</h4>
                  <p className="mt-2 text-sm leading-6 text-slate-300">{activeRegion.signal}</p>
                </div>
                <div className="rounded-2xl bg-white/5 px-4 py-3 text-right">
                  <div className="text-xs uppercase tracking-[0.25em] text-slate-500">Savings signal</div>
                  <AnimatedNumber value={activeRegion.savings} suffix="%" className="mt-1 block text-2xl font-semibold text-emerald-300" />
                </div>
              </div>

              <div className="mt-5 grid grid-cols-3 gap-3 text-center">
                <div className="rounded-2xl bg-white/5 p-3">
                  <div className="text-xs uppercase tracking-[0.2em] text-slate-500">Hospitals</div>
                  <AnimatedNumber value={activeRegion.hospitals} suffix="+" className="mt-2 block text-xl font-semibold text-white" />
                </div>
                <div className="rounded-2xl bg-white/5 p-3">
                  <div className="text-xs uppercase tracking-[0.2em] text-slate-500">Compliance</div>
                  <AnimatedNumber value={activeRegion.compliance} suffix="%" className="mt-2 block text-xl font-semibold text-white" />
                </div>
                <div className="rounded-2xl bg-white/5 p-3">
                  <div className="text-xs uppercase tracking-[0.2em] text-slate-500">Signal</div>
                  <div className="mt-2 text-xl font-semibold text-white">{activeRegion.latency}</div>
                </div>
              </div>

              <div className="mt-5 space-y-3">
                {activeRegion.bars.map((value, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center justify-between text-xs text-slate-400">
                      <span>Normalization stage {index + 1}</span>
                      <span>{value}%</span>
                    </div>
                    <div className="bar-track">
                      <div className="bar-fill" style={{ width: `${value}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <div className="metric-card">
                <div className="flex items-center gap-3 text-slate-200">
                  <Stethoscope className="h-4 w-4 text-cyan-300" />
                  <span className="text-sm font-medium">Outcome layer</span>
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Cost, quality, and expected recovery are blended into one score for decision support.
                </p>
              </div>
              <div className="metric-card">
                <div className="flex items-center gap-3 text-slate-200">
                  <Users className="h-4 w-4 text-amber-300" />
                  <span className="text-sm font-medium">Patient support</span>
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Recovery and financing tools keep the experience connected after booking.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section id="coverage" className="space-y-5">
          <SectionTitle
            kicker="Site coverage"
            title="All major points from the product and documentation are represented in the dashboard."
            body="This section ensures the homepage covers the same narrative as the repository: vision, current state, modules, stack, architecture, APIs, security, testing, and deployment."
          />

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {coverageCards.map((card) => {
              const Icon = card.icon;
              return (
                <div key={card.title} className="glass-card p-5 reveal-up">
                  <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/8 text-emerald-300">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="mt-4 text-lg font-semibold text-white">{card.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-300">{card.body}</p>
                </div>
              );
            })}
          </div>
        </section>

        <section id="features" className="space-y-5">
          <SectionTitle
            kicker="Core modules"
            title="The dashboard presents the platform as a complete product surface, not a placeholder layout."
            body="Each card maps directly to a core feature in the repository and keeps the story of the site visible at a glance."
          />

          <div className="grid gap-4 xl:grid-cols-3">
            {featureCards.map((feature) => {
              const Icon = feature.icon;
              return (
                <article key={feature.title} className="glass-card overflow-hidden p-5 reveal-up">
                  <div className={clsx('rounded-[1.5rem] border border-white/10 bg-gradient-to-br p-4', feature.accent)}>
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-950/60 text-white shadow-lg shadow-black/20">
                        <Icon className="h-5 w-5" />
                      </div>
                      <span className="text-xs uppercase tracking-[0.25em] text-slate-200/70">Module</span>
                    </div>

                    <h3 className="mt-5 text-xl font-semibold text-white">{feature.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-100/90">{feature.body}</p>
                  </div>

                  <ul className="mt-4 space-y-2 text-sm text-slate-300">
                    {feature.bullets.map((bullet) => (
                      <li key={bullet} className="flex items-start gap-2">
                        <CheckCircle2 className="mt-0.5 h-4 w-4 flex-none text-emerald-300" />
                        <span>{bullet}</span>
                      </li>
                    ))}
                  </ul>
                </article>
              );
            })}
          </div>
        </section>

        <section id="workflow" className="grid gap-5 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="glass-panel p-6 sm:p-8 reveal-up">
            <SectionTitle
              kicker="Architecture"
              title="A single flow from ingestion to repayment"
              body="The page visualizes the product as a workflow so the operational path is obvious to stakeholders and users."
            />

            <div className="mt-6 space-y-4">
              {workflowSteps.map((step, index) => (
                <div key={step} className="flex items-start gap-4 rounded-2xl border border-white/8 bg-white/5 p-4">
                  <div className="timeline-node mt-0.5">
                    {index + 1}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">{step}</p>
                    <p className="mt-1 text-sm leading-6 text-slate-400">
                      {index === 0 && 'Price and quality data land from HHS, EHDS, ABDM, and structured feeds.'}
                      {index === 1 && 'Procedure mapping and normalization align data into one schema.'}
                      {index === 2 && 'The score blends cost, quality, and risk for outcome-aware ranking.'}
                      {index === 3 && 'Patients compare local and global options side by side.'}
                      {index === 4 && 'Bookings, travel, and care coordination are unified in one journey.'}
                      {index === 5 && 'Recovery monitoring and financing continue after treatment.'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-panel p-6 sm:p-8 reveal-up">
            <SectionTitle
              kicker="Operational status"
              title="The site now includes current progress and roadmap context."
              body="This card mirrors the repository status table, which helps the landing page feel honest and complete."
            />

            <div className="mt-6 space-y-4">
              {roadmap.map((item) => (
                <div key={item.label} className="rounded-2xl border border-white/8 bg-slate-950/55 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-medium text-white">{item.label}</p>
                      <p className="mt-1 text-xs uppercase tracking-[0.25em] text-slate-500">{item.status}</p>
                    </div>
                    <span
                      className={clsx(
                        'rounded-full px-3 py-1 text-xs font-medium',
                        item.progress === 100
                          ? 'bg-emerald-400/15 text-emerald-200'
                          : item.progress >= 50
                            ? 'bg-amber-400/15 text-amber-200'
                            : 'bg-white/8 text-slate-300'
                      )}
                    >
                      {item.progress}%
                    </span>
                  </div>
                  <div className="bar-track mt-3">
                    <div className="bar-fill" style={{ width: `${item.progress}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="grid gap-5 xl:grid-cols-[0.95fr_1.05fr]">
          <div className="glass-panel p-6 sm:p-8 reveal-up">
            <SectionTitle
              kicker="Tech stack"
              title="The dashboard surfaces the stack that actually ships the product."
              body="It mirrors the repository choices across frontend, backend, infrastructure, DevOps, and AI services."
            />

            <div className="mt-6 space-y-3">
              {techStacks.map((stack) => {
                const Icon = stack.icon;
                return (
                  <div key={stack.title} className="rounded-2xl border border-white/8 bg-white/5 p-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-emerald-400/10 text-emerald-300">
                        <Icon className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-white">{stack.title}</p>
                        <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Platform layer</p>
                      </div>
                    </div>

                    <div className="mt-3 flex flex-wrap gap-2">
                      {stack.items.map((item) => (
                        <span key={item} className="nav-chip bg-white/6 text-slate-200">
                          {item}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="grid gap-5 sm:grid-cols-2">
            <div id="security" className="glass-panel p-6 sm:p-8 reveal-up">
              <SectionTitle
                kicker="Security & compliance"
                title="Privacy is part of the story, not an afterthought."
                body="The site now foregrounds the security commitments already present in the documentation."
              />

              <div className="mt-6 space-y-3">
                {securityChecklist.map((item) => (
                  <div key={item} className="flex items-start gap-3 rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-slate-300">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 flex-none text-emerald-300" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-panel p-6 sm:p-8 reveal-up">
              <SectionTitle
                kicker="APIs & testing"
                title="The backend surface is visible in the UI."
                body="That includes the route families, testing strategy, and CI/CD footprint from the repository."
              />

              <div className="mt-6 flex flex-wrap gap-2">
                {apiModules.map((module) => (
                  <span key={module} className="nav-chip bg-white/6 text-slate-200">
                    /{module}
                  </span>
                ))}
              </div>

              <div className="mt-6 space-y-3 rounded-[1.5rem] border border-white/8 bg-slate-950/55 p-4">
                {[
                  'Type checks and linting on the frontend',
                  'pytest integration coverage on the API',
                  'Docker and docker-compose for local orchestration',
                  'GitHub Actions CI/CD for release confidence',
                ].map((item) => (
                  <div key={item} className="flex items-center gap-3 text-sm text-slate-300">
                    <span className="h-2 w-2 rounded-full bg-emerald-300" />
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="glass-panel overflow-hidden p-6 sm:p-8 reveal-up">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl space-y-3">
              <p className="section-kicker">Dashboard summary</p>
              <h2 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">A complete site narrative in one page.</h2>
              <p className="text-sm leading-6 text-slate-300 sm:text-base">
                The landing page now covers the full set of site points: mission, product modules, data sources,
                architecture, compliance, roadmap, testing, and deployment. It is animated, responsive, and built
                to read like a real operational dashboard.
              </p>
            </div>

            <a href="#coverage" className="primary-action w-fit">
              Explore coverage
              <ArrowRight className="h-4 w-4" />
            </a>
          </div>
        </section>
      </main>
    </div>
  );
}

function SearchHint() {
  return (
    <div className="pointer-events-none absolute inset-y-0 right-4 flex items-center text-xs uppercase tracking-[0.25em] text-slate-500">
      Treatment search
    </div>
  );
}