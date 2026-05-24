"use client";

import React, { useEffect, useState } from 'react';
import { motion } from '../lib/motion-shim';
import { Database, Globe2 } from 'lucide-react';

const SOURCES = [
  { id: 'HHS', label: 'HHS (USA)', color: '#ffffff' },
  { id: 'EHDS', label: 'EHDS (EU)', color: '#e5e5e5' },
  { id: 'ABDM', label: 'ABDM (India)', color: '#bdbdbd' },
];

const EXAMPLES = [
  'normalized_price -> $8,500',
  'mapped_cpt -> 27447 (Knee arthroplasty)',
  'us_median_cost -> $45,200',
  'checksum -> OK',
  'currency -> USD',
];

function scrambleText(text: string) {
  // Simple scrambling effect generator
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  return text
    .split('')
    .map((ch) => (Math.random() > 0.6 ? letters[Math.floor(Math.random() * letters.length)] : ch))
    .join('');
}

export default function Ticker() {
  const [feed, setFeed] = useState<{ source: string; message: string; id: string }[]>([]);

  useEffect(() => {
    let mounted = true;
    const interval = setInterval(() => {
      if (!mounted) return;
      const src = SOURCES[Math.floor(Math.random() * SOURCES.length)];
      const msg = EXAMPLES[Math.floor(Math.random() * EXAMPLES.length)];
      const entry = { source: src.label, message: msg, id: `${Date.now()}-${Math.random()}` };
      setFeed((f) => [entry, ...f].slice(0, 6));
    }, 1400);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="glass-panel p-4" role="region" aria-label="Global ingestion feed">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-white/[0.06] p-2 ring-1 ring-white/10">
            <Database className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="text-xs font-semibold text-white">Global ingestion feed</div>
            <div className="text-sm text-slate-300">Live normalized events from transparency sources</div>
          </div>
        </div>
        <div className="text-xs text-slate-400">Simulated</div>
      </div>

      <div className="mt-3 space-y-2">
        {feed.map((f, idx) => (
          <motion.div
            key={f.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ type: 'spring', stiffness: 300, damping: 28, delay: idx * 0.02 }}
            className="flex items-center gap-3 rounded-lg border border-white/6 bg-white/[0.03] px-3 py-2"
            role="article"
            aria-live="polite"
          >
            <div className="h-8 w-8 flex-shrink-0 rounded-md bg-white/[0.06]">
              <Globe2 className="m-2 h-4 w-4 text-white" />
            </div>
            <div className="flex-1">
              <div className="flex items-baseline justify-between">
                <div className="font-mono text-sm font-semibold text-white">{f.source}</div>
                <div className="text-xs text-slate-400">{new Date().toLocaleTimeString()}</div>
              </div>
              <div className="mt-1 flex items-center gap-2">
                <div className="font-mono text-sm text-slate-100">{scrambleText(f.message)}</div>
                <div className="text-xs text-slate-400">→</div>
                <div className="text-sm font-semibold text-white">{f.message.match(/\$[0-9,]+/)?.[0] ?? f.message}</div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
