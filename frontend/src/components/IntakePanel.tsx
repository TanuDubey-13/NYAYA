import React, { useState } from 'react';
import { Sparkles, MessageSquare } from 'lucide-react';

interface IntakePanelProps {
  onSubmit: (text: string) => void;
  isLoading: boolean;
}

export const IntakePanel: React.FC<IntakePanelProps> = ({ onSubmit, isLoading }) => {
  const [text, setText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSubmit(text);
  };

  return (
    <div className="w-full max-w-3xl mx-auto glass-panel p-8 rounded-2xl border border-slate-800 shadow-xl">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl">
          <MessageSquare className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-xl font-display font-semibold text-slate-100">Describe your civic or legal problem</h2>
          <p className="text-sm text-slate-400">Provide details like garbage accumulation, RTI issues, or municipal complaints.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Example: My area has not had garbage collection for two weeks and it smells terrible..."
          className="w-full h-40 bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all font-sans resize-none"
          disabled={isLoading}
        />
        
        <div className="flex justify-between items-center">
          <span className="text-xs text-slate-500">NYAYA uses verified local sources to construct action paths.</span>
          <button
            type="submit"
            disabled={isLoading || !text.trim()}
            className="flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-500 text-white rounded-xl font-medium shadow-lg hover:shadow-indigo-500/10 transition-all"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-indigo-200 border-t-transparent rounded-full animate-spin"></span>
                Processing...
              </span>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Analyze Problem
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
