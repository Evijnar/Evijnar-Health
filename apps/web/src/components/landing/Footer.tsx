export default function Footer() {
  return (
    <footer className="border-t border-white/10 bg-white/5 py-8 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl flex-col gap-2 px-6 text-sm text-slate-400 md:flex-row md:items-center md:justify-between">
        <div className="font-mono">Zero-Knowledge Encryption Active</div>
        <div className="font-mono">HIPAA / EHDS Compliant</div>
        <div className="font-mono">© {new Date().getFullYear()} Evijnar</div>
      </div>
    </footer>
  );
}
