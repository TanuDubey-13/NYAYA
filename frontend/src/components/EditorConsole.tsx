import React, { useState, useEffect } from 'react';
import { Save, Download, FileText, AlertTriangle } from 'lucide-react';

interface EditorConsoleProps {
  initialContent: string;
  onSave: (content: string) => void;
  onExport: () => void;
}

export const EditorConsole: React.FC<EditorConsoleProps> = ({ initialContent, onSave, onExport }) => {
  const [content, setContent] = useState(initialContent);

  useEffect(() => {
    setContent(initialContent);
  }, [initialContent]);

  const handleSave = () => {
    onSave(content);
  };

  return (
    <div className="w-full max-w-3xl mx-auto mt-8 glass-panel rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
      {/* Console header */}
      <div className="flex items-center justify-between px-6 py-4 bg-slate-900/80 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-indigo-400" />
          <span className="text-sm font-semibold text-slate-200">Grievance Complaint Editor</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleSave}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-slate-800 hover:bg-slate-750 text-slate-300 hover:text-white text-xs font-semibold rounded-lg transition-colors border border-slate-700"
          >
            <Save className="w-3.5 h-3.5" />
            Save Changes
          </button>
          <button
            onClick={onExport}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition-colors shadow-md shadow-indigo-600/10"
          >
            <Download className="w-3.5 h-3.5" />
            Export Draft
          </button>
        </div>
      </div>

      {/* Editor Warning Banner */}
      <div className="bg-amber-500/5 border-b border-amber-500/10 px-6 py-3 flex items-start gap-2.5">
        <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
        <p className="text-[11px] text-amber-400/80 leading-relaxed font-sans">
          This is an AI-generated draft. Please review and replace all bracketed items (e.g. [ENTER NAME]) with your actual personal details before filing.
        </p>
      </div>

      {/* Text area editor */}
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        className="w-full h-80 bg-slate-950/40 p-6 text-slate-300 font-mono text-xs focus:outline-none resize-none leading-relaxed"
      />
    </div>
  );
};
