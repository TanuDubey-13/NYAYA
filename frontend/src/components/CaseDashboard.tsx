import React from 'react';
import { CaseDocument } from '../utils/api';
import { Shield, MapPin, Calendar, AlertTriangle } from 'lucide-react';

interface CaseDashboardProps {
  cases: CaseDocument[];
  onSelectCase: (c: CaseDocument) => void;
}

export const CaseDashboard: React.FC<CaseDashboardProps> = ({ cases, onSelectCase }) => {
  const getStatusBadgeClass = (status: string) => {
    switch (status.toUpperCase()) {
      case 'NEW':
      case 'TRIAGED':
        return 'bg-blue-500/10 text-blue-400 border border-blue-500/20';
      case 'NEEDS_INFORMATION':
        return 'bg-amber-500/10 text-amber-400 border border-amber-500/20';
      case 'RESEARCHING':
      case 'EVIDENCE_READY':
        return 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20';
      case 'ACTION_PLAN_READY':
      case 'DRAFT_READY':
      case 'READY_TO_SUBMIT':
        return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
      case 'SUBMITTED_BY_USER':
      case 'RESOLVED':
        return 'bg-slate-500/10 text-slate-400 border border-slate-500/20';
      default:
        return 'bg-slate-500/10 text-slate-400 border border-slate-500/20';
    }
  };

  const formatDate = (isoString: string) => {
    try {
      return new Date(isoString).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    } catch {
      return 'Unknown date';
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto mt-8 animate-fadeIn">
      <div className="flex items-center justify-between border-b border-slate-900 pb-4">
        <div>
          <h2 className="text-xl font-display font-bold text-white">Saved Actions & Cases</h2>
          <p className="text-xs text-slate-500 mt-1">Access your citizen folders and track their submission status.</p>
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 bg-slate-900 rounded-lg text-indigo-400 border border-slate-800">
          {cases.length} Folders
        </span>
      </div>

      {cases.length === 0 ? (
        <div className="glass-panel p-12 rounded-2xl border border-slate-850 text-center space-y-3">
          <Shield className="w-10 h-10 text-slate-700 mx-auto" />
          <p className="text-sm font-medium text-slate-400">No cases found in this profile.</p>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            You can create a new civic problem report on the homepage. If you have an active guest case, log in to claim and save it.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {cases.map((c) => (
            <div
              key={c.caseId}
              onClick={() => onSelectCase(c)}
              className="glass-panel p-5 rounded-2xl border border-slate-850 hover:border-indigo-500/40 cursor-pointer transition-all hover:translate-y-[-2px] flex flex-col justify-between gap-4"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${getStatusBadgeClass(c.status)}`}>
                    {c.status.replace(/_/g, ' ')}
                  </span>
                  {c.urgency === 'high' && (
                    <span className="flex items-center gap-1 text-[10px] text-rose-400 font-bold bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded-full">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      High Urgency
                    </span>
                  )}
                </div>

                <div>
                  <h4 className="text-sm font-bold text-slate-200 line-clamp-1 capitalize">
                    {c.subcategory ? c.subcategory.replace(/_/g, ' ') : c.category?.replace(/_/g, ' ')}
                  </h4>
                  <p className="text-xs text-slate-400 line-clamp-2 mt-1 italic">
                    "{c.initialProblem}"
                  </p>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-900/60 flex flex-wrap items-center justify-between text-[10px] text-slate-500 gap-2">
                <div className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-slate-500" />
                  <span className="truncate max-w-[120px]">
                    {c.jurisdiction ? `${c.jurisdiction.city}, ${c.jurisdiction.state}` : 'Unknown Location'}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-slate-500" />
                    <span>{formatDate(c.status === 'NEW' ? new Date().toISOString() : c.status)}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
