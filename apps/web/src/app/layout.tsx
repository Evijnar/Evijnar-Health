import type { Metadata } from 'next';
import { ReactNode } from 'react';
import { Manrope, Sora } from 'next/font/google';
import './globals.css';
import ParticlesBackdrop from '@/components/ParticlesBackdrop';

const bodyFont = Manrope({
  subsets: ['latin'],
  variable: '--font-body',
  display: 'swap',
});

const displayFont = Sora({
  subsets: ['latin'],
  variable: '--font-display',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Evijnar | Global Health Arbitrage Exchange',
  description: 'Transparent hospital pricing, outcome-driven ranking, recovery monitoring, and financing for global healthcare access.',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={`${bodyFont.variable} ${displayFont.variable}`}>
      <body className="relative bg-black text-white">
        <ParticlesBackdrop />
        <div className="relative z-10">{children}</div>
      </body>
    </html>
  );
}
