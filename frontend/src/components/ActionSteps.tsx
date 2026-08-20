import React from 'react';
import { CheckCircle2, Circle } from 'lucide-react';

interface Step {
  stepNumber: number;
  action: string;
  whyItMatters: string;
  requiredEvidence: string[];
  authority: string;
  completed: boolean;
}

interface ActionStepsProps {
  steps: Step[];
  onToggleStep: (stepNumber: number) => void;
}

export const ActionSteps: React.FC<ActionStepsProps> = ({ steps, onToggleStep }) => {
  return (
    <div className="w-full max-w-3xl mx-auto mt-8 glass-panel p-8 rounded-2xl border border-slate-800">
      <h3 className="text-lg font-display font-semibold text-slate-100 mb-6">Your Personalized Action Plan</h3>

      {steps.length === 0 ? (
        <p className="text-sm text-slate-500 text-center py-4">No steps generated yet. Describe your problem first.</p>
      ) : (
        <div className="relative border-l border-slate-800 pl-6 ml-3 space-y-8">
          {steps.map((step) => (
            <div key={step.stepNumber} className="relative group">
              {/* Timeline marker */}
              <button
                onClick={() => onToggleStep(step.stepNumber)}
                className="absolute -left-[37px] top-1 bg-slate-950 rounded-full transition-all focus:outline-none"
              >
                {step.completed ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-500 fill-emerald-500/10" />
                ) : (
                  <Circle className="w-5 h-5 text-slate-600 group-hover:text-indigo-400" />
                )}
              </button>

              <div className={`p-4 rounded-xl border transition-all ${
                step.completed 
                  ? 'bg-slate-900/20 border-slate-900 text-slate-500' 
                  : 'bg-slate-900/60 border-slate-800 text-slate-200'
              }`}>
                <div className="flex items-center justify-between mb-1">
                  <h4 className={`text-sm font-semibold ${step.completed ? 'line-through text-slate-500' : 'text-slate-200'}`}>
                    Step {step.stepNumber}: {step.action}
                  </h4>
                  <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded-md font-mono">
                    {step.authority}
                  </span>
                </div>
                
                <p className="text-xs text-slate-400 mt-1">{step.whyItMatters}</p>

                {step.requiredEvidence.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2 items-center">
                    <span className="text-[10px] text-slate-500 font-semibold uppercase">Requires:</span>
                    {step.requiredEvidence.map((ev, index) => (
                      <span key={index} className="text-[10px] bg-indigo-500/5 text-indigo-400/80 px-2 py-0.5 rounded border border-indigo-500/10">
                        {ev}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
