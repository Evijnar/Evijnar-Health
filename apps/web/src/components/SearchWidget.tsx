"use client";

import React, { useEffect, useMemo, useState } from 'react';
import { motion, AnimatePresence } from '../lib/motion-shim';
import clsx from 'clsx';

const PROCEDURES = [
  { code: '27447', title: 'Total knee replacement' },
  { code: '47562', title: 'Laparoscopic cholecystectomy' },
  { code: '33533', title: 'CABG - Coronary artery bypass' },
];

const MOCK_HOSPITALS = [
  { id: 'us-1', name: 'Mayo Clinic', country: 'US', price: 57400, success: 0.968, complication: 0.021 },
  { id: 'in-1', name: 'Apollo Delhi', country: 'IN', price: 11300, success: 0.987, complication: 0.013 },
  { id: 'de-1', name: 'Charite Berlin', country: 'DE', price: 21600, success: 0.978, complication: 0.015 },
];

function computeScore({ price, success, complication }: { price: number; success: number; complication: number }, costWeight: number, riskWeight: number) {
  // Simplified Score: higher is better
  const priceScore = 1 / (price / 10000);
  const successScore = success;
  const riskScore = 1 - complication;

  // costWeight + riskWeight + qualityWeight = 1
  const qualityWeight = Math.max(0, 1 - costWeight - riskWeight);

  return priceScore * costWeight + successScore * qualityWeight + riskScore * riskWeight;
}

export default function SearchWidget() {
  const [selected, setSelected] = useState(PROCEDURES[0]);
  const [costWeight, setCostWeight] = useState(0.4);
  const [riskWeight, setRiskWeight] = useState(0.3);

  const ranked = useMemo(() => {
    const list = MOCK_HOSPITALS.map((h) => ({ ...h, score: computeScore(h as any, costWeight, riskWeight) }));
    list.sort((a, b) => b.score - a.score);
    return list;
  }, [costWeight, riskWeight, selected]);

  return (
    <div className="glass-panel p-5" role="region" aria-label="Success adjusted value search">
      <div className="flex items-center justify-between">
          <div>
          <div className="text-xs font-semibold text-white">Success-Adjusted Value</div>
          <div className="text-sm text-slate-300">Interactive re-ranking by weight sliders</div>
        </div>
        <div className="flex items-center gap-2">
          <label className="sr-only" htmlFor="procedure-select">Procedure</label>
          <select id="procedure-select" className="rounded-md border border-white/10 bg-white/[0.04] px-3 py-2 text-sm text-white" value={selected.code} onChange={(e) => setSelected(PROCEDURES.find((p) => p.code === e.target.value) || PROCEDURES[0])} aria-label="Select procedure">
            {PROCEDURES.map((p) => (
              <option key={p.code} value={p.code}>{p.title}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className="p-3">
          <label className="text-xs text-slate-300">Cost Weight {Math.round(costWeight * 100)}%</label>
          <input type="range" min={0} max={1} step={0.05} value={costWeight} onChange={(e) => setCostWeight(Number(e.target.value))} className="w-full mt-2" />
          <label className="text-xs text-slate-300">Risk Weight {Math.round(riskWeight * 100)}%</label>
          <input type="range" min={0} max={1} step={0.05} value={riskWeight} onChange={(e) => setRiskWeight(Number(e.target.value))} className="w-full mt-2" />
        </div>

          <div className="p-3">
          <div className="space-y-3">
            <AnimatePresence>
              {ranked.map((h, idx) => (
                <motion.div key={h.id} initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ type: 'spring', stiffness: 300, damping: 28, delay: idx * 0.02 }} className={clsx('flex items-center justify-between gap-3 rounded-lg px-3 py-2', idx === 0 ? 'bg-white/[0.07] ring-1 ring-white/15' : 'bg-white/[0.03]')}>
                  <div>
                    <div className="text-sm font-semibold text-white">{h.name}</div>
                    <div className="text-xs text-slate-300">{h.country} • success {(h.success * 100).toFixed(1)}%</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-mono text-white">${h.price.toLocaleString()}</div>
                    <div className="text-xs text-slate-300">score {h.score.toFixed(3)}</div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      </div>

      <div className="mt-4 h-28 w-full overflow-hidden rounded-lg border border-white/6 bg-gradient-to-br from-black/10 to-white/[0.04] p-3">
        <div className="relative h-full">
          {/* radial comparison wheel */}
          <svg viewBox="0 0 200 200" className="mx-auto block h-full w-full">
            <defs>
              <linearGradient id="g1" x1="0" x2="1">
                <stop offset="0%" stopColor="#ffffff" />
                <stop offset="100%" stopColor="#a1a1aa" />
              </linearGradient>
            </defs>
            <g transform="translate(100,100)">
              {ranked.map((h, i) => {
                const angle = (i / ranked.length) * Math.PI * 2;
                const r = 44 + i * 8;
                const x = Math.cos(angle) * r;
                const y = Math.sin(angle) * r;
                return (
                  <g key={h.id} opacity={i === 0 ? 1 : 0.8}>
                    <motion.circle cx={x} cy={y} r={12} fill={i === 0 ? '#ffffff' : '#d4d4d8'} initial={{ r: 6 }} animate={{ r: 12 }} transition={{ type: 'spring', stiffness: 260, damping: 24 }} />
                    <text x={x} y={y + 28} fontSize={8} textAnchor="middle" fill="#e5e7eb">{h.country}</text>
                  </g>
                );
              })}
            </g>
          </svg>
        </div>
      </div>
    </div>
  );
}
