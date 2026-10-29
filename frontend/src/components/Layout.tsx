import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Home, 
  BookOpen, 
  MapPin, 
  HelpCircle, 
  LogOut, 
  Menu, 
  X, 
  Camera, 
  Activity, 
  Stethoscope,
  ChevronDown
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
  activeTitle: string;
}

export const Layout: React.FC<LayoutProps> = ({ children, activeTitle }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [showGuide, setShowGuide] = useState(false);

  const getInitials = (name?: string) => {
    if (!name) return 'CS';
    return name
      .split(' ')
      .map((n) => n[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  };

  const handleLogout = async () => {
    await logout();
    navigate('/auth');
  };

  return (
    <div className="min-h-screen bg-[#f7f8f4] text-[#26332b]">
      {/* Mobile Backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-30 md:hidden backdrop-blur-xs"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 w-[246px] bg-white border-r border-[#e7ebe3] p-5 flex flex-col transition-transform duration-200 ease-in-out md:translate-x-0 ${
          sidebarOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'
        }`}
      >
        {/* Brand */}
        <div className="flex items-center justify-between pb-7 px-1">
          <NavLink to="/" className="flex items-center gap-2.5 text-decoration-none text-[#26332b]">
            <span className="w-9 h-9 rounded-xl bg-[#245c3a] text-white flex items-center justify-center font-bold text-lg">
              ✳
            </span>
            <div>
              <div className="font-extrabold text-base tracking-tight leading-none text-[#26332b]">
                CropShield<span className="text-[#37774b]"> AI</span>
              </div>
              <small className="block text-[10px] text-[#8a948a] font-medium tracking-wide mt-0.5">
                Crop health intelligence
              </small>
            </div>
          </NavLink>
          <button
            onClick={() => setSidebarOpen(false)}
            className="md:hidden text-[#788279] hover:text-[#26332b]"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="text-[10px] tracking-widest font-bold text-[#8b958a] px-3 pb-3 uppercase">
          WORKSPACE
        </div>

        {/* Navigation */}
        <nav className="space-y-1">
          <NavLink
            to="/"
            onClick={() => setSidebarOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-xs transition ${
                isActive
                  ? 'bg-[#edf4e8] text-[#245c3a] font-bold'
                  : 'text-[#707a71] hover:bg-[#f5f7f2] hover:text-[#245c3a]'
              }`
            }
          >
            <Home className="w-4 h-4" />
            <span>Dashboard</span>
          </NavLink>

          <NavLink
            to="/plantopedia"
            onClick={() => setSidebarOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-xs transition ${
                isActive
                  ? 'bg-[#edf4e8] text-[#245c3a] font-bold'
                  : 'text-[#707a71] hover:bg-[#f5f7f2] hover:text-[#245c3a]'
              }`
            }
          >
            <BookOpen className="w-4 h-4" />
            <span>Plantopedia</span>
            <span className="ml-auto text-[9px] bg-[#dcecc9] text-[#245c3a] px-1.5 py-0.5 rounded font-bold">
              API
            </span>
          </NavLink>

          <NavLink
            to="/stores"
            onClick={() => setSidebarOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-xs transition ${
                isActive
                  ? 'bg-[#edf4e8] text-[#245c3a] font-bold'
                  : 'text-[#707a71] hover:bg-[#f5f7f2] hover:text-[#245c3a]'
              }`
            }
          >
            <MapPin className="w-4 h-4" />
            <span>Nearby Stores</span>
            <span className="ml-auto text-[9px] bg-[#fff2d8] text-[#ad781d] px-1.5 py-0.5 rounded font-bold">
              Demo
            </span>
          </NavLink>

          <NavLink
            to="/disease"
            onClick={() => setSidebarOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-xs transition ${
                isActive
                  ? 'bg-[#edf4e8] text-[#245c3a] font-bold'
                  : 'text-[#707a71] hover:bg-[#f5f7f2] hover:text-[#245c3a]'
              }`
            }
          >
            <Camera className="w-4 h-4 text-[#37774b]" />
            <span>Disease Detection</span>
            <span className="ml-auto text-[9px] bg-[#dcecc9] text-[#245c3a] px-1.5 py-0.5 rounded font-bold">
              AI
            </span>
          </NavLink>

          {/* Phase 2 Feature items explicitly disabled */}
          <div className="pt-4 pb-2 px-3 text-[10px] font-bold tracking-wider text-[#a0a89f] uppercase">
            Future Scope (Phase 2)
          </div>

          <div
            title="Out of scope for Phase 1. Available in Phase 2."
            className="flex items-center justify-between px-3 py-2.5 rounded-xl text-xs text-[#a1a89f] bg-transparent cursor-not-allowed opacity-60"
          >
            <div className="flex items-center gap-3">
              <Activity className="w-4 h-4" />
              <span>Risk Prediction</span>
            </div>
            <span className="text-[9px] bg-[#f0f2ed] text-[#788276] px-1.5 py-0.5 rounded font-semibold">
              Soon
            </span>
          </div>

          <div
            title="Out of scope for Phase 1. Available in Phase 2."
            className="flex items-center justify-between px-3 py-2.5 rounded-xl text-xs text-[#a1a89f] bg-transparent cursor-not-allowed opacity-60"
          >
            <div className="flex items-center gap-3">
              <Stethoscope className="w-4 h-4" />
              <span>Remedies & Advice</span>
            </div>
            <span className="text-[9px] bg-[#f0f2ed] text-[#788276] px-1.5 py-0.5 rounded font-semibold">
              Soon
            </span>
          </div>
        </nav>

        {/* Sidebar Bottom */}
        <div className="mt-auto pt-4">
          <div className="bg-[#f6f8f1] border border-[#e8eddf] rounded-xl p-3.5 mb-4">
            <div className="w-6 h-6 rounded-lg bg-[#e3ecd8] text-[#245c3a] flex items-center justify-center text-xs font-bold mb-2">
              <HelpCircle className="w-3.5 h-3.5" />
            </div>
            <strong className="block text-xs font-bold text-[#26332b]">CropShield Guide</strong>
            <p className="text-[11px] text-[#788279] mt-0.5 mb-2 leading-tight">
              Phase 1 includes Plantopedia, Saved Bookmarks & Demo Stores.
            </p>
            <button
              onClick={() => setShowGuide(true)}
              className="text-[11px] text-[#245c3a] font-bold hover:underline flex items-center gap-1"
            >
              <span>View phase scope</span>
              <span>↗</span>
            </button>
          </div>

          <div className="border-t border-[#e7ebe3] pt-3.5 flex items-center justify-between">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-8 h-8 rounded-full bg-[#e2ebdc] text-[#245c3a] font-extrabold text-xs flex items-center justify-center shrink-0">
                {getInitials(user?.full_name)}
              </div>
              <div className="min-w-0">
                <strong className="block text-xs truncate text-[#26332b]">{user?.full_name || 'Farmer'}</strong>
                <small className="block text-[10px] text-[#788279] truncate">{user?.email || 'Logged in'}</small>
              </div>
            </div>
            <button
              onClick={handleLogout}
              title="Sign out"
              className="text-[#788279] hover:text-[#a24e4a] p-1 rounded-md transition"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Container */}
      <div className="md:ml-[246px] min-h-screen flex flex-col">
        {/* Topbar */}
        <header className="h-16 px-6 border-b border-[#e7ebe3] bg-white flex items-center justify-between sticky top-0 z-20">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden text-[#245c3a] p-1.5 rounded-lg border border-[#e7ebe3]"
              aria-label="Open menu"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="text-xs text-[#899187]">
              Workspace <span className="text-[#b3bbb2] px-1.5">/</span>{' '}
              <strong className="text-[#39453b] font-semibold">{activeTitle}</strong>
            </div>
          </div>

          <div className="flex items-center gap-3.5">
            <div className="hidden sm:flex items-center gap-2 text-[11px] text-[#637064] border border-[#e7ebe3] rounded-lg px-2.5 py-1.5 bg-[#fbfcf9]">
              <MapPin className="w-3.5 h-3.5 text-[#245c3a]" />
              <span>{user?.farm_location || 'Demo farm workspace'}</span>
            </div>

            <div className="relative">
              <button
                onClick={() => setProfileOpen(!profileOpen)}
                className="flex items-center gap-2 text-xs text-[#566157] py-1 px-1.5 rounded-lg hover:bg-[#f5f7f2] transition"
              >
                <div className="w-7 h-7 rounded-full bg-[#e2ebdc] text-[#245c3a] font-bold text-[10px] flex items-center justify-center">
                  {getInitials(user?.full_name)}
                </div>
                <span className="hidden md:inline font-semibold text-[#26332b]">
                  {user?.full_name?.split(' ')[0] || 'Farmer'}
                </span>
                <ChevronDown className="w-3.5 h-3.5 text-[#8b958a]" />
              </button>

              {profileOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white border border-[#e7ebe3] rounded-xl shadow-lg py-1.5 z-30">
                  <div className="px-3 py-2 border-b border-[#f0f2ed]">
                    <div className="text-xs font-bold text-[#26332b]">{user?.full_name}</div>
                    <div className="text-[10px] text-[#788279] truncate">{user?.email}</div>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-3 py-2 text-xs text-[#a24e4a] hover:bg-[#faeeee] flex items-center gap-2"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Sign Out</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Content View */}
        <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto animate-fade-in">
          {children}
        </main>

        {/* Footer */}
        <footer className="px-6 py-4 border-t border-[#e7ebe3] text-[11px] text-[#9aa196] flex flex-col sm:flex-row items-center justify-between gap-2 max-w-7xl w-full mx-auto">
          <div className="flex items-center gap-1.5 font-bold text-[#6f7e6c]">
            <span>✳ CropShield AI</span>
            <span className="font-normal text-[#9aa196]">· Phase 1 Working Application</span>
          </div>
          <div>Database & API Connected · Argon2id Authenticated</div>
        </footer>
      </div>

      {/* Quick Guide Modal */}
      {showGuide && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 border border-[#e7ebe3] shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#8b958a]">
                CropShield AI Phase 1
              </span>
              <button
                onClick={() => setShowGuide(false)}
                className="text-[#788279] hover:text-[#26332b] p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <h3 className="text-lg font-bold text-[#26332b] mb-2">Scope of This Release</h3>
            <div className="space-y-3 text-xs text-[#526052] leading-relaxed">
              <p>
                <strong>Active Features:</strong> User Registration & Login with Argon2id encryption, PostgreSQL database persistence, authenticated dashboard with live bookmark metrics, interactive Plantopedia with external API & local curated fallback data, and categorized demo nearby agricultural stores.
              </p>
              <p>
                <strong>Future Scope (Phase 2):</strong> Camera plant disease classification, weather-driven risk prediction model, and AI treatment remedies are explicitly marked as "Coming Soon" to maintain scientific transparency.
              </p>
            </div>
            <button
              onClick={() => setShowGuide(false)}
              className="mt-6 w-full py-2 bg-[#245c3a] text-white rounded-lg text-xs font-bold hover:bg-[#1d4c2f]"
            >
              Understood
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
