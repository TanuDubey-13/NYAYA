import React from 'react';
import { Globe } from 'lucide-react';

interface LanguageToggleProps {
  currentLanguage: 'en' | 'hi';
  onToggle: (lang: 'en' | 'hi') => void;
}

export const LanguageToggle: React.FC<LanguageToggleProps> = ({ currentLanguage, onToggle }) => {
  return (
    <div className="flex items-center gap-1.5 p-1 bg-slate-900 border border-slate-800 rounded-xl">
      <div className="p-1 text-slate-500">
        <Globe className="w-4 h-4" />
      </div>
      <button
        onClick={() => onToggle('en')}
        className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
          currentLanguage === 'en' 
            ? 'bg-slate-800 text-indigo-400 font-bold border border-slate-700' 
            : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        English
      </button>
      <button
        onClick={() => onToggle('hi')}
        className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
          currentLanguage === 'hi' 
            ? 'bg-slate-800 text-indigo-400 font-bold border border-slate-700' 
            : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        हिन्दी
      </button>
    </div>
  );
};
