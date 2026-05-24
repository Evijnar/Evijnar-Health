"use client";

export default function SectionHeading({ eyebrow, title, subtitle }: { eyebrow: string; title: string; subtitle: string }) {
  return (
    <div className="max-w-3xl">
      <p className="text-xs font-semibold uppercase tracking-[0.4em] text-white/70">{eyebrow}</p>
      <h2 className="mt-3 text-3xl font-bold tracking-tight text-white sm:text-4xl md:text-5xl">{title}</h2>
      <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-300 md:text-base">{subtitle}</p>
    </div>
  );
}
