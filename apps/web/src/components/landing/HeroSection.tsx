"use client";

import { useEffect, useState } from 'react';
import { motion } from '@/lib/motion-shim';
import { ArrowRight, Database, HeartPulse, ShieldCheck } from 'lucide-react';

const ingestionFrames = [
  'HHS USA -> CPT 33533 -> Normalizing...',
  'EHDS EU -> ICD-10 I25.10 -> Mapping...',
  'ABDM India -> UHI CABG -> Price delta computed...',
  'HHS USA -> CPT 27447 -> Normalizing...',
  'EHDS EU -> CPT 47562 -> Success-adjusted value updated...',
];

export default function HeroSection() {
  const [tickerIndex, setTickerIndex] = useState(0);

  useEffect(() => {
    const id = window.setInterval(() => {
      setTickerIndex((prev) => (prev + 1) % ingestionFrames.length);
    }, 2200);
    return () => window.clearInterval(id);
  }, []);

  return (
    <section id="hero" className="relative flex min-h-screen items-center overflow-hidden">
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_50%_20%,rgba(255,255,255,0.10),transparent_20%),radial-gradient(circle_at_20%_80%,rgba(255,255,255,0.06),transparent_24%),linear-gradient(180deg,#000000_0%,#070707_100%)]" />

      <motion.div
        className="absolute -top-28 left-[-10%] h-[55vw] w-[55vw] rounded-full blur-3xl"
        animate={{ x: ['0%', '10%', '0%'], y: ['0%', '4%', '0%'] }}
        transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
        style={{ background: 'radial-gradient(circle, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.04) 30%, transparent 70%)' }}
      />

      <motion.div
        className="absolute bottom-[-20%] right-[-10%] h-[45vw] w-[45vw] rounded-full blur-3xl"
        animate={{ x: ['0%', '-8%', '0%'], y: ['0%', '-3%', '0%'] }}
        transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut' }}
        style={{ background: 'radial-gradient(circle, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 25%, transparent 70%)' }}
      />

      <div className="mx-auto flex w-full max-w-6xl flex-col items-center px-6 py-24 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-xs uppercase tracking-[0.36em] text-slate-300"
        >
          <ShieldCheck className="h-4 w-4 text-white" />
          Cyber-Medical Nexus
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.8 }}
          className="mt-8 max-w-5xl text-5xl font-black tracking-tight text-white sm:text-6xl md:text-7xl lg:text-8xl"
        >
          <motion.span animate={{ y: [0, -8, 0] }} transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }} className="block">
            Global Health Arbitrage
          </motion.span>
          <span className="block text-white/80">Exchange</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.7 }}
          className="mt-6 max-w-3xl text-sm leading-7 text-slate-300 sm:text-base md:text-lg"
        >
          Compare hospital cost, quality, and recovery safety across borders with live ingestion, success-adjusted ranking, IoMT monitoring, and rural financing.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.7 }}
          className="mt-8 flex flex-wrap items-center justify-center gap-3"
        >
          <motion.a whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} href="#nexus" className="inline-flex items-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-semibold text-black shadow-[0_0_30px_rgba(255,255,255,0.18)]">
            Explore live dashboard <ArrowRight className="h-4 w-4" />
          </motion.a>
          <motion.a whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} href="#recovery" className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-semibold text-white/90">
            Recovery Bridge <HeartPulse className="h-4 w-4" />
          </motion.a>
        </motion.div>

        <div className="mt-14 w-full overflow-hidden rounded-2xl border border-white/10 bg-white/[0.04] backdrop-blur-md">
          <motion.div animate={{ x: ['0%', '-50%'] }} transition={{ duration: 24, repeat: Infinity, ease: 'linear' }} className="flex whitespace-nowrap py-3 font-mono text-xs uppercase tracking-[0.28em] text-slate-300">
            {Array.from({ length: 2 }).map((_, groupIndex) => (
              <div key={groupIndex} className="flex gap-8 px-8">
                {ingestionFrames.map((item, index) => (
                  <span key={`${groupIndex}-${index}`} className="inline-flex items-center gap-2">
                    <Database className="h-3.5 w-3.5 text-white" />
                    {item}
                  </span>
                ))}
              </div>
            ))}
          </motion.div>
          <div className="border-t border-white/5 px-6 py-2 text-[11px] uppercase tracking-[0.28em] text-slate-500">Live stream frame {tickerIndex + 1} of {ingestionFrames.length}</div>
        </div>
      </div>
    </section>
  );
}
