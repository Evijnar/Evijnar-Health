'use client';

import { useState, useRef, useEffect } from 'react';
import {
  Search,
  Mic,
  Globe,
  MapPin,
  Check,
  AlertCircle,
  MoreVertical,
  Heart,
  Thermometer,
  Shield,
  DollarSign,
  CreditCard,
  ArrowRight,
} from 'lucide-react';
import clsx from 'clsx';

type SearchMode = 'local' | 'global';
type SortBy = 'price' | 'accreditation' | 'savings';
interface Hospital {
  id: string;
  name: string;
  location: string;
  price: number;
  currency: string;
  jciAccredited: boolean;
  successRate: number;
  estimatedSavings: number;
  savingsPercentage: number;
  type: 'local' | 'global';
  country?: string;
  specialization?: string;
}

type VitalStats = {
  heartRate: number;
  temperature: number;
  isStable: boolean;
};

export default function SearchPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [searchMode, setSearchMode] = useState<SearchMode>('local');
  const [sortBy, setSortBy] = useState<SortBy>('price');
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [showRecoveryBridge, setShowRecoveryBridge] = useState(false);
  const [vitalStats, setVitalStats] = useState<VitalStats>({
    heartRate: 72,
    temperature: 37.2,
    isStable: true,
  });
  const micRef = useRef<HTMLButtonElement>(null);

  const mockHospitals: Hospital[] = [
    {
      id: 'local-1',
      name: 'City General Hospital',
      location: 'New York, USA',
      price: 45000,
      currency: 'USD',
      jciAccredited: true,
      successRate: 97,
      estimatedSavings: 0,
      savingsPercentage: 0,
      type: 'local',
    },
    {
      id: 'global-1',
      name: 'Apollo Hospitals',
      location: 'Delhi, India',
      price: 8500,
      currency: 'USD',
      jciAccredited: true,
      successRate: 98.5,
      estimatedSavings: 36500,
      savingsPercentage: 81,
      type: 'global',
      country: 'India',
      specialization: 'Center of Excellence',
    },
    {
      id: 'global-2',
      name: 'Medanta Orthopedic Hospital',
      location: 'Gurgaon, India',
      price: 7200,
      currency: 'USD',
      jciAccredited: true,
      successRate: 99,
      estimatedSavings: 37800,
      savingsPercentage: 84,
      type: 'global',
      country: 'India',
      specialization: 'Center of Excellence',
    },
  ];

  useEffect(() => {
    // Simulate real-time vitals update
    const interval = setInterval(() => {
      setVitalStats((prev) => ({
        heartRate: prev.heartRate + (Math.random() - 0.5) * 10,
        temperature: prev.temperature + (Math.random() - 0.5) * 0.2,
        isStable: Math.random() > 0.1,
      }));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleSearch = () => {
    if (searchQuery.trim()) {
      setHospitals(mockHospitals);
    }
  };

  const handleVoiceSearch = async () => {
    setIsListening(!isListening);
    if (!isListening) {
      // Web Speech API
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setSearchQuery(transcript);
          setIsListening(false);
        };
        recognition.start();
      }
    }
  };

  const sortedHospitals = [...hospitals].sort((a, b) => {
    if (sortBy === 'price') return a.price - b.price;
    if (sortBy === 'savings') return b.savingsPercentage - a.savingsPercentage;
    if (sortBy === 'accreditation') return b.successRate - a.successRate;
    return 0;
  });

  const filtered = sortedHospitals.filter((h) => {
    if (searchMode === 'local') return h.type === 'local';
    return h.type === 'global';
  });

  const localHospital = filtered.find((h) => h.type === 'local');
  const globalHospital = filtered.find((h) => h.type === 'global');

  return (
    <div className="min-h-screen bg-white pb-8">
      {/* Header */}
      <header className="bg-navy sticky top-0 z-50 shadow-md">
        <div className="max-w-2xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <h1 className="text-white font-bold text-xl">Evijnar</h1>
            <span className="text-emerald text-sm font-semibold">Global Access</span>
          </div>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-6 space-y-8">
        {/* ===== 1. UNIVERSAL SEARCH COMPONENT ===== */}
        <section className="space-y-4">
          <div>
            <h2 className="text-h3 mb-4">Find Your Treatment</h2>

            {/* Search Bar */}
            <div className="flex gap-2 mb-4">
              <div className="flex-1 relative">
                <input
                  type="text"
                  placeholder="Procedure or Symptom..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className={clsx('input-base pl-4', 'text-base')}
                />
                <Search className="absolute right-3 top-3 text-gray-medium w-5 h-5" />
              </div>

              {/* Voice Search Button */}
              <button
                ref={micRef}
                onClick={handleVoiceSearch}
                className={clsx(
                  'btn-sm rounded-lg transition-all duration-200 flex items-center gap-2',
                  isListening
                    ? 'bg-red-alert text-white animate-pulse'
                    : 'bg-emerald text-white hover:bg-emerald-dark'
                )}
                title="Voice search"
              >
                <Mic className="w-5 h-5" />
              </button>

              <button
                onClick={handleSearch}
                className="btn-primary btn-sm flex items-center gap-2"
              >
                <Search className="w-5 h-5" />
                <span className="hidden sm:inline">Search</span>
              </button>
            </div>

            {/* Search Mode Toggle */}
            <div className="flex gap-2 mb-4">
              <button
                onClick={() => setSearchMode('local')}
                className={clsx(
                  'badge btn-sm flex-1 justify-center gap-2 transition-all',
                  searchMode === 'local'
                    ? 'bg-navy text-white'
                    : 'bg-gray-light text-gray-dark hover:bg-gray-200'
                )}
              >
                <MapPin className="w-4 h-4" />
                <span>Local Search</span>
              </button>
              <button
                onClick={() => setSearchMode('global')}
                className={clsx(
                  'badge btn-sm flex-1 justify-center gap-2 transition-all',
                  searchMode === 'global'
                    ? 'bg-emerald text-white'
                    : 'bg-gray-light text-gray-dark hover:bg-gray-200'
                )}
              >
                <Globe className="w-4 h-4" />
                <span>Global Arbitrage</span>
              </button>
            </div>

            {/* Sort Options */}
            {hospitals.length > 0 && (
              <div className="flex gap-2 overflow-x-auto pb-2">
                {(['price', 'savings', 'accreditation'] as const).map((sort) => (
                  <button
                    key={sort}
                    onClick={() => setSortBy(sort)}
                    className={clsx(
                      'badge btn-sm whitespace-nowrap transition-all',
                      sortBy === sort
                        ? 'bg-navy text-white'
                        : 'bg-gray-light text-gray-dark hover:bg-gray-200'
                    )}
                  >
                    {sort === 'price' && '💰 Price'}
                    {sort === 'savings' && '🎯 Savings'}
                    {sort === 'accreditation' && '✓ Quality'}
                  </button>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* ===== 2. ARBITRAGE COMPARISON DASHBOARD ===== */}
        {hospitals.length > 0 && (
          <section className="space-y-4">
            <h2 className="text-h3">Your Options</h2>

            {/* Side-by-Side Comparison */}
            <div className="grid grid-2-col gap-4">
              {/* Local Option */}
              {localHospital && (
                <div className="card p-4 space-y-3 border-l-4 border-navy">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-bold text-navy text-sm">{localHospital.name}</h3>
                      <p className="text-caption text-gray-medium flex items-center gap-1 mt-1">
                        <MapPin className="w-3 h-3" />
                        {localHospital.location}
                      </p>
                    </div>
                    <button className="p-1 hover:bg-gray-100 rounded">
                      <MoreVertical className="w-4 h-4 text-gray-medium" />
                    </button>
                  </div>

                  {/* Price */}
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-caption text-gray-medium">Local Price</p>
                    <p className="text-2xl font-bold text-navy">
                      {localHospital.currency} {localHospital.price.toLocaleString()}
                    </p>
                  </div>

                  {/* JCI Badge */}
                  {localHospital.jciAccredited && (
                    <div className="flex flex-wrap gap-2">
                      <span className="badge badge-navy">
                        <Check className="w-3 h-3" />
                        JCI Accredited
                      </span>
                    </div>
                  )}

                  {/* Success Rate */}
                  <p className="text-caption text-gray-dark">
                    Success Rate: <span className="font-semibold text-navy">{localHospital.successRate}%</span>
                  </p>

                  <button className="w-full btn-secondary btn-sm mt-2">
                    Learn More
                  </button>
                </div>
              )}

              {/* Global Option */}
              {globalHospital && (
                <div className="card p-4 space-y-3 border-l-4 border-emerald bg-emerald-light">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-bold text-emerald-dark text-sm">
                        {globalHospital.specialization}
                      </h3>
                      <p className="text-caption text-emerald-dark/70 flex items-center gap-1 mt-1">
                        <Globe className="w-3 h-3" />
                        {globalHospital.location}
                      </p>
                    </div>
                    <button className="p-1 hover:bg-white/50 rounded">
                      <MoreVertical className="w-4 h-4 text-emerald-dark" />
                    </button>
                  </div>

                  {/* Price + Savings */}
                  <div className="bg-white rounded-lg p-3">
                    <p className="text-caption text-gray-medium">Global Price</p>
                    <div className="flex items-baseline gap-2 mt-1">
                      <p className="text-2xl font-bold text-emerald">
                        USD {globalHospital.price.toLocaleString()}
                      </p>
                      <span className="text-sm font-semibold text-emerald">
                        Save {globalHospital.savingsPercentage}%
                      </span>
                    </div>
                  </div>

                  {/* Savings Breakdown */}
                  <div className="bg-white rounded-lg p-3 border border-emerald/20">
                    <p className="text-caption text-gray-medium mb-2">Your Savings</p>
                    <p className="text-xl font-bold text-emerald">
                      USD {globalHospital.estimatedSavings.toLocaleString()}
                    </p>
                  </div>

                  {/* Quality Badges */}
                  <div className="flex flex-wrap gap-2">
                    <span className="badge bg-white text-emerald-dark text-xs">
                      <Check className="w-3 h-3" />
                      JCI Certified
                    </span>
                    <span className="badge bg-white text-emerald-dark text-xs">
                      Excellence: {globalHospital.successRate}%
                    </span>
                  </div>

                  <button className="w-full btn-primary btn-sm mt-2 flex items-center justify-center gap-2">
                    Select & Continue
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>

            {/* Why Choose Global? */}
            <div className="card-navy p-4 space-y-3">
              <h4 className="font-semibold text-white text-sm">💡 Why Choose Global?</h4>
              <ul className="space-y-2 text-sm text-white/90">
                <li className="flex gap-2">
                  <Check className="w-4 h-4 flex-shrink-0 text-emerald" />
                  <span>Same quality standards (JCI/ISO certified)</span>
                </li>
                <li className="flex gap-2">
                  <Check className="w-4 h-4 flex-shrink-0 text-emerald" />
                  <span>Free flights + accommodation included</span>
                </li>
                <li className="flex gap-2">
                  <Check className="w-4 h-4 flex-shrink-0 text-emerald" />
                  <span>Global surgeon + local recovery team</span>
                </li>
              </ul>
            </div>
          </section>
        )}

        {/* ===== 3. RECOVERY BRIDGE PATIENT PORTAL ===== */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-h3">Recovery Bridge</h2>
            <button
              onClick={() => setShowRecoveryBridge(!showRecoveryBridge)}
              className="text-sm font-semibold text-emerald hover:text-emerald-dark"
            >
              {showRecoveryBridge ? 'Hide' : 'View'} Portal
            </button>
          </div>

          {showRecoveryBridge && (
            <div className="card p-6 space-y-6">
              {/* Status Indicator */}
              <div className="flex items-center justify-between bg-emerald-light rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-emerald rounded-full animate-pulse" />
                  <div>
                    <p className="text-sm font-semibold text-emerald-dark">Global Surgeon Monitoring</p>
                    <p className="text-xs text-emerald-dark/70">Dr. Rajesh Kumar (Apollo)</p>
                  </div>
                </div>
                <span className={clsx('badge', vitalStats.isStable ? 'badge-success' : 'badge-alert')}>
                  {vitalStats.isStable ? 'SAFE' : 'ALERT'}
                </span>
              </div>

              {/* Real-Time Vitals */}
              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-navy">Real-Time Vitals</h3>

                <div className="grid grid-cols-2 gap-4">
                  {/* Heart Rate */}
                  <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-4 space-y-2">
                    <div className="flex items-center gap-2 text-red-alert">
                      <Heart className="w-4 h-4" />
                      <p className="text-xs font-semibold">Heart Rate</p>
                    </div>
                    <p className="text-2xl font-bold text-red-alert">
                      {Math.round(vitalStats.heartRate)} bpm
                    </p>
                    <p className="text-xs text-gray-medium">Normal: 60-100 bpm</p>
                  </div>

                  {/* Temperature */}
                  <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4 space-y-2">
                    <div className="flex items-center gap-2 text-orange-600">
                      <Thermometer className="w-4 h-4" />
                      <p className="text-xs font-semibold">Temperature</p>
                    </div>
                    <p className="text-2xl font-bold text-orange-600">
                      {vitalStats.temperature.toFixed(1)}°C
                    </p>
                    <p className="text-xs text-gray-medium">Normal: 36.5-37.5°C</p>
                  </div>
                </div>
              </div>

              {/* Alert Zone */}
              {!vitalStats.isStable && (
                <div className="bg-red-light border border-red-alert rounded-lg p-4 flex gap-3">
                  <AlertCircle className="w-5 h-5 text-red-alert flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-red-alert text-sm">Alert: Check vitals</p>
                    <p className="text-xs text-gray-dark mt-1">
                      Your surgeon has been notified. Take medication and rest.
                    </p>
                  </div>
                </div>
              )}

              {/* Quick Actions */}
              <div className="flex gap-2">
                <button className="flex-1 btn-primary btn-sm flex items-center justify-center gap-2">
                  <Shield className="w-4 h-4" />
                  Contact Doctor
                </button>
                <button className="flex-1 btn-secondary btn-sm">Medication Log</button>
              </div>

              {/* 24/7 Support Badge */}
              <div className="text-center p-3 bg-navy rounded-lg">
                <p className="text-white text-xs">
                  ✓ <span className="font-semibold">24/7 Surgery Team Support</span>
                </p>
              </div>
            </div>
          )}
        </section>

        {/* ===== 4. RURAL EQUITY CHECKOUT ===== */}
        {hospitals.length > 0 && (
          <section className="space-y-4">
            <h2 className="text-h3">Payment Options</h2>

            <div className="card p-4 space-y-4">
              {/* Cost Breakdown */}
              <div className="space-y-3 bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-navy text-sm mb-3">Cost Breakdown</h3>

                <div className="flex justify-between items-center pb-2 border-b border-gray-200">
                  <span className="text-sm text-gray-dark">Surgery + Treatment</span>
                  <span className="font-semibold text-navy">USD 8,500</span>
                </div>

                <div className="flex justify-between items-center pb-2 border-b border-gray-200">
                  <span className="text-sm text-gray-dark">Flights + Accommodation</span>
                  <span className="font-semibold text-navy">USD 2,000</span>
                </div>

                <div className="flex justify-between items-center pb-2 border-b border-gray-200">
                  <span className="text-sm text-gray-dark">Recovery Kit + Monitoring</span>
                  <span className="font-semibold text-navy">USD 500</span>
                </div>

                <div className="flex justify-between items-center pt-2 text-base font-bold text-emerald">
                  <span>Total Cost</span>
                  <span>USD 11,000</span>
                </div>
              </div>

              {/* Payment Method Selection */}
              <div className="space-y-3">
                <h3 className="font-semibold text-navy text-sm">Payment Method</h3>

                {/* Health EMI Option */}
                <label className="flex gap-3 p-3 border-2 border-emerald rounded-lg cursor-pointer hover:bg-emerald-light transition-colors">
                  <input type="radio" name="payment" defaultChecked className="mt-1" />
                  <div className="flex-1">
                    <p className="font-semibold text-sm text-navy">Health-EMI (0% Interest)</p>
                    <p className="text-xs text-gray-medium mt-1">
                      Pay USD 917/month for 12 months
                    </p>
                    <p className="text-xs text-emerald font-semibold mt-1">✓ Recommended for rural patients</p>
                  </div>
                </label>

                {/* UPI Option */}
                <label className="flex gap-3 p-3 border-2 border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                  <input type="radio" name="payment" className="mt-1" />
                  <div className="flex-1">
                    <p className="font-semibold text-sm text-navy">UPI 2.0 Direct</p>
                    <p className="text-xs text-gray-medium mt-1">Instant payment from your bank</p>
                    <p className="text-xs text-gray-medium mt-1 flex items-center gap-1">
                      <Check className="w-3 h-3" />
                      Works offline
                    </p>
                  </div>
                </label>

                {/* Crypto Option */}
                <label className="flex gap-3 p-3 border-2 border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                  <input type="radio" name="payment" className="mt-1" />
                  <div className="flex-1">
                    <p className="font-semibold text-sm text-navy">Blockchain Payment</p>
                    <p className="text-xs text-gray-medium mt-1">USDC stable coin settlement</p>
                  </div>
                </label>
              </div>

              {/* Transparency Note */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex gap-2">
                <Shield className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
                <p className="text-xs text-gray-dark">
                  <span className="font-semibold text-blue-900">100% Transparent:</span> No hidden costs. All fees disclosed.
                </p>
              </div>

              {/* CTA Button */}
              <button className="w-full btn-primary btn-sm py-3 flex items-center justify-center gap-2 text-base font-semibold">
                <DollarSign className="w-5 h-5" />
                Proceed to Payment
              </button>
            </div>
          </section>
        )}

        {/* Empty State */}
        {hospitals.length === 0 && searchQuery === '' && (
          <div className="text-center py-12 space-y-4">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto">
              <Search className="w-8 h-8 text-gray-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-navy">Search for Treatment</h3>
              <p className="text-sm text-gray-medium mt-2">
                Enter a procedure name or symptom to find global options
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
