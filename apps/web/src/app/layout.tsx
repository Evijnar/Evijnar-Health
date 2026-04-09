import type { Metadata } from 'next';
import { ReactNode } from 'react';
import './globals.css';

export const metadata: Metadata = {
  title: 'Evijnar - Global Healthcare Arbitrage',
  description: 'Access world-class healthcare at transparent, affordable prices',
  keywords: [
    'healthcare arbitrage',
    'medical tourism',
    'surgery costs',
    'affordable healthcare',
    'JCI accredited hospitals',
  ],
  apple: {
    statusBarStyle: 'black-translucent',
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
    viewportFit: 'cover',
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta charSet="utf-8" />
        <meta name="theme-color" content="#001F3F" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="Evijnar" />
      </head>
      <body className="bg-white text-gray-900 overflow-x-hidden">
        <div className="min-h-screen flex flex-col">
          {children}
        </div>
      </body>
    </html>
  );
}
