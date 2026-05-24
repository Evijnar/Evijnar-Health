"use client";

import { useMemo, useState } from 'react';
import { motion } from '@/lib/motion-shim';
import { CreditCard } from 'lucide-react';
import SectionHeading from './SectionHeading';

function computeEemi(principal: number, months: number, annualRate = 0.12) {
  const r = annualRate / 12;
  const n = months;
  const denom = 1 - Math.pow(1 + r, -n);
  return Math.round(denom > 0 ? principal * (r / denom) : principal / n);
}

export default function FinancingSection() {
  const [procedureCost, setProcedureCost] = useState(20000);
  const [months, setMonths] = useState(6);

  const emi = useMemo(() => computeEemi(procedureCost, months), [procedureCost, months]);

  return (
    <section id="financing" className="mx-auto max-w-7xl px-6 py-24">
      <SectionHeading
        eyebrow="Rural UPI Financing"
        title="Loan calculator with animated approval timeline"
        subtitle="Adjust procedure cost to update monthly EMI and watch the approval path activate as the view scrolls into frame."
      />

      <div className="mt-12 grid gap-8 lg:grid-cols-[1fr_0.9fr]">
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
              <CreditCard className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-white">Procedure Cost Slider</h3>
              <p className="text-sm text-slate-400">Mock micro-financing engine</p>
            </div>
          </div>

          <div className="mt-8 space-y-5">
            <div>
              <div className="mb-3 flex items-center justify-between text-sm text-slate-300">
                <span>Procedure Cost</span>
                <span className="font-mono text-white">₹{procedureCost.toLocaleString()}</span>
              </div>
              <input
                aria-label="Procedure cost"
                type="range"
                min={2000}
                max={80000}
                step={100}
                value={procedureCost}
                onChange={(e) => setProcedureCost(Number(e.target.value))}
                className="h-2 w-full cursor-pointer appearance-none rounded-full bg-white/10 accent-white"
              />
            </div>

            <div>
              <div className="mb-3 flex items-center justify-between text-sm text-slate-300">
                <span>Tenure</span>
                <span className="font-mono text-white">{months} months</span>
              </div>
              <input
                aria-label="Loan tenure"
                type="range"
                min={3}
                max={24}
                step={1}
                value={months}
                onChange={(e) => setMonths(Number(e.target.value))}
                className="h-2 w-full cursor-pointer appearance-none rounded-full bg-white/10 accent-white"
              />
            </div>

            <div className="rounded-[1.5rem] border border-white/10 bg-black/20 p-5">
              <div className="text-xs uppercase tracking-[0.3em] text-slate-400">EMI per month</div>
              <div className="mt-2 text-4xl font-black text-white">₹{emi.toLocaleString()}</div>
              <div className="mt-2 text-sm text-slate-400">Estimated financing for the selected procedure cost.</div>
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
          <h3 className="text-xl font-semibold text-white">Approval Timeline</h3>
          <p className="mt-2 text-sm text-slate-400">Input → Auth → Route → Approved</p>

          <div className="mt-8 grid gap-5">
            {[
              { label: 'Input', detail: 'Patient cost capture' },
              { label: 'Auth', detail: 'UPI 2.0 authorization' },
              { label: 'Route', detail: 'Hospital routing and underwriting' },
              { label: 'Approved', detail: 'Micro-loan disbursed' },
            ].map((step, index) => (
              <motion.div
                key={step.label}
                initial={{ opacity: 0, x: 24 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: '-100px' }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                transition={{ delay: index * 0.06 }}
                className="flex items-start gap-4"
              >
                <div className="flex flex-col items-center pt-1">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-[#0A0F1D] text-xs font-semibold text-white">
                    0{index + 1}
                  </div>
                  {index < 3 ? <motion.div initial={{ height: 0 }} whileInView={{ height: 48 }} viewport={{ once: true, margin: '-100px' }} className="mt-2 w-px bg-gradient-to-b from-white to-slate-500" /> : null}
                </div>

                <div className="flex-1 rounded-[1.25rem] border border-white/10 bg-black/20 p-4">
                  <div className="font-semibold text-white">{step.label}</div>
                  <div className="mt-1 text-sm text-slate-400">{step.detail}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
