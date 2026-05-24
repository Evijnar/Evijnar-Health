"use client";

import { useEffect, useMemo, useState } from 'react';
import { motion } from '@/lib/motion-shim';
import { Bolt, Globe2, Hospital, Search } from 'lucide-react';
import SectionHeading from './SectionHeading';
import { fetchDashboardOverview, fetchHospitalSearch, type HospitalCard } from '@/lib/evijnar-api';

const DEFAULT_PROCEDURES = ['33533', '27447', '47562'];

function scoreLabel(score: number) {
  return `${score.toFixed(2)}`;
}

export default function DataNexusSection() {
  const [procedureCode, setProcedureCode] = useState(DEFAULT_PROCEDURES[0]);
  const [country, setCountry] = useState('All');
  const [cards, setCards] = useState<HospitalCard[]>([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [arbitrageOpportunity, setArbitrageOpportunity] = useState<number | null>(null);

  const canFetch = useMemo(() => Boolean(procedureCode.trim()), [procedureCode]);

  async function runSearch() {
    if (!canFetch) return;
    setLoading(true);
    const result = await fetchHospitalSearch(procedureCode, country);
    setCards(result.cards);
    setConnected(result.connected);
    setLoading(false);
  }

  useEffect(() => {
    let mounted = true;
    void fetchDashboardOverview().then((overview) => {
      if (!mounted || !overview) return;
      const market = overview.market as { arbitrage_opportunity_usd?: number } | undefined;
      if (market?.arbitrage_opportunity_usd) {
        setArbitrageOpportunity(market.arbitrage_opportunity_usd);
      }
    });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    void runSearch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section id="nexus" className="mx-auto max-w-7xl px-6 py-24">
      <SectionHeading
        eyebrow="Data Nexus"
        title="Hospital search and arbitrage intelligence"
        subtitle="Search procedural codes, compare cross-border price gaps, and rank providers by value, quality, and risk."
      />

      <div className="mt-12 grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
        <motion.div
          initial={{ opacity: 0, x: -24 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="rounded-[2rem] border border-white/10 bg-white/5 p-6 backdrop-blur-xl"
        >
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-white/10 p-3 text-white ring-1 ring-white/15">
              <Search className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-white">Procedure Search</h3>
              <p className="text-sm text-slate-400">Live backend search with fallback arbitrage data</p>
            </div>
          </div>

          <div className="mt-8 space-y-5">
            <label className="block space-y-2">
              <span className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-400">Procedure Code</span>
              <input
                value={procedureCode}
                onChange={(event) => setProcedureCode(event.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-black px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-white/30"
              />
            </label>

            <label className="block space-y-2">
              <span className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-400">Country</span>
              <select
                value={country}
                onChange={(event) => setCountry(event.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-black px-4 py-3 text-sm text-white outline-none transition focus:border-white/30"
              >
                <option>All</option>
                <option>US</option>
                <option>IN</option>
                <option>DE</option>
              </select>
            </label>

            <div className="flex flex-wrap gap-3 pt-2">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => void runSearch()}
                className="inline-flex items-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-semibold text-black shadow-[0_0_25px_rgba(255,255,255,0.12)]"
              >
                Run Arbitration <Bolt className="h-4 w-4" />
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-semibold text-white"
              >
                Compare Markets <Globe2 className="h-4 w-4" />
              </motion.button>
            </div>

            <div className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-xs uppercase tracking-[0.3em] text-slate-400">
              Backend connection {connected ? 'live' : 'demo'} {loading ? ' • refreshing...' : ''}
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-slate-200">
              Live arbitrage opportunity: <span className="font-mono text-white">${arbitrageOpportunity?.toLocaleString() ?? '46,100'}</span>
            </div>
          </div>
        </motion.div>

        <div className="grid gap-4">
          <motion.div
            variants={{ hidden: {}, show: { transition: { staggerChildren: 0.08 } } }}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, margin: '-100px' }}
            className="grid gap-4"
          >
            {cards.map((hospital) => (
              <motion.article
                key={hospital.id}
                variants={{ hidden: { opacity: 0, x: 60 }, show: { opacity: 1, x: 0 } }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="rounded-[1.75rem] border border-white/10 bg-white/5 p-5 backdrop-blur-xl"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <Hospital className="h-4 w-4 text-white" />
                      <h4 className="text-lg font-semibold text-white">{hospital.name}</h4>
                    </div>
                    <p className="mt-2 text-sm text-slate-400">
                      {hospital.city} • {hospital.country} • Success {(hospital.success * 100).toFixed(1)}%
                    </p>
                  </div>

                  <div className="text-right">
                    <div className="font-mono text-xl text-white">${hospital.price.toLocaleString()}</div>
                    <div className="mt-1 text-xs uppercase tracking-[0.28em] text-slate-500">Score {scoreLabel(hospital.score)}</div>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-3 gap-3 text-xs text-slate-300">
                  <div className="rounded-2xl border border-white/6 bg-black/20 px-3 py-2">Quality {hospital.quality.toFixed(1)}</div>
                  <div className="rounded-2xl border border-white/6 bg-black/20 px-3 py-2">Risk {(hospital.complication * 100).toFixed(1)}%</div>
                  <div className="rounded-2xl border border-white/6 bg-black/20 px-3 py-2">Savings ${(hospital.savingsUsd ?? 0).toLocaleString()}</div>
                </div>
              </motion.article>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
