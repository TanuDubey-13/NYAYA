import { BookOpen, ExternalLink, ShieldCheck, AlertCircle, Landmark } from 'lucide-react';

export interface Claim {
  claim: string;
  sourceIds: string[];
  verificationStatus: string;
}

export interface Evidence {
  sourceId: string;
  title: string;
  authority: string;
  excerpt: string;
  officialUrl: string;
  jurisdiction: {
    country: string;
    state: string;
    city: string;
    localityOrWard?: string;
  };
  verificationStatus: string;
}

interface RightsPanelProps {
  understoodText: string;
  category: string;
  subcategory: string;
  urgency: string;
  jurisdiction: {
    country: string;
    state: string;
    city: string;
    localityOrWard: string;
    department?: string | null;
    authority?: string | null;
  } | null;
  claims: Claim[];
  evidenceList: Evidence[];
}

export const RightsPanel: React.FC<RightsPanelProps> = ({
  understoodText,
  category,
  subcategory,
  urgency,
  jurisdiction,
  claims,
  evidenceList
}) => {
  const getBadgeStyle = (status: string) => {
    switch (status.toUpperCase()) {
      case 'VERIFIED':
        return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
      case 'NEEDS_VERIFICATION':
        return 'bg-amber-500/10 text-amber-400 border border-amber-500/20';
      case 'NO_EVIDENCE':
      default:
        return 'bg-rose-500/10 text-rose-400 border border-rose-500/20';
    }
  };

  const getBadgeLabel = (status: string) => {
    switch (status.toUpperCase()) {
      case 'VERIFIED':
        return '🟢 Verified from source';
      case 'NEEDS_VERIFICATION':
        return '🟡 Needs verification';
      case 'NO_EVIDENCE':
      default:
        return '🔴 Unverified / No evidence';
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-7xl mx-auto mt-8">
      {/* Left Column: Understanding, Claims and Action details (col-span-2) */}
      <div className="lg:col-span-2 space-y-6">
        
        {/* Section 1: What NYAYA Understood */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <h3 className="text-base font-display font-semibold text-slate-100 flex items-center gap-2 mb-4">
            <BookOpen className="w-5 h-5 text-indigo-400" />
            What NYAYA Understood
          </h3>
          
          <div className="space-y-4">
            <p className="text-slate-300 text-sm leading-relaxed italic">
              "{understoodText || 'Awaiting input...'}"
            </p>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-slate-900">
              <div>
                <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">Category</span>
                <span className="text-xs font-semibold text-slate-300 capitalize">{category.replace('_', ' ')}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">Subcategory</span>
                <span className="text-xs font-semibold text-slate-300 capitalize">{subcategory.replace('_', ' ')}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">Urgency</span>
                <span className={`text-xs font-semibold capitalize ${urgency === 'high' ? 'text-rose-400' : 'text-slate-300'}`}>
                  {urgency}
                </span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">Location</span>
                <span className="text-xs font-semibold text-slate-300 truncate block">
                  {jurisdiction ? `${jurisdiction.city}, ${jurisdiction.state}` : 'Not provided'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Section 2: What Official Sources Indicate (Claims) */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-base font-display font-semibold text-slate-100 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            What Official Sources Indicate
          </h3>

          <div className="space-y-4 pt-2">
            {claims.length === 0 ? (
              <p className="text-xs text-slate-500">No legal claims formulated yet.</p>
            ) : (
              claims.map((c, i) => (
                <div key={i} className="p-4 rounded-xl bg-slate-900/40 border border-slate-900 space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${getBadgeStyle(c.verificationStatus)}`}>
                      {getBadgeLabel(c.verificationStatus)}
                    </span>
                    {c.sourceIds.length > 0 && (
                      <span className="text-[10px] font-mono text-slate-500">Source: {c.sourceIds.join(', ')}</span>
                    )}
                  </div>
                  <p className="text-sm text-slate-200 leading-relaxed font-medium">
                    {c.claim}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Section 3: Who to Approach */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <h3 className="text-base font-display font-semibold text-slate-100 flex items-center gap-2 mb-4">
            <Landmark className="w-5 h-5 text-indigo-400" />
            Who You Need to Approach
          </h3>
          
          {jurisdiction && jurisdiction.authority ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-900">
                <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">Target Authority</span>
                <span className="text-sm font-semibold text-slate-200 mt-1 block">{jurisdiction.authority}</span>
              </div>
              <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-900">
                <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">Department Name</span>
                <span className="text-sm font-semibold text-slate-200 mt-1 block">{jurisdiction.department || 'General Administration'}</span>
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-rose-500/5 border border-rose-500/10 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
              <p className="text-xs text-rose-300 leading-relaxed">
                Authority could not be verified from the available authoritative sources. 
                Please ensure you have confirmed your local jurisdiction correctly.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Right Column: Evidence & Citations */}
      <div className="space-y-4">
        <h4 className="font-display font-semibold text-slate-200 text-sm tracking-wider uppercase px-1">Evidence & Citations</h4>
        
        {evidenceList.length === 0 ? (
          <div className="glass-panel p-6 rounded-2xl border border-slate-850 text-center space-y-3">
            <AlertCircle className="w-8 h-8 text-rose-500/40 mx-auto" />
            <p className="text-xs text-slate-400">
              I could not verify this information from an authoritative source.
            </p>
          </div>
        ) : (
          evidenceList.map((ev) => (
            <div key={ev.sourceId} className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col gap-3">
              <div className="flex justify-between items-start gap-2">
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${getBadgeStyle(ev.verificationStatus)}`}>
                  {ev.verificationStatus === 'VERIFIED' ? '🟢 Verified' : '🟡 Needs Verification'}
                </span>
                <span className="text-[10px] text-slate-500 font-mono">{ev.sourceId}</span>
              </div>
              
              <div>
                <h5 className="text-xs font-semibold text-slate-200 line-clamp-2">{ev.title}</h5>
                <span className="text-[10px] text-indigo-400 font-medium block mt-0.5">{ev.authority}</span>
                <span className="text-[9px] text-slate-500 block">Jurisdiction: {ev.jurisdiction.city}, {ev.jurisdiction.state}</span>
              </div>
              
              <p className="text-xs text-slate-400 bg-slate-900/40 p-3 rounded-lg border border-slate-850 italic line-clamp-4 leading-relaxed">
                "{ev.excerpt}"
              </p>
              
              <a
                href={ev.officialUrl}
                target="_blank"
                rel="noreferrer"
                className="flex items-center justify-between text-[11px] text-indigo-400 hover:text-indigo-300 font-medium transition-colors pt-1 border-t border-slate-900"
              >
                <span>Official source portal</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
