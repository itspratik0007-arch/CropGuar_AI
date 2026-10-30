import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import type { DashboardSummary } from '../types';
import { 
  BookMarked, 
  Search, 
  MapPin, 
  ArrowRight, 
  Camera, 
  Activity, 
  AlertTriangle,
  Loader2,
  CheckCircle2
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    async function loadDashboard() {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getDashboardSummary();
        setSummary(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard summary.');
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/plantopedia?q=${encodeURIComponent(searchQuery.trim())}`);
    } else {
      navigate('/plantopedia');
    }
  };

  const timeGreeting = useMemo(() => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  }, []);

  return (
    <Layout activeTitle="Dashboard">
      {/* Welcome Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-7">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-bold text-[#8b958a] tracking-widest uppercase mb-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#6fa05b]"></span>
            YOUR FARM AT A GLANCE
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-[#26332b] tracking-tight">
            {timeGreeting}, {user?.full_name?.split(' ')[0] || 'Farmer'} <span className="text-[#d7a54c]">☀</span>
          </h1>
          <p className="text-xs text-[#788279] mt-0.5">
            Phase 1 workspace connected to your live database profile.
          </p>
        </div>

        <button
          onClick={() => navigate('/plantopedia')}
          className="self-start md:self-auto px-4 py-2.5 bg-[#245c3a] hover:bg-[#1d4c2f] text-white text-xs font-bold rounded-xl shadow-xs flex items-center gap-2 transition"
        >
          <Search className="w-4 h-4" />
          <span>Explore Plantopedia</span>
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-[#faeeee] border border-[#f3d2d2] rounded-xl text-xs text-[#a24e4a] flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Database Status Strip */}
      <div className="flex items-center gap-3 p-3.5 bg-[#eef5e8] border border-[#e1ecd8] rounded-xl mb-7 text-xs text-[#6a7969]">
        <div className="w-7 h-7 rounded-lg bg-[#dceacc] text-[#245c3a] flex items-center justify-center shrink-0">
          <CheckCircle2 className="w-4 h-4" />
        </div>
        <div className="flex-1">
          <strong className="text-[#35543b] mr-1">Database Connected:</strong>
          <span>
            {summary?.system_status || 'Session authenticated with persistent database storage.'}
          </span>
        </div>
        <button
          onClick={() => navigate('/stores')}
          className="text-xs font-bold text-[#245c3a] hover:underline flex items-center gap-1 shrink-0"
        >
          <span>Find Suppliers</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-7">
        {/* Metric 1: Saved Plants */}
        <div className="bg-white border border-[#e7ebe3] rounded-2xl p-5 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div className="w-9 h-9 rounded-xl bg-[#eaf3e3] text-[#4e7c42] flex items-center justify-center">
              <BookMarked className="w-4 h-4" />
            </div>
            <span className="text-[10px] font-bold tracking-wider text-[#899388] uppercase">
              SAVED PLANTS
            </span>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-[#26332b]">
              {loading ? (
                <Loader2 className="w-6 h-6 animate-spin text-[#245c3a]" />
              ) : (
                summary?.total_saved_plants ?? 0
              )}{' '}
              <span className="text-xs font-medium text-[#8a9388]">bookmarks</span>
            </div>
            <p className="text-xs text-[#788279] mt-1 mb-4">
              Your personalized reference library saved in the database.
            </p>
          </div>
          <button
            onClick={() => navigate('/plantopedia')}
            className="text-xs font-bold text-[#245c3a] hover:underline flex items-center gap-1.5 self-start"
          >
            <span>Browse saved plants</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Metric 2: Plantopedia Quick Search */}
        <div className="bg-white border border-[#e7ebe3] rounded-2xl p-5 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div className="w-9 h-9 rounded-xl bg-[#eaf2fb] text-[#4775a7] flex items-center justify-center">
              <Search className="w-4 h-4" />
            </div>
            <span className="text-[10px] font-bold tracking-wider text-[#899388] uppercase">
              PLANTOPEDIA
            </span>
          </div>
          <div>
            <form onSubmit={handleSearchSubmit} className="mb-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-[#8b9689] absolute left-3 top-3" />
                <input
                  type="text"
                  placeholder="Quick search (e.g. Tomato, Rice)..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-8 pr-3 py-2 bg-[#fbfcf9] border border-[#e0e6dc] rounded-lg text-xs text-[#26332b] focus:border-[#245c3a] outline-none"
                />
              </div>
            </form>
            <p className="text-xs text-[#788279] mt-1 mb-4">
              Access growing conditions, soil, watering, and botanical info.
            </p>
          </div>
          <button
            onClick={handleSearchSubmit}
            className="text-xs font-bold text-[#4775a7] hover:underline flex items-center gap-1.5 self-start"
          >
            <span>Search botanical library</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Metric 3: Nearby Stores Shortcut */}
        <div className="bg-white border border-[#e7ebe3] rounded-2xl p-5 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div className="w-9 h-9 rounded-xl bg-[#fff2d8] text-[#ad781d] flex items-center justify-center">
              <MapPin className="w-4 h-4" />
            </div>
            <span className="text-[10px] font-bold tracking-wider text-[#899388] uppercase">
              LOCAL SUPPLIERS
            </span>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-[#26332b]">
              5 <span className="text-xs font-medium text-[#8a9388]">demo stores</span>
            </div>
            <p className="text-xs text-[#788279] mt-1 mb-4">
              Agricultural seeds, fertilizers, and equipment suppliers.
            </p>
          </div>
          <button
            onClick={() => navigate('/stores')}
            className="text-xs font-bold text-[#ad781d] hover:underline flex items-center gap-1.5 self-start"
          >
            <span>View demo directory</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Two Column Layout: Recent Bookmarks + Future Features */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-7">
        {/* Panel 1: Recently Bookmarked Plants */}
        <div className="bg-white border border-[#e7ebe3] rounded-2xl p-6 shadow-xs">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#f0f2ed]">
            <div>
              <h2 className="text-base font-bold text-[#26332b]">Your Bookmarked Plants</h2>
              <p className="text-xs text-[#788279]">Live records saved under your user account</p>
            </div>
            <button
              onClick={() => navigate('/plantopedia')}
              className="text-xs font-bold text-[#245c3a] hover:underline flex items-center gap-1"
            >
              <span>View all</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {loading ? (
            <div className="py-12 flex flex-col items-center justify-center text-xs text-[#899388]">
              <Loader2 className="w-6 h-6 animate-spin text-[#245c3a] mb-2" />
              <span>Loading saved plants from database...</span>
            </div>
          ) : summary?.recent_bookmarks && summary.recent_bookmarks.length > 0 ? (
            <div className="space-y-3">
              {summary.recent_bookmarks.map((bm) => (
                <div
                  key={bm.plant_id}
                  onClick={() => navigate(`/plantopedia?id=${bm.plant_id}`)}
                  className="flex items-center justify-between p-3 rounded-xl border border-[#f0f2ed] hover:border-[#cddbc5] hover:bg-[#fbfcf9] transition cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    {bm.image_url ? (
                      <img
                        src={bm.image_url}
                        alt={bm.common_name}
                        className="w-11 h-11 rounded-lg object-cover bg-[#f0f4eb]"
                        onError={(e) => {
                          // Prevent broken image layout
                          (e.target as HTMLElement).style.display = 'none';
                        }}
                      />
                    ) : (
                      <div className="w-11 h-11 rounded-lg bg-[#eef4e8] text-[#245c3a] flex items-center justify-center font-bold text-lg">
                        🌱
                      </div>
                    )}
                    <div>
                      <strong className="block text-xs font-bold text-[#26332b]">
                        {bm.common_name}
                      </strong>
                      <span className="block text-[11px] text-[#8a9389] italic">
                        {bm.scientific_name}
                      </span>
                    </div>
                  </div>
                  <span className="text-xs font-bold text-[#245c3a] flex items-center gap-1">
                    <span>Inspect</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-10 text-center border border-dashed border-[#e7ebe3] rounded-xl bg-[#fbfcf9] p-6">
              <BookMarked className="w-8 h-8 text-[#8b9689] mx-auto mb-2 opacity-50" />
              <strong className="block text-xs font-bold text-[#26332b]">No saved plants yet</strong>
              <p className="text-xs text-[#788279] mt-1 mb-4">
                Explore the Plantopedia catalog to bookmark plants for your farm.
              </p>
              <button
                onClick={() => navigate('/plantopedia')}
                className="px-3.5 py-2 bg-[#245c3a] text-white text-xs font-bold rounded-lg hover:bg-[#1d4c2f] transition"
              >
                Browse Plantopedia
              </button>
            </div>
          )}
        </div>

        {/* Panel 2: Scope Transparency & Future Phase Roadmap */}
        <div className="bg-white border border-[#e7ebe3] rounded-2xl p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#f0f2ed]">
              <div>
                <h2 className="text-base font-bold text-[#26332b]">Phase Roadmap & Scope</h2>
                <p className="text-xs text-[#788279]">Scientific integrity & honest system capabilities</p>
              </div>
              <span className="text-[10px] font-bold bg-[#edf4e8] text-[#245c3a] px-2 py-0.5 rounded-full">
                Phase 1 Active
              </span>
            </div>

            <div className="space-y-3">
              <div className="p-3.5 rounded-xl border border-[#e8eddf] bg-[#fbfcf9] flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-[#e2ebdc] text-[#245c3a] flex items-center justify-center shrink-0 mt-0.5">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
                <div>
                  <strong className="block text-xs font-bold text-[#26332b]">
                    Active Phase 1 Modules
                  </strong>
                  <p className="text-[11px] text-[#788279] mt-0.5 leading-relaxed">
                    User authentication, PostgreSQL database storage, live bookmark persistence, Plantopedia API integration, and demo supplier directory.
                  </p>
                </div>
              </div>

              {/* Disabled Coming Soon Feature 1 */}
              {/* Active AI Disease Detection Feature */}
              <div 
                onClick={() => navigate('/disease')}
                className="p-3.5 rounded-xl border border-[#dbe8d4] bg-[#f7faf4] hover:bg-[#edf4e8] transition flex items-start gap-3 cursor-pointer group shadow-2xs"
              >
                <div className="w-8 h-8 rounded-lg bg-[#245c3a] text-white flex items-center justify-center shrink-0 mt-0.5 shadow-xs">
                  <Camera className="w-4 h-4" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <strong className="text-xs font-bold text-[#26332b] group-hover:text-[#245c3a] flex items-center gap-1.5">
                      <span>AI Disease Detection</span>
                      <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition" />
                    </strong>
                    <span className="text-[9px] bg-[#dcecc9] text-[#245c3a] px-1.5 py-0.5 rounded font-bold">
                      Active · ONNX Ready
                    </span>
                  </div>
                  <p className="text-[11px] text-[#556356] mt-0.5 leading-relaxed">
                    Trained MobileNetV2 vision model for foliar pathology diagnosis across 38 crop disease classes.
                  </p>
                </div>
              </div>

              {/* Disabled Coming Soon Feature 2 */}
              <div className="p-3.5 rounded-xl border border-[#f0f2ed] bg-[#fafbfa] flex items-start gap-3 opacity-75">
                <div className="w-8 h-8 rounded-lg bg-[#f0f2ed] text-[#788276] flex items-center justify-center shrink-0 mt-0.5">
                  <Activity className="w-4 h-4" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <strong className="text-xs font-bold text-[#26332b]">
                      Microclimate Risk Prediction
                    </strong>
                    <span className="text-[9px] bg-[#f0f2ed] text-[#788276] px-1.5 py-0.5 rounded font-bold">
                      Coming Soon · Phase 2
                    </span>
                  </div>
                  <p className="text-[11px] text-[#788279] mt-0.5 leading-relaxed">
                    Continuous weather station ingestion and crop susceptibility modeling.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-5 p-3 bg-[#fff5df] border border-[#f4e0ba] rounded-xl text-[11px] text-[#a76d14] flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>
              CropGuard AI does not fabricate disease predictions without validated models.
            </span>
          </div>
        </div>
      </div>
    </Layout>
  );
};
