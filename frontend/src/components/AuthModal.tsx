import React, { useState } from 'react';
import { signUpWithEmail, loginWithEmail } from '../utils/firebase';
import { X, Mail, Lock, Key, UserCheck } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!email.trim() || !password.trim()) {
      setError("Please fill in all fields.");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    
    setLoading(true);
    try {
      if (isSignUp) {
        await signUpWithEmail(email, password);
      } else {
        await loginWithEmail(email, password);
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Authentication failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div className="w-full max-w-md glass-panel p-8 rounded-2xl border border-slate-800 relative animate-fadeIn shadow-2xl">
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-500 hover:text-slate-300 transition-colors p-1"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center space-y-2 mb-6">
          <div className="w-12 h-12 bg-indigo-600/10 border border-indigo-500/20 rounded-xl flex items-center justify-center mx-auto text-indigo-400">
            {isSignUp ? <UserCheck className="w-6 h-6" /> : <Key className="w-6 h-6" />}
          </div>
          <h3 className="text-lg font-display font-bold text-white">
            {isSignUp ? "Create a NYAYA Account" : "Access Your Citizen Dashboard"}
          </h3>
          <p className="text-xs text-slate-400">
            {isSignUp 
              ? "Track, save, and claim your active civic action plans." 
              : "Sign in to access your saved cases and documents."}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-xs text-rose-400">
              {error}
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3.5 w-4 h-4 text-slate-500" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="citizen@nyaya.org"
                className="w-full pl-9 pr-4 py-3 bg-slate-900/60 border border-slate-800 rounded-xl text-sm text-slate-200 focus:border-indigo-500 focus:outline-none transition-colors"
                required
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3.5 w-4 h-4 text-slate-500" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••"
                className="w-full pl-9 pr-4 py-3 bg-slate-900/60 border border-slate-800 rounded-xl text-sm text-slate-200 focus:border-indigo-500 focus:outline-none transition-colors"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 mt-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white rounded-xl text-sm font-semibold transition-colors flex items-center justify-center gap-2"
          >
            {loading ? "Authenticating..." : (isSignUp ? "Sign Up" : "Log In")}
          </button>
        </form>

        <div className="text-center mt-6 pt-4 border-t border-slate-900 text-xs text-slate-400">
          {isSignUp ? "Already have an account?" : "Need a secure folder?"}{" "}
          <button
            onClick={() => {
              setIsSignUp(!isSignUp);
              setError(null);
            }}
            className="text-indigo-400 hover:text-indigo-300 font-semibold hover:underline"
          >
            {isSignUp ? "Log In here" : "Sign Up here"}
          </button>
        </div>
      </div>
    </div>
  );
};
