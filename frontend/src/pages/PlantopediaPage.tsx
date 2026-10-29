import React, { useEffect, useState, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { api } from '../services/api';
import type { 
  Plant, 
  ConversationSummary, 
  AssistantMessage 
} from '../types';
import { 
  Search, 
  Bookmark, 
  BookmarkCheck, 
  Sun, 
  Droplets, 
  Layers, 
  CloudSun, 
  Info, 
  Loader2, 
  X, 
  AlertCircle,
  MessageSquare,
  Sparkles,
  Send,
  PlusCircle,
  Trash2,
  Calendar,
  ShieldAlert,
  Bug,
  BookOpen,
  Bot
} from 'lucide-react';

export const PlantopediaPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  const initialPlantId = searchParams.get('id');

  const [query, setQuery] = useState(initialQuery);
  const [suggestions, setSuggestions] = useState<Plant[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [plants, setPlants] = useState<Plant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apiSource, setApiSource] = useState<string>('');
  const [selectedPlant, setSelectedPlant] = useState<Plant | null>(null);
  const [filterSavedOnly, setFilterSavedOnly] = useState(false);
  const [bookmarkingId, setBookmarkingId] = useState<number | null>(null);

  // AI Assistant Chat Drawer State
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatPlant, setChatPlant] = useState<Plant | null>(null);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<AssistantMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const [groundingSources, setGroundingSources] = useState<string[]>([]);
  const [activeModel, setActiveModel] = useState<string>('');
  const [isFallbackMode, setIsFallbackMode] = useState(false);
  const [showHistoryList, setShowHistoryList] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch plant catalog
  const fetchPlants = async (searchStr: string) => {
    setLoading(true);
    setError(null);
    try {
      if (filterSavedOnly) {
        const saved = await api.getBookmarks();
        setPlants(saved);
        setApiSource('curated_local');
      } else {
        const res = await api.searchPlants(searchStr);
        setPlants(res.items);
        setApiSource(res.api_source);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load plants.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlants(initialQuery);
  }, [initialQuery, filterSavedOnly]);

  useEffect(() => {
    if (initialPlantId && plants.length > 0) {
      const match = plants.find((p) => p.id === Number(initialPlantId));
      if (match) {
        setSelectedPlant(match);
      } else {
        api.getPlantDetail(Number(initialPlantId))
          .then((p) => setSelectedPlant(p))
          .catch(() => {});
      }
    }
  }, [initialPlantId, plants]);

  // Load user conversation list for AI assistant
  const loadConversations = async () => {
    try {
      const convList = await api.getConversations();
      setConversations(convList);
    } catch {
      // Non-blocking
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  // Search input typing suggestions
  useEffect(() => {
    if (query.trim().length >= 2) {
      const qLower = query.toLowerCase();
      const filtered = plants
        .filter(
          (p) =>
            p.common_name.toLowerCase().includes(qLower) ||
            p.scientific_name.toLowerCase().includes(qLower) ||
            (p.family && p.family.toLowerCase().includes(qLower))
        )
        .slice(0, 5);
      setSuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [query, plants]);

  // Scroll chat messages into view
  useEffect(() => {
    if (isChatOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isChatOpen]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowSuggestions(false);
    setSearchParams(query ? { q: query } : {});
  };

  const handleSelectSuggestion = (plant: Plant) => {
    setQuery(plant.common_name);
    setShowSuggestions(false);
    setSelectedPlant(plant);
  };

  const handleToggleBookmark = async (plant: Plant, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setBookmarkingId(plant.id);
    try {
      if (plant.is_bookmarked) {
        await api.removeBookmark(plant.id);
        setPlants((prev) =>
          prev.map((p) => (p.id === plant.id ? { ...p, is_bookmarked: false } : p))
        );
        if (selectedPlant?.id === plant.id) {
          setSelectedPlant({ ...selectedPlant, is_bookmarked: false });
        }
      } else {
        await api.addBookmark(plant.id);
        setPlants((prev) =>
          prev.map((p) => (p.id === plant.id ? { ...p, is_bookmarked: true } : p))
        );
        if (selectedPlant?.id === plant.id) {
          setSelectedPlant({ ...selectedPlant, is_bookmarked: true });
        }
      }
    } catch (err: any) {
      alert(err.message || 'Failed to update bookmark.');
    } finally {
      setBookmarkingId(null);
    }
  };

  // Open Chat for a given plant
  const handleOpenPlantChat = (plant?: Plant) => {
    const target = plant || selectedPlant || null;
    setChatPlant(target);
    setIsChatOpen(true);
    setChatError(null);

    // If starting chat on a new target plant, start fresh turn or check existing
    if (target) {
      const existingConv = conversations.find((c) => c.plant_id === target.id);
      if (existingConv && (!currentConversationId || currentConversationId !== existingConv.id)) {
        handleSelectConversation(existingConv.id);
        return;
      }
    }

    if (!currentConversationId) {
      // Seed a welcome message for the assistant
      setMessages([
        {
          id: -1,
          conversation_id: 0,
          role: 'assistant',
          content: target
            ? `Hello! I am your AI Agronomic Assistant for **${target.common_name}** (*${target.scientific_name}*).\n\nYou can ask me about soil pH, water cycles, fertilizer programs, yellow leaves, fungal blights, or request care steps in simple terms or Marathi.`
            : `Hello! I am CropGuard AI's Botanical & Plant Health Assistant. Select any crop from Plantopedia or ask me any crop care question to begin!`,
          created_at: new Date().toISOString()
        }
      ]);
    }
  };

  const handleStartNewChat = () => {
    setCurrentConversationId(null);
    setChatError(null);
    setGroundingSources([]);
    setActiveModel('');
    setIsFallbackMode(false);
    setMessages([
      {
        id: -1,
        conversation_id: 0,
        role: 'assistant',
        content: chatPlant
          ? `Started a new conversation for **${chatPlant.common_name}** (*${chatPlant.scientific_name}*). What would you like to know?`
          : `Started a new agronomic inquiry. Ask me anything about crop diseases, growing requirements, or field management.`,
        created_at: new Date().toISOString()
      }
    ]);
    setShowHistoryList(false);
  };

  const handleSelectConversation = async (convId: number) => {
    try {
      setSendingMessage(true);
      setShowHistoryList(false);
      const detail = await api.getConversationDetail(convId);
      setCurrentConversationId(detail.id);
      if (detail.plant) {
        setChatPlant(detail.plant);
      }
      setMessages(detail.messages);
      setChatError(null);
    } catch (err: any) {
      setChatError(err.message || 'Failed to load conversation history.');
    } finally {
      setSendingMessage(false);
    }
  };

  const handleDeleteConversation = async (convId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this conversation?')) return;
    try {
      await api.deleteConversation(convId);
      setConversations((prev) => prev.filter((c) => c.id !== convId));
      if (currentConversationId === convId) {
        handleStartNewChat();
      }
    } catch (err: any) {
      alert(err.message || 'Failed to delete conversation.');
    }
  };

  const handleSendMessage = async (customMessage?: string) => {
    const text = (customMessage || chatInput).trim();
    if (!text || sendingMessage) return;

    const userTurn: AssistantMessage = {
      id: Date.now(),
      conversation_id: currentConversationId || 0,
      role: 'user',
      content: text,
      created_at: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userTurn]);
    setChatInput('');
    setSendingMessage(true);
    setChatError(null);

    try {
      const response = await api.sendChatMessage({
        message: text,
        plant_id: chatPlant?.id,
        conversation_id: currentConversationId || undefined
      });

      setCurrentConversationId(response.conversation_id);
      setMessages((prev) => [...prev, response.message]);
      setGroundingSources(response.grounding_sources || []);
      setActiveModel(response.model);
      setIsFallbackMode(response.is_fallback);

      // Refresh conversations list in background
      loadConversations();
    } catch (err: any) {
      setChatError(err.message || 'Unable to connect to AI assistant. Please retry.');
    } finally {
      setSendingMessage(false);
    }
  };

  const quickPrompts = chatPlant ? [
    `What is the complete growing guide for ${chatPlant.common_name}?`,
    `Which soil type and pH are suitable?`,
    `What fertilizers are needed, and when?`,
    `What are common diseases and symptoms?`,
    `Why are leaves turning yellow or getting brown spots?`,
    `How to prevent pests naturally?`,
    `Explain this plant's care in simple language.`,
    `Explain this in Marathi.`
  ] : [
    'How does rainfall and humidity affect crop diseases?',
    'What is the difference between bacterial and fungal infections?',
    'What are the best natural pest control methods?'
  ];

  return (
    <Layout activeTitle="Plantopedia">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-bold text-[#8b958a] tracking-widest uppercase mb-1">
            BOTANICAL REFERENCE & INTELLIGENT ADVISOR
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-[#26332b] tracking-tight">
            Plantopedia AI Assistant
          </h1>
          <p className="text-xs text-[#788279] mt-0.5">
            Crop health profiles, soil guidelines, and conversational AI agronomy assistant.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Ask AI General Button */}
          <button
            onClick={() => handleOpenPlantChat()}
            className="px-4 py-2 text-xs font-bold rounded-xl bg-[#eff5e9] text-[#245c3a] border border-[#d2e3cb] hover:bg-[#e4eed9] transition flex items-center gap-2 shadow-xs"
          >
            <Sparkles className="w-3.5 h-3.5 text-[#245c3a]" />
            <span>Ask Plant AI</span>
          </button>

          {/* Saved Plants Toggle Button */}
          <button
            onClick={() => setFilterSavedOnly(!filterSavedOnly)}
            className={`px-4 py-2 text-xs font-bold rounded-xl border transition flex items-center gap-2 ${
              filterSavedOnly
                ? 'bg-[#245c3a] text-white border-[#245c3a]'
                : 'bg-white text-[#3f5b44] border-[#dfe6dc] hover:bg-[#f9fbf7]'
            }`}
          >
            <Bookmark className="w-3.5 h-3.5" />
            <span>{filterSavedOnly ? 'Showing Saved Plants' : 'View Saved Plants'}</span>
          </button>
        </div>
      </div>

      {/* Search & Suggestions Bar */}
      <div className="bg-white border border-[#e7ebe3] rounded-2xl p-4 shadow-xs mb-6 relative">
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-[#8b9689] absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Search by common name, scientific name, or family (e.g. Tomato, Oryza, Solanaceae)..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => {
                if (suggestions.length > 0) setShowSuggestions(true);
              }}
              className="w-full pl-10 pr-3 py-2.5 bg-[#fbfcf9] border border-[#e0e6dc] rounded-xl text-xs text-[#26332b] focus:border-[#245c3a] focus:ring-2 focus:ring-[#eff5e9] outline-none"
            />

            {/* Autocomplete Suggestions Dropdown */}
            {showSuggestions && suggestions.length > 0 && (
              <div className="absolute left-0 right-0 top-full mt-1.5 bg-white border border-[#dfe6dc] rounded-xl shadow-lg z-30 overflow-hidden divide-y divide-[#f2f4ef]">
                {suggestions.map((p) => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => handleSelectSuggestion(p)}
                    className="w-full text-left px-3.5 py-2.5 hover:bg-[#f6f9f3] flex items-center justify-between transition text-xs"
                  >
                    <div>
                      <strong className="text-[#26332b]">{p.common_name}</strong>
                      <span className="text-[#889286] italic ml-2">({p.scientific_name})</span>
                    </div>
                    {p.category && (
                      <span className="text-[10px] bg-[#eff5e9] text-[#245c3a] px-2 py-0.5 rounded-full font-medium">
                        {p.category}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          <button
            type="submit"
            className="px-5 py-2.5 bg-[#245c3a] hover:bg-[#1d4c2f] text-white text-xs font-bold rounded-xl transition shrink-0"
          >
            Search Plants
          </button>
        </form>

        {/* Data Source Strip */}
        <div className="mt-3 pt-3 border-t border-[#f0f2ed] flex flex-wrap items-center justify-between text-[11px] text-[#788279] gap-2">
          <div className="flex items-center gap-1.5">
            <Info className="w-3.5 h-3.5 text-[#245c3a]" />
            <span>
              Source Mode:{' '}
              <strong className="text-[#26332b]">
                {apiSource.includes('external_api')
                  ? apiSource.includes('Perenual')
                    ? 'External Botanical API (Perenual Botanical Service)'
                    : 'External Botanical API (Botanical Service)'
                  : 'Curated Agricultural Reference Database (Verified local starter catalog)'}
              </strong>
            </span>
          </div>
          <span className="text-[10px] text-[#8a9389]">
            {plants.length} plant record{plants.length === 1 ? '' : 's'} available
          </span>
        </div>
      </div>

      {/* Plant Grid or Loading State */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center text-xs text-[#899388]">
          <Loader2 className="w-8 h-8 animate-spin text-[#245c3a] mb-3" />
          <span>Fetching botanical records from database & API...</span>
        </div>
      ) : error ? (
        <div className="p-6 bg-[#faeeee] border border-[#f3d2d2] rounded-2xl text-[#a24e4a] text-xs flex items-start gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <div>
            <strong className="block font-bold">Failed to load Plantopedia records</strong>
            <p className="mt-1">{error}</p>
            <button
              onClick={() => fetchPlants(query)}
              className="mt-3 px-3 py-1.5 bg-[#a24e4a] text-white rounded-lg text-xs font-bold hover:bg-[#8e423e]"
            >
              Retry Search
            </button>
          </div>
        </div>
      ) : plants.length === 0 ? (
        <div className="py-16 text-center bg-white border border-dashed border-[#e7ebe3] rounded-2xl p-8">
          <div className="w-12 h-12 rounded-2xl bg-[#eff5e9] text-[#245c3a] flex items-center justify-center text-2xl mx-auto mb-3">
            🌱
          </div>
          <h3 className="text-base font-bold text-[#26332b]">No plants found</h3>
          <p className="text-xs text-[#788279] max-w-md mx-auto mt-1 mb-4">
            {filterSavedOnly
              ? "You haven't bookmarked any plants yet. Browse the full Plantopedia catalog to save crops to your personal library."
              : `We couldn't find matches for "${query}". Try searching for Tomato, Wheat, Rice, Cotton, Mango, Banana, or Neem.`}
          </p>
          {filterSavedOnly ? (
            <button
              onClick={() => setFilterSavedOnly(false)}
              className="px-4 py-2 bg-[#245c3a] text-white text-xs font-bold rounded-xl"
            >
              View All Plants
            </button>
          ) : (
            <button
              onClick={() => {
                setQuery('');
                setSearchParams({});
              }}
              className="px-4 py-2 bg-[#245c3a] text-white text-xs font-bold rounded-xl"
            >
              Clear Search
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {plants.map((plant) => (
            <article
              key={plant.id}
              onClick={() => setSelectedPlant(plant)}
              className="bg-white border border-[#e7ebe3] hover:border-[#b4cfb0] rounded-2xl overflow-hidden shadow-xs hover:shadow-md transition cursor-pointer flex flex-col group"
            >
              {/* Plant Image / Banner */}
              <div className="h-44 bg-[#eef3e9] relative overflow-hidden flex items-center justify-center">
                {plant.image_url ? (
                  <img
                    src={plant.image_url}
                    alt={plant.common_name}
                    className="w-full h-full object-cover transition duration-300 group-hover:scale-105"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = 'none';
                    }}
                  />
                ) : (
                  <span className="text-5xl">🌿</span>
                )}
                {/* Source Badge */}
                <div className="absolute left-3 top-3 bg-white/90 backdrop-blur-xs px-2 py-0.5 rounded-md text-[9px] font-bold text-[#4e5c50] tracking-wide uppercase">
                  {plant.source_type === 'curated_local' ? 'Curated Reference' : 'API Record'}
                </div>
                {/* Bookmark Toggle */}
                <button
                  type="button"
                  onClick={(e) => handleToggleBookmark(plant, e)}
                  disabled={bookmarkingId === plant.id}
                  className={`absolute right-3 top-3 w-8 h-8 rounded-full flex items-center justify-center shadow-xs transition ${
                    plant.is_bookmarked
                      ? 'bg-[#245c3a] text-white'
                      : 'bg-white/90 text-[#4e5c50] hover:text-[#245c3a]'
                  }`}
                  title={plant.is_bookmarked ? 'Remove bookmark' : 'Bookmark plant'}
                >
                  {bookmarkingId === plant.id ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : plant.is_bookmarked ? (
                    <BookmarkCheck className="w-4 h-4" />
                  ) : (
                    <Bookmark className="w-4 h-4" />
                  )}
                </button>
              </div>

              {/* Plant Body */}
              <div className="p-5 flex-1 flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <div>
                      <h3 className="text-base font-bold text-[#26332b] leading-snug">
                        {plant.common_name}
                      </h3>
                      <p className="text-xs text-[#8a9389] italic">
                        {plant.scientific_name}
                      </p>
                    </div>
                    {plant.family && (
                      <span className="text-[10px] bg-[#eff5e9] text-[#245c3a] font-semibold px-2 py-0.5 rounded-full shrink-0">
                        {plant.family.split(' ')[0]}
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-[#788279] line-clamp-2 mt-2 leading-relaxed">
                    {plant.description}
                  </p>
                </div>

                {/* Quick Action Button Strip */}
                <div className="mt-4 pt-3 border-t border-[#f0f2ed] flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 text-[11px] text-[#526450] truncate">
                    <Sun className="w-3.5 h-3.5 text-[#ad781d] shrink-0" />
                    <span className="truncate">{plant.sunlight.split('(')[0]}</span>
                  </div>

                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleOpenPlantChat(plant);
                    }}
                    className="px-2.5 py-1 rounded-lg bg-[#eff5e9] hover:bg-[#245c3a] text-[#245c3a] hover:text-white transition text-[11px] font-bold flex items-center gap-1 shrink-0"
                    title="Ask AI about this plant"
                  >
                    <Sparkles className="w-3 h-3" />
                    <span>Ask AI</span>
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}

      {/* Plant Detail Modal */}
      {selectedPlant && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 backdrop-blur-xs animate-fade-in">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-[#e7ebe3] shadow-2xl">
            {/* Modal Header Image */}
            <div className="h-56 bg-[#eef3e9] relative overflow-hidden flex items-center justify-center">
              {selectedPlant.image_url ? (
                <img
                  src={selectedPlant.image_url}
                  alt={selectedPlant.common_name}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.target as HTMLElement).style.display = 'none';
                  }}
                />
              ) : (
                <span className="text-6xl">🌿</span>
              )}
              <button
                onClick={() => setSelectedPlant(null)}
                className="absolute top-4 right-4 w-8 h-8 rounded-full bg-white/90 text-[#26332b] flex items-center justify-center hover:bg-white shadow-md transition"
              >
                <X className="w-4 h-4" />
              </button>
              <div className="absolute left-4 bottom-4 bg-white/95 backdrop-blur-xs px-3 py-1 rounded-lg text-xs font-bold text-[#245c3a] shadow-sm flex items-center gap-1.5">
                <span>{selectedPlant.source_type === 'curated_local' ? 'Curated Database' : 'External Botanical API'}</span>
                {selectedPlant.data_source && (
                  <span className="text-[#788279] text-[10px] font-normal">({selectedPlant.data_source})</span>
                )}
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#f0f2ed]">
                <div>
                  <h2 className="text-2xl font-extrabold text-[#26332b]">
                    {selectedPlant.common_name}
                  </h2>
                  <p className="text-xs text-[#8a9389] italic font-medium mt-0.5">
                    {selectedPlant.scientific_name} · {selectedPlant.family || 'Botanical Family'} · {selectedPlant.category || 'Crop'}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      const p = selectedPlant;
                      setSelectedPlant(null);
                      handleOpenPlantChat(p);
                    }}
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-[#245c3a] text-white hover:bg-[#1d4c2f] flex items-center gap-1.5 shadow-xs transition"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Ask AI About This Plant</span>
                  </button>

                  <button
                    onClick={() => handleToggleBookmark(selectedPlant)}
                    disabled={bookmarkingId === selectedPlant.id}
                    className={`p-2 rounded-xl text-xs font-bold transition border ${
                      selectedPlant.is_bookmarked
                        ? 'bg-[#edf4e8] text-[#245c3a] border-[#c8dec2]'
                        : 'bg-white text-[#556353] border-[#dfe6dc] hover:bg-[#f6f9f3]'
                    }`}
                    title={selectedPlant.is_bookmarked ? 'Saved to bookmarks' : 'Bookmark plant'}
                  >
                    {selectedPlant.is_bookmarked ? (
                      <BookmarkCheck className="w-4 h-4 text-[#245c3a]" />
                    ) : (
                      <Bookmark className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Description */}
              <div className="py-4">
                <h4 className="text-xs font-bold text-[#8b958a] tracking-wider uppercase mb-1.5">
                  Agronomic Overview
                </h4>
                <p className="text-xs text-[#4e5c50] leading-relaxed">
                  {selectedPlant.description}
                </p>
              </div>

              {/* Key Growing Requirement Specs */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 my-3">
                <div className="p-3.5 bg-[#fbfcf9] border border-[#e8eddf] rounded-xl">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#ad781d] mb-1">
                    <Sun className="w-4 h-4" />
                    <span>Sunlight Requirements</span>
                  </div>
                  <p className="text-xs text-[#637064]">{selectedPlant.sunlight}</p>
                </div>

                <div className="p-3.5 bg-[#fbfcf9] border border-[#e8eddf] rounded-xl">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#416c9c] mb-1">
                    <Droplets className="w-4 h-4" />
                    <span>Watering & Irrigation</span>
                  </div>
                  <p className="text-xs text-[#637064]">{selectedPlant.watering}</p>
                </div>

                <div className="p-3.5 bg-[#fbfcf9] border border-[#e8eddf] rounded-xl">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#76541a] mb-1">
                    <Layers className="w-4 h-4" />
                    <span>Soil & pH Requirements</span>
                  </div>
                  <p className="text-xs text-[#637064]">{selectedPlant.soil_requirements}</p>
                </div>

                <div className="p-3.5 bg-[#fbfcf9] border border-[#e8eddf] rounded-xl">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#37774b] mb-1">
                    <CloudSun className="w-4 h-4" />
                    <span>Climate & Ideal Temp</span>
                  </div>
                  <p className="text-xs text-[#637064]">
                    {selectedPlant.climate}
                    {selectedPlant.temperature_range && ` (${selectedPlant.temperature_range})`}
                  </p>
                </div>
              </div>

              {/* Fertilizer & Seasonal Specs */}
              {(selectedPlant.fertilizer || selectedPlant.season) && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 my-3">
                  {selectedPlant.fertilizer && (
                    <div className="p-3.5 bg-[#fbfcf9] border border-[#e8eddf] rounded-xl">
                      <div className="flex items-center gap-2 text-xs font-bold text-[#4a6b32] mb-1">
                        <BookOpen className="w-4 h-4" />
                        <span>Fertilizer Needs</span>
                      </div>
                      <p className="text-xs text-[#637064] leading-relaxed">{selectedPlant.fertilizer}</p>
                    </div>
                  )}

                  {selectedPlant.season && (
                    <div className="p-3.5 bg-[#fbfcf9] border border-[#e8eddf] rounded-xl">
                      <div className="flex items-center gap-2 text-xs font-bold text-[#786131] mb-1">
                        <Calendar className="w-4 h-4" />
                        <span>Growing Season</span>
                      </div>
                      <p className="text-xs text-[#637064]">{selectedPlant.season}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Diseases and Pest Guidelines */}
              {(selectedPlant.common_diseases || selectedPlant.common_pests) && (
                <div className="py-3 border-t border-[#f0f2ed] space-y-3">
                  <h4 className="text-xs font-bold text-[#8b958a] tracking-wider uppercase">
                    Crop Protection & Pathology
                  </h4>

                  {selectedPlant.common_diseases && (
                    <div className="p-3 bg-[#faeeee] border border-[#f3d3d3] rounded-xl text-xs text-[#873a36]">
                      <div className="flex items-center gap-1.5 font-bold mb-1">
                        <ShieldAlert className="w-3.5 h-3.5 text-[#a24e4a]" />
                        <span>Common Diseases</span>
                      </div>
                      <p className="leading-relaxed">{selectedPlant.common_diseases}</p>
                    </div>
                  )}

                  {selectedPlant.common_pests && (
                    <div className="p-3 bg-[#fff8eb] border border-[#f5e3be] rounded-xl text-xs text-[#8a5b17]">
                      <div className="flex items-center gap-1.5 font-bold mb-1">
                        <Bug className="w-3.5 h-3.5 text-[#ad781d]" />
                        <span>Common Pests</span>
                      </div>
                      <p className="leading-relaxed">{selectedPlant.common_pests}</p>
                    </div>
                  )}

                  {selectedPlant.prevention_treatment && (
                    <div className="p-3 bg-[#f0f7ec] border border-[#d6ebd0] rounded-xl text-xs text-[#2a5b33]">
                      <strong className="block font-bold mb-1">Integrated Management & Prevention:</strong>
                      <p className="leading-relaxed">{selectedPlant.prevention_treatment}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Cultivation Conditions */}
              <div className="py-3 border-t border-[#f0f2ed]">
                <h4 className="text-xs font-bold text-[#8b958a] tracking-wider uppercase mb-1.5">
                  Cultivation & Management
                </h4>
                <p className="text-xs text-[#4e5c50] leading-relaxed">
                  {selectedPlant.growing_conditions}
                </p>
              </div>

              {/* Facts / Agricultural Notes */}
              {selectedPlant.facts && (
                <div className="p-3.5 bg-[#eef5e8] border border-[#e1ecd8] rounded-xl text-xs text-[#35543b] mt-2">
                  <strong className="block font-bold mb-0.5">Agricultural Fact:</strong>
                  <span>{selectedPlant.facts}</span>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 bg-[#fbfcf9] border-t border-[#f0f2ed] flex justify-end">
              <button
                onClick={() => setSelectedPlant(null)}
                className="px-5 py-2 bg-[#245c3a] text-white text-xs font-bold rounded-xl hover:bg-[#1d4c2f]"
              >
                Close Profile
              </button>
            </div>
          </div>
        </div>
      )}

      {/* AI Plant Assistant Chat Drawer / Sliding Panel */}
      {isChatOpen && (
        <div className="fixed inset-0 z-50 flex justify-end animate-fade-in">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-xs transition"
            onClick={() => setIsChatOpen(false)}
          />

          {/* Drawer Body */}
          <div className="relative w-full max-w-lg bg-white h-full shadow-2xl flex flex-col z-10 border-l border-[#e7ebe3]">
            {/* Drawer Header */}
            <div className="p-4 border-b border-[#e7ebe3] bg-[#fbfcf9] flex items-center justify-between">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="w-8 h-8 rounded-xl bg-[#245c3a] text-white flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <h3 className="text-sm font-bold text-[#26332b] truncate">
                    Plantopedia AI Assistant
                  </h3>
                  <p className="text-[10px] text-[#788279] truncate">
                    {chatPlant
                      ? `Focused on ${chatPlant.common_name} (${chatPlant.scientific_name})`
                      : 'General Agricultural Advisory Mode'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-1.5">
                {/* Conversation History Toggle */}
                <button
                  type="button"
                  onClick={() => setShowHistoryList(!showHistoryList)}
                  className={`p-2 rounded-lg text-xs font-bold transition flex items-center gap-1 ${
                    showHistoryList
                      ? 'bg-[#245c3a] text-white'
                      : 'bg-[#edf4e8] text-[#245c3a] hover:bg-[#dcecc9]'
                  }`}
                  title="View past conversation history"
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">History ({conversations.length})</span>
                </button>

                {/* New Chat Button */}
                <button
                  type="button"
                  onClick={handleStartNewChat}
                  className="p-2 rounded-lg bg-white border border-[#dfe6dc] text-[#556353] hover:bg-[#f6f9f3] transition text-xs font-bold"
                  title="Start a new chat"
                >
                  <PlusCircle className="w-3.5 h-3.5" />
                </button>

                {/* Close Drawer */}
                <button
                  type="button"
                  onClick={() => setIsChatOpen(false)}
                  className="p-2 rounded-lg text-[#788279] hover:text-[#26332b] transition"
                  title="Close assistant"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Conversation History Popout overlay */}
            {showHistoryList && (
              <div className="bg-[#f8faf6] border-b border-[#e7ebe3] max-h-56 overflow-y-auto p-3 space-y-1.5 divide-y divide-[#ecefe8]">
                <div className="text-[10px] font-bold text-[#8a9488] uppercase tracking-wider mb-2">
                  Saved Plant Conversations
                </div>
                {conversations.length === 0 ? (
                  <p className="text-xs text-[#8a9488] py-2 text-center">
                    No past conversations found. Ask a question to start your first chat!
                  </p>
                ) : (
                  conversations.map((c) => (
                    <div
                      key={c.id}
                      onClick={() => handleSelectConversation(c.id)}
                      className={`pt-2 flex items-center justify-between text-xs cursor-pointer rounded-lg p-2 transition ${
                        currentConversationId === c.id
                          ? 'bg-[#245c3a] text-white font-bold'
                          : 'hover:bg-white text-[#334237]'
                      }`}
                    >
                      <div className="min-w-0 pr-2">
                        <strong className="block truncate">{c.title}</strong>
                        {c.last_message && (
                          <span className={`block text-[10px] truncate ${currentConversationId === c.id ? 'text-white/80' : 'text-[#8a9488]'}`}>
                            {c.last_message}
                          </span>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={(e) => handleDeleteConversation(c.id, e)}
                        className={`p-1 rounded-md transition shrink-0 ${
                          currentConversationId === c.id
                            ? 'text-white/70 hover:text-white'
                            : 'text-[#8a9488] hover:text-[#a24e4a]'
                        }`}
                        title="Delete conversation"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Grounding & Provider Status Strip */}
            <div className="bg-[#f0f4ec] px-4 py-1.5 border-b border-[#e3ebdd] flex items-center justify-between text-[10px] text-[#556754]">
              <div className="flex items-center gap-1.5 truncate">
                <Sparkles className="w-3 h-3 text-[#245c3a] shrink-0" />
                <span className="truncate">
                  {isFallbackMode
                    ? 'CropGuard Verified Knowledgebase (Offline Mode)'
                    : activeModel
                    ? `Provider: ${activeModel}`
                    : 'Grounded Agricultural Model'}
                </span>
              </div>
              {groundingSources.length > 0 && (
                <span className="text-[9px] bg-white text-[#245c3a] font-bold px-1.5 py-0.5 rounded shadow-xs shrink-0">
                  {groundingSources.length} Grounded Source{groundingSources.length === 1 ? '' : 's'}
                </span>
              )}
            </div>

            {/* Chat Messages Body */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-[#fbfcf9]">
              {messages.map((m, idx) => {
                const isAssistant = m.role === 'assistant';
                return (
                  <div
                    key={idx}
                    className={`flex flex-col ${isAssistant ? 'items-start' : 'items-end'}`}
                  >
                    <div
                      className={`max-w-[88%] rounded-2xl p-3.5 text-xs leading-relaxed shadow-xs ${
                        isAssistant
                          ? 'bg-white text-[#26332b] border border-[#e5eae0]'
                          : 'bg-[#245c3a] text-white'
                      }`}
                    >
                      {/* Markdown rendering simplified and sanitized */}
                      <div className="whitespace-pre-wrap space-y-1">
                        {m.content.split('\n').map((line, lIdx) => {
                          if (line.startsWith('### ')) {
                            return (
                              <h4 key={lIdx} className="font-extrabold text-sm text-[#1e482e] pt-1 pb-0.5">
                                {line.replace('### ', '')}
                              </h4>
                            );
                          }
                          if (line.startsWith('#### ')) {
                            return (
                              <h5 key={lIdx} className="font-bold text-xs text-[#26332b] pt-1">
                                {line.replace('#### ', '')}
                              </h5>
                            );
                          }
                          if (line.startsWith('> [!NOTE]') || line.startsWith('> [!WARNING]') || line.startsWith('> [!IMPORTANT]')) {
                            return null;
                          }
                          if (line.startsWith('> ')) {
                            return (
                              <blockquote key={lIdx} className="border-l-2 border-[#245c3a] pl-2 text-[11px] text-[#556353] italic my-1">
                                {line.replace('> ', '')}
                              </blockquote>
                            );
                          }
                          return (
                            <p key={lIdx} className="leading-relaxed">
                              {line}
                            </p>
                          );
                        })}
                      </div>

                      {/* Message Timestamp */}
                      <div className={`mt-2 pt-1 border-t text-[9px] flex items-center justify-between ${
                        isAssistant ? 'border-[#f2f4ef] text-[#939c90]' : 'border-white/20 text-white/70'
                      }`}>
                        <span>{isAssistant ? 'CropGuard AI' : 'You'}</span>
                        <span>{new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      </div>
                    </div>
                  </div>
                );
              })}

              {sendingMessage && (
                <div className="flex items-center gap-2 text-xs text-[#6e7d6b] p-3 bg-white border border-[#e5eae0] rounded-2xl w-fit">
                  <Loader2 className="w-4 h-4 animate-spin text-[#245c3a]" />
                  <span>Synthesizing botanical advice & grounding facts...</span>
                </div>
              )}

              {chatError && (
                <div className="p-3 bg-[#faeeee] border border-[#f3d2d2] rounded-xl text-[#a24e4a] text-xs flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <span>{chatError}</span>
                    <button
                      onClick={() => handleSendMessage()}
                      className="block mt-1 font-bold underline"
                    >
                      Retry turn
                    </button>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Quick Suggestion Chips */}
            <div className="p-2 bg-[#f4f7f1] border-t border-[#e7ebe3] overflow-x-auto whitespace-nowrap flex gap-1.5">
              {quickPrompts.map((q, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => handleSendMessage(q)}
                  disabled={sendingMessage}
                  className="px-2.5 py-1 rounded-lg bg-white border border-[#dfe6dc] hover:border-[#245c3a] text-[#334237] text-[10px] font-medium transition shrink-0"
                >
                  {q}
                </button>
              ))}
            </div>

            {/* Chat Input Bar */}
            <div className="p-3 bg-white border-t border-[#e7ebe3]">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSendMessage();
                }}
                className="flex items-center gap-2"
              >
                <input
                  type="text"
                  placeholder={
                    chatPlant
                      ? `Ask anything about ${chatPlant.common_name}...`
                      : 'Ask a plant care question...'
                  }
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  disabled={sendingMessage}
                  className="flex-1 px-3 py-2 bg-[#fbfcf9] border border-[#dfe6dc] rounded-xl text-xs text-[#26332b] focus:border-[#245c3a] focus:ring-1 focus:ring-[#245c3a] outline-none"
                />
                <button
                  type="submit"
                  disabled={!chatInput.trim() || sendingMessage}
                  className="p-2.5 bg-[#245c3a] hover:bg-[#1d4c2f] disabled:bg-[#a0baa8] text-white rounded-xl transition shrink-0 shadow-xs"
                >
                  {sendingMessage ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
};
