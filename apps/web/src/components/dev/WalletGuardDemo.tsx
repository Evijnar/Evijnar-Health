"use client";

import { useState } from 'react';
import { hasWalletProvider, isMetaMaskProvider, safeConnectWallet } from '@/lib/wallet-guard';

type Status = {
  title: string;
  detail: string;
};

const initialStatus: Status = {
  title: 'Wallet check ready',
  detail: 'No wallet call has been made yet.',
};

export default function WalletGuardDemo() {
  const [status, setStatus] = useState<Status>(initialStatus);
  const [accounts, setAccounts] = useState<string[]>([]);

  const onConnect = async () => {
    const result = await safeConnectWallet();

    if (!result.ok) {
      setAccounts([]);
      setStatus({
        title: `Safe failure: ${result.error.code}`,
        detail: result.error.message,
      });
      return;
    }

    setAccounts(result.data);
    setStatus({
      title: 'Wallet connected safely',
      detail: `${result.data.length} account(s) returned by provider.`,
    });
  };

  return (
    <section className="rounded-2xl border border-white/10 bg-black/30 p-4 text-sm text-slate-200">
      <h3 className="text-base font-semibold text-white">Wallet Guard (Safe Optional Integration)</h3>
      <p className="mt-2 text-slate-300">This demo prevents crashes when MetaMask or other providers are absent.</p>

      <div className="mt-3 space-y-1 text-xs text-slate-400">
        <p>Provider detected: {hasWalletProvider() ? 'Yes' : 'No'}</p>
        <p>MetaMask detected: {isMetaMaskProvider() ? 'Yes' : 'No'}</p>
      </div>

      <button
        type="button"
        onClick={onConnect}
        className="mt-4 rounded-full bg-white px-4 py-2 font-semibold text-black"
      >
        Try Safe Connect
      </button>

      <div className="mt-3 rounded-xl border border-white/10 bg-white/[0.04] p-3">
        <p className="font-medium text-white">{status.title}</p>
        <p className="mt-1 text-xs text-slate-300">{status.detail}</p>
        {accounts.length > 0 ? (
          <p className="mt-2 text-xs text-slate-300">Accounts: {accounts.join(', ')}</p>
        ) : null}
      </div>
    </section>
  );
}
