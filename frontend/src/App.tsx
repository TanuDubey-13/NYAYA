import React, { useState } from 'react';
import { Scale, ArrowRight, UserPlus, Info } from 'lucide-react';
import { IntakePanel } from './components/IntakePanel';
import { RightsPanel } from './components/RightsPanel';
import { ActionSteps } from './components/ActionSteps';
import { EditorConsole } from './components/EditorConsole';
import { TimelineTracker } from './components/TimelineTracker';
import { LanguageToggle } from './components/LanguageToggle';
import { submitIntake, checkBackendHealth, CaseDocument } from './utils/api';

export default function App() {
  const [lang, setLang] = useState<'en' | 'hi'>('en');
  const [showDemo, setShowDemo] = useState(false);
  const [loading, setLoading] = useState(false);
  const [backendHealth, setBackendHealth] = useState<string | null>(null);
  
  // Case Session states
  const [activeCase, setActiveCase] = useState<CaseDocument | null>(null);
  const [locality, setLocality] = useState('');
  
  // Check backend health on landing
  React.useEffect(() => {
    checkBackendHealth()
      .then(res => setBackendHealth(`${res.service} is running (Status: ${res.status})`))
      .catch(() => setBackendHealth('Backend offline / not started'));
  }, []);

  const handleStartDemo = () => {
    setShowDemo(true);
  };

  const handleIntakeSubmit = async (problemText: string) => {
    setLoading(true);
    try {
      // Phase 1 API Call: Intake Triager
      const sessionCase = await submitIntake(problemText, "guest-session-123");
      setActiveCase(sessionCase);
    } catch (e) {
      console.error(e);
      alert("Backend connection error. Make sure the backend server is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleClarifySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!locality.trim() || !activeCase) return;
    setLoading(true);
    
    try {
      // Phase 1 API Call: Clarify Locality
      const response = await fetch(`http://localhost:8000/api/v1/cases/${activeCase.caseId}/respond?question_id=q_locality&answer=${encodeURIComponent(locality)}`, {
        method: 'POST'
      });
      if (!response.ok) throw new Error("Failed to clarify locality");
      const updatedCase = await response.json();
      setActiveCase(updatedCase);
      
      // Auto-trigger RAG research analysis
      await handleRunAnalysis(updatedCase.caseId);
    } catch (e) {
      console.error(e);
      alert("Error submitting details");
    } finally {
      setLoading(false);
    }
  };

  const handleRunAnalysis = async (caseId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/cases/${caseId}/analyze`, { method: 'POST' });
      if (!response.ok) throw new Error("Failed to analyze claims");
      const updatedCase = await response.json();
      setActiveCase(updatedCase);

      // Trigger Action plan creation
      const planResponse = await fetch(`http://localhost:8000/api/v1/cases/${caseId}/action-plan`, { method: 'POST' });
      const caseWithPlan = await planResponse.json();
      setActiveCase(caseWithPlan);

      // Trigger Draft letter generation
      const draftResponse = await fetch(`http://localhost:8000/api/v1/cases/${caseId}/draft`, { method: 'POST' });
      const caseWithDraft = await draftResponse.json();
      setActiveCase(caseWithDraft);
    } catch (e) {
      console.error(e);
    }
  };

  const handleToggleStep = async (stepNumber: number) => {
    if (!activeCase) return;
    const updatedSteps = activeCase.actionPlan.map(s => 
      s.stepNumber === stepNumber ? { ...s, completed: !s.completed } : s
    );
    setActiveCase({
      ...activeCase,
      actionPlan: updatedSteps
    });
  };

  const handleSaveDraft = async (newContent: string) => {
    if (!activeCase) return;
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/cases/${activeCase.caseId}/draft?content=${encodeURIComponent(newContent)}`, {
        method: 'PUT'
      });
      if (!response.ok) throw new Error("Failed to save draft");
      const updatedCase = await response.json();
      setActiveCase(updatedCase);
    } catch (e) {
      console.error(e);
      alert("Error saving draft modifications");
    } finally {
      setLoading(false);
    }
  };

  const handleExportDraft = () => {
    if (!activeCase || !activeCase.draftDocument) return;
    
    // Create text file download trigger
    const element = document.createElement("a");
    const file = new Blob([activeCase.draftDocument.content], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `${activeCase.draftDocument.title.toLowerCase().replace(/\s+/g, '_')}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handleSubmitStatus = async () => {
    if (!activeCase) return;
    try {
      const response = await fetch(`http://localhost:8000/api/v1/cases/${activeCase.caseId}/submit-status`, { method: 'POST' });
      if (!response.ok) throw new Error("Failed to update status");
      const updatedCase = await response.json();
      setActiveCase(updatedCase);
    } catch (e) {
      console.error(e);
    }
  };

  const handleRegisterMock = async () => {
    if (!activeCase) return;
    try {
      const response = await fetch(`http://localhost:8000/api/v1/cases/${activeCase.caseId}/claim`, { 
        method: 'POST',
        headers: { 'Authorization': 'Bearer mock-user-token' }
      });
      if (!response.ok) throw new Error("Failed to register and link case");
      const updatedCase = await response.json();
      setActiveCase(updatedCase);
      alert("Account registration successful! Your case history has been permanently mapped to user-uid.");
    } catch (e) {
      console.error(e);
    }
  };

  const handleReset = () => {
    setActiveCase(null);
    setLocality('');
    setShowDemo(false);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950">
      {/* Header bar */}
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 cursor-pointer" onClick={handleReset}>
            <Scale className="w-6 h-6 text-indigo-500" />
            <span className="font-display font-bold text-lg tracking-wide text-slate-100">NYAYA</span>
          </div>

          <div className="flex items-center gap-4">
            {backendHealth && (
              <span className={`text-[10px] px-2 py-0.5 rounded-full ${
                backendHealth.includes('offline') ? 'bg-rose-500/10 text-rose-400' : 'bg-emerald-500/10 text-emerald-400'
              }`}>
                {backendHealth}
              </span>
            )}
            <LanguageToggle currentLanguage={lang} onToggle={setLang} />
          </div>
        </div>
      </header>

      {/* Main body */}
      <main className="flex-1 flex flex-col justify-center py-12 px-6">
        {!showDemo ? (
          /* Landing Screen */
          <div className="max-w-4xl mx-auto text-center space-y-8">
            <div className="space-y-4">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-indigo-500/10 text-indigo-400 rounded-full text-xs font-semibold uppercase tracking-wider">
                ⚖️ AI Civic & Legal Action Navigator
              </span>
              <h1 className="text-4xl md:text-6xl font-display font-extrabold tracking-tight text-white leading-tight">
                Turn your civic problem into a <br />
                <span className="text-gradient">verified action plan.</span>
              </h1>
              <p className="text-slate-400 text-lg max-w-2xl mx-auto leading-relaxed">
                Describe your issue in plain language. NYAYA identifies relevant regulations, 
                retrieves citations from official portals, outlines action plans, and structures drafts.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <button
                onClick={handleStartDemo}
                className="glow-btn flex items-center gap-2 px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold shadow-lg shadow-indigo-600/20 transition-all w-full sm:w-auto justify-center"
              >
                Try NYAYA
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>

            <div className="border-t border-slate-900 pt-8 max-w-lg mx-auto">
              <p className="text-xs text-slate-500 uppercase tracking-widest font-semibold mb-4">Core Principles</p>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <span className="text-xs font-semibold text-slate-300 block">Evidence-Backed</span>
                  <span className="text-[10px] text-slate-500 mt-1 block">Sources from official codes</span>
                </div>
                <div>
                  <span className="text-xs font-semibold text-slate-300 block">Personalized Tasks</span>
                  <span className="text-[10px] text-slate-500 mt-1 block">Contextual next-steps</span>
                </div>
                <div>
                  <span className="text-xs font-semibold text-slate-300 block">Document Drafting</span>
                  <span className="text-[10px] text-slate-500 mt-1 block">Filing applications directly</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Active Case Workspace */
          <div className="space-y-8 max-w-6xl mx-auto w-full">
            {activeCase && <TimelineTracker currentStatus={activeCase.status} />}

            {/* Step 1: Intake Form */}
            {!activeCase && (
              <IntakePanel onSubmit={handleIntakeSubmit} isLoading={loading} />
            )}

            {/* Step 2: Clarification prompt (Triage results in NEEDS_INFORMATION / RESEARCHING status) */}
            {activeCase && activeCase.status === 'TRIAGED' && (
              <div className="w-full max-w-2xl mx-auto glass-panel p-8 rounded-2xl border border-slate-800 shadow-xl space-y-6">
                <div className="flex items-start gap-3">
                  <div className="p-2.5 bg-amber-500/10 text-amber-500 rounded-xl mt-1">
                    <Info className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-slate-100">Jurisdiction Clarification</h3>
                    <p className="text-xs text-slate-400 mt-0.5">Please confirm your locality parameters to query local rules.</p>
                  </div>
                </div>

                <form onSubmit={handleClarifySubmit} className="space-y-4">
                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-slate-400">Ward Number or Locality Name</label>
                    <input
                      type="text"
                      value={locality}
                      onChange={(e) => setLocality(e.target.value)}
                      placeholder="e.g. Ward 150, HSR Layout, Bengaluru"
                      className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500/50 text-slate-200"
                      disabled={loading}
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={loading || !locality.trim()}
                    className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white rounded-xl text-sm font-semibold transition-colors"
                  >
                    Submit Details
                  </button>
                </form>
              </div>
            )}

            {/* Step 3: Rights Navigator & Citations */}
            {activeCase && activeCase.status !== 'TRIAGED' && (
              <div className="space-y-8 animate-fadeIn">
                <div className="border-b border-slate-900 pb-4">
                  <h2 className="text-2xl font-display font-bold text-white">NYAYA Navigator Panel</h2>
                  <p className="text-xs text-slate-400 mt-1">Review verified civic parameters and custom actions generated for you.</p>
                </div>

                <RightsPanel 
                  understoodText={activeCase.initialProblem} 
                  category={activeCase.category || ""}
                  subcategory={activeCase.subcategory || ""}
                  urgency={activeCase.urgency || "normal"}
                  jurisdiction={activeCase.jurisdiction || null}
                  claims={activeCase.claims || []}
                  evidenceList={activeCase.evidence.map(e => ({
                    sourceId: e.sourceId,
                    title: e.title,
                    authority: e.authority,
                    excerpt: e.excerpt,
                    officialUrl: e.officialUrl,
                    jurisdiction: e.jurisdiction,
                    verificationStatus: activeCase.claims.find(c => c.sourceIds.includes(e.sourceId))?.verificationStatus || 'NEEDS_VERIFICATION'
                  }))} 
                />

                {activeCase.actionPlan.length > 0 && (
                  <ActionSteps steps={activeCase.actionPlan} onToggleStep={handleToggleStep} />
                )}

                {activeCase.draftDocument && (
                  <EditorConsole 
                    initialContent={activeCase.draftDocument.content} 
                    onSave={handleSaveDraft} 
                    onExport={handleExportDraft} 
                  />
                )}

                {/* Submissions & Auth Mapping CTA card */}
                <div className="w-full max-w-3xl mx-auto glass-panel p-8 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-6">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-200">Prepared by NYAYA • Action Plan Ready</h3>
                    <p className="text-xs text-slate-500 mt-1">
                      {activeCase.status === 'READY_TO_SUBMIT' 
                        ? 'Draft modified. You can file this draft on the official grievance portal.' 
                        : activeCase.status === 'SUBMITTED_BY_USER'
                          ? 'Complaint lodged manually by the citizen.'
                          : 'Verify details, download, and file through target channels.'
                      }
                    </p>
                  </div>
                  <div className="flex gap-3">
                    {activeCase.status === 'READY_TO_SUBMIT' && (
                      <button
                        onClick={handleSubmitStatus}
                        className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl transition-all shadow-lg shadow-emerald-600/10"
                      >
                        I Filed This Complaint
                      </button>
                    )}
                    {activeCase.userId === null && (
                      <button
                        onClick={handleRegisterMock}
                        className="flex items-center gap-1.5 px-5 py-2.5 bg-slate-850 hover:bg-slate-800 text-indigo-400 hover:text-indigo-300 text-xs font-semibold rounded-xl border border-slate-800 transition-all"
                      >
                        <UserPlus className="w-4 h-4" />
                        Save to Account
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer bar */}
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500 bg-slate-950">
        <p className="max-w-2xl mx-auto px-6">
          NYAYA provides informational and procedural guidance based on available sources. 
          It does not replace a qualified legal professional or an official government decision.
        </p>
      </footer>
    </div>
  );
}
