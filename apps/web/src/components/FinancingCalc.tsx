"use client";

import React, { useMemo, useState } from 'react';
import { motion } from '../lib/motion-shim';

function amortization(principal: number, months: number, annualRate = 0.12) {
  const r = annualRate / 12;
  const n = months;
  const denom = 1 - Math.pow(1 + r, -n);
  const emi = denom > 0 ? principal * (r / denom) : principal / n;
  const schedule = Array.from({ length: n }).map((_, i) => ({ month: i + 1, payment: emi }));
  return { emi, schedule, total: emi * n };
}

export default function FinancingCalc() {
  const [amount, setAmount] = useState(5000);
  const [months, setMonths] = useState(6);

  const { emi, total } = useMemo(() => amortization(amount, months, 0.12), [amount, months]);

  const pct = (amount / 20000) * 100;

  return (
    <div className="glass-panel p-4" role="region" aria-label="Rural UPI financing calculator">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs font-semibold text-white">Rural UPI Micro-Loan</div>
          <div className="text-sm text-slate-300">Interactive EMI calculator and approval path</div>
        </div>
      </div>

      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <div>
          <label className="text-xs text-slate-300" htmlFor="loan-amount">Loan Amount</label>
          <input id="loan-amount" aria-label="Loan amount" type="range" min={500} max={20000} step={100} value={amount} onChange={(e) => setAmount(Number(e.target.value))} className="w-full mt-2" />
          <div className="mt-2 text-2xl font-mono font-semibold text-white">₹{amount.toLocaleString()}</div>

          <label className="mt-4 text-xs text-slate-300" htmlFor="loan-months">Tenure (months)</label>
          <input id="loan-months" aria-label="Loan tenure months" type="range" min={3} max={24} step={1} value={months} onChange={(e) => setMonths(Number(e.target.value))} className="w-full mt-2" />
          <div className="mt-2 text-sm text-slate-300">{months} months</div>
        </div>

        <div className="flex flex-col items-center justify-center">
          <div className="h-36 w-36 rounded-full bg-white/5 p-4">
            <svg viewBox="0 0 36 36" className="h-full w-full">
              <defs>
                <linearGradient id="g2" x1="0" x2="1">
                  <stop offset="0%" stopColor="#ffffff" />
                  <stop offset="100%" stopColor="#a1a1aa" />
                </linearGradient>
              </defs>
              <circle cx="18" cy="18" r="16" fill="none" stroke="#0b1220" strokeWidth={4} />
              <circle cx="18" cy="18" r="12" fill="none" stroke="url(#g2)" strokeWidth={4} strokeDasharray={`${(pct / 100) * 75} 75`} strokeLinecap="round" transform="rotate(-90 18 18)" />
              <text x="18" y="20" fontSize={6} textAnchor="middle" fill="#dffaf4" fontFamily="ui-monospace, SFMono-Regular, Menlo, Monaco, monospace">₹{amount}</text>
            </svg>
          </div>

          <div className="mt-3 text-sm text-slate-300">Estimated EMI</div>
          <div className="text-2xl font-mono font-semibold text-white">₹{Math.round(emi)}</div>
          <div className="mt-2 text-xs text-slate-400">Total repayable: ₹{Math.round(total)}</div>
        </div>
      </div>

      <div className="mt-4">
        <div className="flex items-center gap-3">
          <div className="h-3 w-3 rounded-full bg-white/40" />
          <div className="text-sm text-slate-300">User Input</div>
          <div className="ml-auto text-sm text-slate-300">UPI 2.0 Auth → Routing → Approve</div>
        </div>

        <div className="mt-3 flex items-center gap-3">
          <div className="h-3 w-3 rounded-full bg-white/40" />
          <div className="text-xs text-slate-400">Simulated approval path</div>
        </div>
      </div>
    </div>
  );
}
