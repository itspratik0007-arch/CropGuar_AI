import React, { useEffect, useState, useCallback } from 'react';
import { Layout } from '../components/Layout';
import { api } from '../services/api';
import type { DemoStore } from '../types';
import { 
  Search, 
  MapPin, 
  Phone, 
  Clock, 
  Package, 
  AlertTriangle, 
  Filter, 
  Loader2, 
  Store
} from 'lucide-react';

const CATEGORIES = ['All', 'Seeds & Fertilizers', 'Fertilizers & Crop Care', 'Agricultural Equipment', 'Organic Inputs'];

export const NearbyStoresPage: React.FC = () => {
  const [stores, setStores] = useState<DemoStore[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [error, setError] = useState<string | null>(null);

  const fetchStores = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getDemoStores(search, selectedCategory);
      setStores(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load demo stores.');
    } finally {
      setLoading(false);
    }
  }, [search, selectedCategory]);

  useEffect(() => {
    fetchStores();
  }, [fetchStores]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchStores();
  };

  return (
    <Layout activeTitle="Nearby Stores (Demo)">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-bold text-[#8b958a] tracking-widest uppercase mb-1">
            LOCAL AGRICULTURAL NETWORK
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-[#26332b] tracking-tight">
            Nearby Agricultural Stores
          </h1>
          <p className="text-xs text-[#788279] mt-0.5">
            Sample supplier directory for seeds, plant nutrition, and agricultural implements.
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-[#faeeee] border border-[#f3d2d2] rounded-xl text-xs text-[#a24e4a] flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Mandatory Demo Banner */}
      <div className="p-4 bg-[#fff5df] border border-[#f4e0ba] rounded-2xl mb-6 flex items-start gap-3 text-xs text-[#82530d]">
        <AlertTriangle className="w-5 h-5 shrink-0 text-[#ad781d] mt-0.5" />
        <div>
          <strong className="block font-bold text-[#6d4508] text-xs">
            DEMO DATA ONLY · UNVERIFIED BUSINESSES
          </strong>
          <p className="mt-0.5 text-[11px] leading-relaxed">
            All stores, addresses, phone numbers, and product lines shown below are simulated demo placeholders for testing layout and filtering. No live store inventory, real contact details, or GPS location coordinates are accessed or stored.
          </p>
        </div>
      </div>

      {/* Search and Category Filters */}
      <div className="bg-white border border-[#e7ebe3] rounded-2xl p-4 shadow-xs mb-6 space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-[#8b9689] absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Search by store name, product or equipment (e.g. Tomato Seeds, Sprayer, Bio-Fertilizer)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-3 py-2.5 bg-[#fbfcf9] border border-[#e0e6dc] rounded-xl text-xs text-[#26332b] focus:border-[#245c3a] focus:ring-2 focus:ring-[#eff5e9] outline-none"
            />
          </div>
          <button
            type="submit"
            className="px-5 py-2.5 bg-[#245c3a] hover:bg-[#1d4c2f] text-white text-xs font-bold rounded-xl transition shrink-0"
          >
            Search Stores
          </button>
        </form>

        {/* Filter Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pt-1 pb-1">
          <span className="text-[11px] font-bold text-[#8b958a] flex items-center gap-1 shrink-0 mr-1">
            <Filter className="w-3 h-3" /> Filter:
          </span>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold whitespace-nowrap transition ${
                selectedCategory === cat
                  ? 'bg-[#245c3a] text-white'
                  : 'bg-[#f5f7f2] text-[#637064] hover:bg-[#e8eddf]'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Store Cards Grid */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center text-xs text-[#899388]">
          <Loader2 className="w-8 h-8 animate-spin text-[#245c3a] mb-3" />
          <span>Loading demo suppliers...</span>
        </div>
      ) : stores.length === 0 ? (
        <div className="py-16 text-center bg-white border border-dashed border-[#e7ebe3] rounded-2xl p-8">
          <Store className="w-10 h-10 text-[#8b9689] mx-auto mb-2 opacity-50" />
          <h3 className="text-base font-bold text-[#26332b]">No demo stores found</h3>
          <p className="text-xs text-[#788279] mt-1 mb-4">
            Try adjusting your search keywords or switching category filters.
          </p>
          <button
            onClick={() => {
              setSearch('');
              setSelectedCategory('All');
            }}
            className="px-4 py-2 bg-[#245c3a] text-white text-xs font-bold rounded-xl"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {stores.map((store) => (
            <article
              key={store.id}
              className="bg-white border border-[#e7ebe3] rounded-2xl p-5 shadow-xs flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-3 mb-2.5">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-[#eef4e8] text-[#245c3a] flex items-center justify-center font-bold">
                      <Store className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-[#26332b]">{store.name}</h3>
                      <span className="text-[11px] font-semibold text-[#6a7969] bg-[#edf4e8] px-2 py-0.5 rounded-md inline-block mt-0.5">
                        {store.category}
                      </span>
                    </div>
                  </div>
                  <span className="text-[9px] font-bold bg-[#fff2d8] text-[#ad781d] px-2 py-0.5 rounded-full uppercase shrink-0">
                    Demo Record
                  </span>
                </div>

                {/* Details */}
                <div className="space-y-2 my-4 text-xs">
                  <div className="flex items-start gap-2 text-[#4e5c50]">
                    <MapPin className="w-4 h-4 text-[#8b9689] shrink-0 mt-0.5" />
                    <span className="text-[11px] leading-tight text-[#637064]">{store.address}</span>
                  </div>

                  <div className="flex items-center gap-2 text-[#4e5c50]">
                    <Phone className="w-4 h-4 text-[#8b9689] shrink-0" />
                    <span className="text-[11px] text-[#637064]">{store.phone}</span>
                  </div>

                  <div className="flex items-center gap-2 text-[#4e5c50]">
                    <Clock className="w-4 h-4 text-[#8b9689] shrink-0" />
                    <span className="text-[11px] text-[#637064]">{store.operating_hours}</span>
                  </div>
                </div>

                {/* Sample Products */}
                <div>
                  <div className="flex items-center gap-1.5 text-[10px] font-bold text-[#8b958a] tracking-wider uppercase mb-1.5">
                    <Package className="w-3 h-3" /> Sample Product Categories
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {store.sample_products.map((p, idx) => (
                      <span
                        key={idx}
                        className="text-[10px] bg-[#f5f7f2] border border-[#e7ebe3] text-[#566157] px-2 py-0.5 rounded-md"
                      >
                        {p}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-3 border-t border-[#f0f2ed] flex items-center justify-between text-[11px] text-[#8a9388]">
                <span>Fictional sample info</span>
                <span className="text-[#245c3a] font-semibold">Demo view only</span>
              </div>
            </article>
          ))}
        </div>
      )}
    </Layout>
  );
};
