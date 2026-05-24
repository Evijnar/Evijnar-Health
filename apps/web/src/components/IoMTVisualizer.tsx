"use client";

import React, { useEffect, useRef, useState } from 'react';
import { motion, useReducedMotion } from '../lib/motion-shim';
import { HeartPulse } from 'lucide-react';
import DispatchModal from './DispatchModal';
import { MOTION } from '../lib/theme';

function useWave(initial = 72) {
  const [value, setValue] = useState(initial);
  useEffect(() => {
    const iv = setInterval(() => {
      setValue((v) => {
        const next = v + (Math.random() * 4 - 2);
        return Math.max(50, Math.min(120, Math.round(next)));
      });
    }, 700);
    return () => clearInterval(iv);
  }, []);
  return [value, setValue] as const;
}

export default function IoMTVisualizer() {
  const [hr, setHr] = useWave(78);
  const [spo2, setSpo2] = useState(98);
  const [history, setHistory] = useState<number[]>([]);
  const [alerting, setAlerting] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const reduce = useReducedMotion();

  useEffect(() => {
    const h = [...history];
    h.push(hr);
    if (h.length > 60) h.shift();
    setHistory(h);
  }, [hr]);

  function triggerAlert() {
    // create an outlier and flash border
    setHr(140);
    setSpo2(86);
    setAlerting(true);
    setModalOpen(true);
    setTimeout(() => {
      setAlerting(false);
      setHr(84 + Math.round(Math.random() * 6));
      setSpo2(97 + Math.round(Math.random() * 1));
    }, 3000);
  }

  return (
    <div className={`glass-panel p-4 ${alerting ? 'ring-2 ring-white/60 animate-pulse' : ''}`} aria-live="polite">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-white/[0.06] p-2 ring-1 ring-white/10">
            <HeartPulse className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="text-xs font-semibold text-white">Recovery Bridge</div>
            <div className="text-sm text-slate-300">Live IoMT vitals preview (simulated)</div>
          </div>
        </div>
        <div>
          <button onClick={triggerAlert} className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-2 text-sm font-semibold text-white hover:bg-white/10">
            Trigger Alert Test
          </button>
        </div>
      </div>

          <div className="mt-3 flex gap-4">
        <div className="w-2/3">
          <div className="h-36 w-full overflow-hidden rounded-lg border border-white/6 bg-gradient-to-br from-black/5 to-white/3 p-2">
            <svg viewBox="0 0 600 120" preserveAspectRatio="none" className="h-full w-full">
              <polyline
                fill="none"
                stroke="#ffffff"
                strokeWidth={2}
                points={history.map((v, i) => `${(i / 60) * 600},${120 - (v - 40)} `).join('')}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <div className="mt-3 grid grid-cols-3 gap-3">
            <div className="rounded-xl bg-white/[0.03] p-3 text-center">
              <div className="text-xs text-slate-300">Heart Rate</div>
              <div className="mt-1 text-2xl font-mono font-semibold text-white">{hr} <span className="text-sm">bpm</span></div>
            </div>
            <div className="rounded-xl bg-white/[0.03] p-3 text-center">
              <div className="text-xs text-slate-300">SpO2</div>
              <div className="mt-1 text-2xl font-mono font-semibold text-white">{spo2}%</div>
            </div>
            <div className="rounded-xl bg-white/[0.03] p-3 text-center">
              <div className="text-xs text-slate-300">Respiratory</div>
              <div className="mt-1 text-2xl font-mono font-semibold text-slate-100">16</div>
            </div>
          </div>
        </div>

        <div className="w-1/3 space-y-3">
          <div className="rounded-xl bg-white/3 p-3">
            <div className="text-xs text-slate-300">Latest Events</div>
            <ul className="mt-2 space-y-1 text-sm text-slate-200">
              <li>Heart rate stabilised at <span className="font-mono text-white">{hr} bpm</span></li>
              <li>SpO2 nominal at <span className="font-mono text-white">{spo2}%</span></li>
              <li className="text-white/70">No critical alerts</li>
            </ul>
          </div>

          <motion.div layout className="rounded-xl bg-white/3 p-3" transition={reduce ? { duration: 0.08 } : MOTION.spring}>
            <div className="text-xs text-slate-300">Dispatch</div>
            <div className="mt-2 text-sm text-slate-200">Automated Escalation to Tier-2 Cardiac Care Team</div>
            <div className="mt-3 h-2 w-full rounded-full bg-white/5">
              <div className={`h-2 rounded-full bg-white`} style={{ width: alerting ? '100%' : '0%' }} />
            </div>
          </motion.div>
        </div>
      </div>
      <DispatchModal open={modalOpen} onClose={() => setModalOpen(false)} title="Automated Escalation to Tier-2 Cardiac Care Team" body="Dispatching nurses and cardiology team. Monitoring live vitals and routing to the nearest provider." />
    </div>
  );
}
