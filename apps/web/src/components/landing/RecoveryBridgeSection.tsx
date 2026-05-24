"use client";

import { useEffect, useState } from 'react';
import { motion } from '@/lib/motion-shim';
import { Bolt, HeartPulse } from 'lucide-react';
import SectionHeading from './SectionHeading';
import { escalateRecoveryAlert } from '@/lib/evijnar-api';

export default function RecoveryBridgeSection() {
  const [alertActive, setAlertActive] = useState(false);
  const [phase, setPhase] = useState(0);
  const [apiState, setApiState] = useState<'idle' | 'sending' | 'sent' | 'demo'>('idle');

  useEffect(() => {
    const id = window.setInterval(() => {
      setPhase((value) => (value + 1) % 120);
    }, 80);
    return () => window.clearInterval(id);
  }, []);

  async function triggerAlert() {
    setAlertActive(true);
    setApiState('sending');
    const escalated = await escalateRecoveryAlert();
    setApiState(escalated ? 'sent' : 'demo');

    window.setTimeout(() => {
      setAlertActive(false);
      setApiState('idle');
    }, 4000);
  }

  const wavePoints = Array.from({ length: 96 }, (_, index) => {
    const x = (index / 95) * 600;
    const base = 82 + Math.sin((index + phase) / 4.5) * (alertActive ? 36 : 18);
    const spike = alertActive && index % 26 === 0 ? -28 : 0;
    const y = base + spike;
    return `${x},${y}`;
  }).join(' ');

  return (
    <section id="recovery" className="border-y border-white/10 bg-[#070B16] py-24">
      <div className="mx-auto max-w-7xl px-6">
        <SectionHeading
          eyebrow="IoMT Recovery Bridge"
          title="A monochrome live-ops monitoring surface"
          subtitle="Waveforms, vital telemetry, and escalation controls tuned for a black-and-white interface."
        />

        <div className="mt-12 grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={`rounded-[2rem] border border-white/10 bg-black/25 p-6 backdrop-blur-xl ${alertActive ? 'ring-2 ring-white/60 shadow-[0_0_60px_rgba(255,255,255,0.14)]' : ''}`}
          >
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="rounded-2xl bg-white/10 p-3 text-white ring-1 ring-white/15">
                  <HeartPulse className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white">Recovery Telemetry</h3>
                  <p className="text-sm text-slate-400">Heart rate + SpO2 preview</p>
                </div>
              </div>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onHoverStart={() => setAlertActive(true)}
                onHoverEnd={() => setAlertActive(false)}
                onClick={() => void triggerAlert()}
                className={`rounded-full px-5 py-3 text-sm font-semibold transition ${alertActive ? 'bg-white text-black shadow-[0_0_40px_rgba(255,255,255,0.18)]' : 'border border-white/10 bg-white/[0.04] text-white'}`}
              >
                Simulate Alert
              </motion.button>
            </div>

            <div className="mt-8 grid gap-6 md:grid-cols-[1.25fr_0.75fr]">
              <div className="rounded-[1.5rem] border border-white/10 bg-[#050812] p-4">
                <svg viewBox="0 0 600 160" className="h-48 w-full overflow-visible">
                  <defs>
                    <linearGradient id="wave" x1="0" x2="1">
                      <stop offset="0%" stopColor="#ffffff" />
                      <stop offset="100%" stopColor="#a1a1aa" />
                    </linearGradient>
                  </defs>
                  <motion.polyline
                    fill="none"
                    stroke="url(#wave)"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    animate={{ points: wavePoints }}
                    transition={{ duration: 0.2 }}
                  />
                </svg>
              </div>

              <div className="grid gap-3">
                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-center">
                  <div className="text-xs uppercase tracking-[0.3em] text-slate-400">Heart Rate</div>
                  <div className="mt-2 text-4xl font-black text-white">{Math.round(alertActive ? 142 : 78)}</div>
                  <div className="mt-1 text-xs text-slate-400">bpm</div>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-center">
                  <div className="text-xs uppercase tracking-[0.3em] text-slate-400">SpO2</div>
                  <div className="mt-2 text-4xl font-black text-white">{alertActive ? 87 : 98}%</div>
                  <div className="mt-1 text-xs text-slate-400">oxygen saturation</div>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="rounded-[2rem] border border-white/10 bg-white/5 p-6 backdrop-blur-xl"
          >
            <div className="flex items-center gap-2 text-sm font-semibold text-white">
              <Bolt className="h-4 w-4 text-white" />
              Escalation Feed
            </div>

            <div className="mt-4 space-y-3 text-sm text-slate-300">
              <div className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3">Step 01 • Wearable packet received</div>
              <div className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3">Step 02 • Threshold breach checked</div>
              <div className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3">Step 03 • Tier-2 cardiac team notified</div>
            </div>

            <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-sm text-slate-200">
              {apiState === 'sent' && 'Escalation dispatched via backend endpoint.'}
              {apiState === 'sending' && 'Dispatching escalation to backend...' }
              {apiState === 'demo' && 'Demo mode active: backend credentials not set, local escalation visualized.'}
              {apiState === 'idle' && 'Automated escalation remains visible for critical alerts with audit logging and PHI-safe routing.'}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
