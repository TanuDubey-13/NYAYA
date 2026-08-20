import React from 'react';

interface TimelineTrackerProps {
  currentStatus: string;
}

const STATES_IN_ORDER = [
  { label: 'Intake', value: 'NEW' },
  { label: 'Triage', value: 'TRIAGED' },
  { label: 'Details', value: 'NEEDS_INFORMATION' },
  { label: 'RAG Search', value: 'RESEARCHING' },
  { label: 'Evidence', value: 'EVIDENCE_READY' },
  { label: 'Action Plan', value: 'ACTION_PLAN_READY' },
  { label: 'Drafting', value: 'DRAFT_READY' },
  { label: 'Ready', value: 'READY_TO_SUBMIT' },
  { label: 'Submitted', value: 'SUBMITTED_BY_USER' }
];

export const TimelineTracker: React.FC<TimelineTrackerProps> = ({ currentStatus }) => {
  // Find current index
  const currentIndex = STATES_IN_ORDER.findIndex(state => state.value === currentStatus);

  return (
    <div className="w-full max-w-5xl mx-auto py-6 mb-8 overflow-x-auto">
      <div className="flex items-center justify-between min-w-[700px] px-4">
        {STATES_IN_ORDER.map((state, index) => {
          const isCompleted = index < currentIndex;
          const isActive = index === currentIndex;
          
          return (
            <React.Fragment key={state.value}>
              {/* Node */}
              <div className="flex flex-col items-center relative z-10">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-mono font-bold transition-all border ${
                  isActive 
                    ? 'bg-indigo-600 border-indigo-400 text-white shadow-lg shadow-indigo-500/20 scale-110' 
                    : isCompleted
                      ? 'bg-slate-800 border-indigo-500/40 text-indigo-400'
                      : 'bg-slate-900 border-slate-800 text-slate-500'
                }`}>
                  {index + 1}
                </div>
                <span className={`text-[10px] font-semibold mt-2 tracking-wide uppercase transition-colors ${
                  isActive 
                    ? 'text-indigo-400' 
                    : isCompleted
                      ? 'text-slate-300'
                      : 'text-slate-500'
                }`}>
                  {state.label}
                </span>
              </div>
              
              {/* Connector Line */}
              {index < STATES_IN_ORDER.length - 1 && (
                <div className="flex-1 h-[2px] mx-2 -mt-6 relative bg-slate-850">
                  <div 
                    className="absolute inset-0 bg-indigo-500 transition-all duration-300"
                    style={{ width: isCompleted ? '100%' : isActive ? '50%' : '0%' }}
                  />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
