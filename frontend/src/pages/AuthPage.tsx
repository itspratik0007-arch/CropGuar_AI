import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { ShieldCheck, Mail, Lock, User as UserIcon, ArrowRight, AlertCircle, Loader2 } from 'lucide-react';

interface AuthModalProps {
  initialMode?: 'login' | 'register';
  isOpen?: boolean;
}

export const AuthPage: React.FC<AuthModalProps> = ({ initialMode = 'login' }) => {
  const [isLogin, setIsLogin] = useState(initialMode === 'login');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email || !password) {
      setError('Please provide both email and password.');
      return;
    }

    if (!isLogin) {
      if (!fullName.trim()) {
        setError('Please enter your full name.');
        return;
      }
      if (password !== confirmPassword) {
        setError('Passwords do not match. Please verify your password confirmation.');
        return;
      }
      if (password.length < 6) {
        setError('Password must be at least 6 characters long.');
        return;
      }
    }

    setIsSubmitting(true);
    try {
      if (isLogin) {
        const res = await api.login({ email, password });
        login(res.access_token, res.user);
        navigate('/');
      } else {
        const res = await api.register({
          full_name: fullName,
          email,
          password,
          confirm_password: confirmPassword,
        });
        login(res.access_token, res.user);
        navigate('/');
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check your inputs.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f7f8f4] flex flex-col justify-center items-center px-4 py-12">
      {/* Brand Header */}
      <div className="flex items-center gap-2 mb-8">
        <div className="w-10 h-10 rounded-xl bg-[#245c3a] text-white flex items-center justify-center text-xl font-bold">
          ✳
        </div>
        <div>
          <span className="text-xl font-extrabold tracking-tight text-[#26332b]">
            CropShield <span className="text-[#37774b]">AI</span>
          </span>
          <span className="block text-[11px] text-[#788279] font-medium tracking-wide">
            Crop Health Intelligence
          </span>
        </div>
      </div>

      {/* Auth Card */}
      <div className="w-full max-w-md bg-white border border-[#e7ebe3] rounded-2xl shadow-[0_8px_28px_rgba(38,51,43,0.045)] p-8">
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-bold tracking-wider text-[#8b958a] uppercase">
              {isLogin ? 'Welcome Back' : 'Farmer Workspace'}
            </span>
            <span className="text-[11px] text-[#245c3a] font-semibold bg-[#eff5e9] px-2.5 py-0.5 rounded-full">
              Phase 1
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-[#26332b]">
            {isLogin ? 'Sign in to your farm' : 'Create your account'}
          </h1>
          <p className="text-xs text-[#788279] mt-1">
            {isLogin
              ? 'Access your authenticated crop records and Plantopedia.'
              : 'Join CropShield AI to organize crops and explore botanical guidance.'}
          </p>
        </div>

        {error && (
          <div className="mb-5 p-3.5 bg-[#faeeee] border border-[#f3d2d2] rounded-xl flex items-start gap-2.5 text-[#a24e4a] text-xs">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-xs font-semibold text-[#4e5c50] mb-1.5" htmlFor="fullName">
                Full Name
              </label>
              <div className="relative">
                <UserIcon className="w-4 h-4 text-[#8a948a] absolute left-3.5 top-3" />
                <input
                  id="fullName"
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Ramesh Patil"
                  className="w-full pl-10 pr-3 py-2.5 bg-white border border-[#dfe6dc] rounded-lg text-xs text-[#26332b] focus:border-[#245c3a] focus:ring-2 focus:ring-[#eff5e9] outline-none transition"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-[#4e5c50] mb-1.5" htmlFor="email">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-[#8a948a] absolute left-3.5 top-3" />
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="farmer@example.com"
                className="w-full pl-10 pr-3 py-2.5 bg-white border border-[#dfe6dc] rounded-lg text-xs text-[#26332b] focus:border-[#245c3a] focus:ring-2 focus:ring-[#eff5e9] outline-none transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#4e5c50] mb-1.5" htmlFor="password">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-[#8a948a] absolute left-3.5 top-3" />
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-3 py-2.5 bg-white border border-[#dfe6dc] rounded-lg text-xs text-[#26332b] focus:border-[#245c3a] focus:ring-2 focus:ring-[#eff5e9] outline-none transition"
              />
            </div>
          </div>

          {!isLogin && (
            <div>
              <label className="block text-xs font-semibold text-[#4e5c50] mb-1.5" htmlFor="confirmPassword">
                Confirm Password
              </label>
              <div className="relative">
                <ShieldCheck className="w-4 h-4 text-[#8a948a] absolute left-3.5 top-3" />
                <input
                  id="confirmPassword"
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-3 py-2.5 bg-white border border-[#dfe6dc] rounded-lg text-xs text-[#26332b] focus:border-[#245c3a] focus:ring-2 focus:ring-[#eff5e9] outline-none transition"
                />
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full mt-2 py-2.5 px-4 bg-[#245c3a] hover:bg-[#1d4c2f] disabled:opacity-70 text-white text-xs font-bold rounded-lg shadow-sm flex items-center justify-center gap-2 transition"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <span>{isLogin ? 'Sign In' : 'Create Free Account'}</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        <div className="mt-6 pt-5 border-t border-[#f0f2ed] text-center">
          <p className="text-xs text-[#788279]">
            {isLogin ? "Don't have an account yet?" : 'Already have an account?'}
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setError(null);
              }}
              className="ml-2 font-bold text-[#245c3a] hover:underline"
            >
              {isLogin ? 'Register now' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>

      <div className="mt-8 text-center text-xs text-[#9aa196]">
        CropShield AI · Protected by Argon2id password encryption & JWT tokens.
      </div>
    </div>
  );
};
