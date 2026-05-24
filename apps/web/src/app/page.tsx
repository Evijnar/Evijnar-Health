import Header from '@/components/landing/Header';
import HeroSection from '@/components/landing/HeroSection';
import DataNexusSection from '@/components/landing/DataNexusSection';
import RecoveryBridgeSection from '@/components/landing/RecoveryBridgeSection';
import FinancingSection from '@/components/landing/FinancingSection';
import Footer from '@/components/landing/Footer';

export default function Page() {
  return (
    <main className="bg-transparent text-slate-100">
      <Header />
      <HeroSection />
      <DataNexusSection />
      <RecoveryBridgeSection />
      <FinancingSection />
      <Footer />
    </main>
  );
}
