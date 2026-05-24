"use client";

import { useEffect, useMemo, useState } from 'react';
import { motion } from '@/lib/motion-shim';
import { Menu, ShieldCheck, Sparkles, X, Wifi, ChevronRight } from 'lucide-react';
import { fetchPlatformStatus, type PlatformStatus } from '@/lib/platform-status';

export default function Header() {
  const [scrollProgress, setScrollProgress] = useState(0);
  const [menuOpen, setMenuOpen] = useState(false);
  const [platformStatus, setPlatformStatus] = useState<PlatformStatus>({
    connected: false,
    healthy: false,
    ready: false,
    label: 'Checking…',
    detail: 'Verifying platform status',
  });

  useEffect(() => {
    const onScroll = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const nextProgress = max > 0 ? window.scrollY / max : 0;
      setScrollProgress(Math.min(1, Math.max(0, nextProgress)));
    };

    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    let mounted = true;
    void fetchPlatformStatus().then((status) => {
      if (mounted) {
        setPlatformStatus(status);
      }
    });

    return () => {
      mounted = false;
    };
  }, []);

  const statusColor = useMemo(() => {
    if (platformStatus.ready) return 'bg-white';
    if (platformStatus.connected) return 'bg-slate-300';
    return 'bg-slate-600';
  }, [platformStatus]);

  const statusLabel = platformStatus.connected ? platformStatus.label : 'Demo Mode';

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-black/70 backdrop-blur-md">
      <motion.div className="h-[2px] bg-gradient-to-r from-white via-slate-300 to-slate-600" style={{ scaleX: scrollProgress, transformOrigin: '0% 50%' }} />

      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-6 py-4">
        <a href="#hero" className="flex items-center gap-3">
          <div className="rounded-2xl bg-white/5 p-2 ring-1 ring-white/10">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="text-sm font-semibold tracking-wide text-white">Evijnar</div>
            <div className="text-xs text-slate-400">Global Health Arbitrage Exchange</div>
          </div>
        </a>

        <nav className="hidden items-center gap-6 text-sm text-slate-300 md:flex">
          <a href="#hero" className="transition hover:text-white">Home</a>
          <a href="#nexus" className="transition hover:text-white">Data Nexus</a>
          <a href="#recovery" className="transition hover:text-white">Recovery Bridge</a>
          <a href="#financing" className="transition hover:text-white">Rural UPI</a>
        </nav>

        <div className="flex items-center gap-3">
          <div className="hidden items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-2 text-xs text-slate-300 md:inline-flex">
            <span className={`h-2.5 w-2.5 rounded-full ${statusColor} shadow-[0_0_20px_rgba(255,255,255,0.18)]`} />
            <span>{statusLabel}</span>
            <span className="text-slate-500">•</span>
            <span>{platformStatus.detail}</span>
          </div>

          <button
            className="inline-flex rounded-full border border-white/10 bg-white/5 p-2 md:hidden"
            aria-label="Menu"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((value) => !value)}
          >
            {menuOpen ? <X className="h-5 w-5 text-slate-200" /> : <Menu className="h-5 w-5 text-slate-200" />}
          </button>
          <motion.a whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} href="#nexus" className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-black shadow-[0_0_30px_rgba(255,255,255,0.12)]">
            Access Platform
          </motion.a>
        </div>
      </div>
      {menuOpen ? (
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          className="border-t border-white/10 bg-black/95 px-6 py-4 md:hidden"
        >
          <div className="mx-auto max-w-7xl space-y-3 text-sm text-slate-300">
            {[
              { href: '#hero', label: 'Home' },
              { href: '#nexus', label: 'Data Nexus' },
              { href: '#recovery', label: 'Recovery Bridge' },
              { href: '#financing', label: 'Rural UPI' },
            ].map((item) => (
              <a key={item.href} href={item.href} onClick={() => setMenuOpen(false)} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 transition hover:border-white/20 hover:bg-white/10">
                <span>{item.label}</span>
                <ChevronRight className="h-4 w-4 text-slate-500" />
              </a>
            ))}
              <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-xs text-slate-300">
              <Wifi className="h-4 w-4 text-white" />
              <span>{statusLabel}</span>
              <span className="text-slate-500">•</span>
              <span>{platformStatus.detail}</span>
            </div>
          </div>
        </motion.div>
      ) : null}
      <div className="border-t border-white/5 px-6 py-2 text-center text-[11px] uppercase tracking-[0.35em] text-slate-400 md:hidden">
        <div className="inline-flex items-center gap-2"><ShieldCheck className="h-3.5 w-3.5 text-white" /> Cyber-Medical Nexus</div>
      </div>
    </header>
  );
}
