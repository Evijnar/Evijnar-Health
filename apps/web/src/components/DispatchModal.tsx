"use client";

import React, { useEffect, useRef, useState } from 'react';
import { motion, useReducedMotion } from '../lib/motion-shim';
import { ArrowRight } from 'lucide-react';
import { MOTION } from '../lib/theme';

export default function DispatchModal({ open, onClose, title = 'Automated Escalation', body = '' }: { open: boolean; onClose: () => void; title?: string; body?: string }) {
  const btnRef = useRef<HTMLButtonElement | null>(null);
  const [count, setCount] = useState(5);
  const reduce = useReducedMotion();

  useEffect(() => {
    if (!open) return;
    setCount(5);
    const t = setInterval(() => setCount((c) => c - 1), 1000);
    return () => clearInterval(t);
  }, [open]);

  useEffect(() => {
    if (open && btnRef.current) btnRef.current.focus();
  }, [open]);

  useEffect(() => {
    if (count <= 0 && open) {
      // simulate completion then auto-close
      setTimeout(() => onClose(), 800);
    }
  }, [count, open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" role="dialog" aria-modal="true">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={reduce ? { duration: 0.12 } : MOTION.spring}
        className="relative z-10 w-full max-w-lg rounded-2xl border border-white/10 bg-white/6 p-6 shadow-[0_24px_80px_rgba(2,6,23,0.6)]"
      >
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <p className="mt-2 text-sm text-slate-300">{body}</p>

        <div className="mt-4 flex items-center justify-between">
          <div className="text-xs text-slate-400">Dispatching to Tier-2 • ETA</div>
          <div className="text-2xl font-mono font-semibold text-white">{count}s</div>
        </div>

        <div className="mt-6 flex items-center justify-end gap-3">
          <button ref={btnRef} onClick={onClose} className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/90" aria-label="Close dispatch modal">
            Cancel
          </button>
          <button onClick={onClose} className="primary-action inline-flex items-center gap-2" aria-label="Acknowledge dispatch">
            Acknowledge <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </motion.div>
    </div>
  );
}
