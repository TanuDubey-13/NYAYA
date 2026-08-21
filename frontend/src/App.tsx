import React, { useState } from 'react';
import { Scale, ArrowRight, UserPlus, Info } from 'lucide-react';
import { IntakePanel } from './components/IntakePanel';
import { RightsPanel } from './components/RightsPanel';
import { ActionSteps } from './components/ActionSteps';
import { EditorConsole } from './components/EditorConsole';
import { TimelineTracker } from './components/TimelineTracker';
import { LanguageToggle } from './components/LanguageToggle';
import { AuthModal } from './components/AuthModal';
import { CaseDashboard } from './components/CaseDashboard';
import { onAuthStateChanged, logout, getIdToken, User } from './utils/firebase';
import { translations } from './utils/translations';
import { 
  submitIntake, 
  respondCase, 
  analyzeCase, 
  createActionPlan, 
  generateDraftDocument, 
  updateDraftDocument, 
  submitStatus, 
  claimCase, 
  fetchCases,
  setAuthToken,
  setGuestSessionId,
  getOrCreateGuestSessionId,
  CaseDocument
} from './utils/api';

export default function App() {
  const [lang, setLang] = useState<'en' | 'hi'>('en');
  const [loading, setLoading] = useState(false);
  
  // Auth & View states
  const [user, setUser] = useState<User | null>(null);
  const [cases, setCases] = useState<CaseDocument[]>([]);
  const [view, setView] = useState<'landing' | 'dashboard' | 'workspace'>('landing');
  const [authModalOpen, setAuthModalOpen] = useState(false);
  
  // Case Session states
  const [activeCase, setActiveCase] = useState<CaseDocument | null>(null);
  const [locality, setLocality] = useState('');

  // Translation helper
  const t = (key: keyof typeof translations['en']) => translations[lang][key] || key;

  // 1. Initial Guest Session and Auth State Observer
  React.useEffect(() => {
    const guestId = getOrCreateGuestSessionId();
    setGuestSessionId(guestId);

    const unsubscribe = onAuthStateChanged(async (fbUser) => {
      setUser(fbUser);
      if (fbUser) {
        const token = await getIdToken();
        setAuthToken(token);
        try {
          const list = await fetchCases();
          setCases(list);
        } catch (e) {
          console.error("Error fetching user cases:", e);
        }
      } else {
        setAuthToken(null);
        try {
          const list = await fetchCases();
          setCases(list);
        } catch (e) {
          console.error("Error fetching guest cases:", e);
        }
      }
    });

    return () => unsubscribe();
  }, []);

  const handleAuthSuccess = async () => {
    const token = await getIdToken();
    setAuthToken(token);
    
    // Automatically claim active guest case if present
    if (activeCase && activeCase.userId === null) {
      try {
        setLoading(true);
        const claimed = await claimCase(activeCase.caseId);
        setActiveCase(claimed);
        alert("Success! This case has been claimed and saved to your account.");
      } catch (e) {
        console.error("Error claiming guest case:", e);
      } finally {
        setLoading(false);
      }
    }
    
    try {
      const list = await fetchCases();
      setCases(list);
      
      if (activeCase) {
        setView('workspace');
      } else {
        setView(list.length > 0 ? 'dashboard' : 'workspace');
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleIntakeSubmit = async (problemText: string) => {
    setLoading(true);
    try {
      const sessionCase = await submitIntake(problemText);
      setActiveCase(sessionCase);
      setView('workspace');
    } catch (e) {
      console.error(e);
      alert("Intake submission failed. Check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  const handleClarifySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!locality.trim() || !activeCase) return;
    setLoading(true);
    
    try {
      const updatedCase = await respondCase(activeCase.caseId, 'q_locality', locality);
      setActiveCase(updatedCase);
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
      const updatedCase = await analyzeCase(caseId);
      setActiveCase(updatedCase);

      const caseWithPlan = await createActionPlan(caseId);
      setActiveCase(caseWithPlan);

      const caseWithDraft = await generateDraftDocument(caseId);
      setActiveCase(caseWithDraft);

      // Refresh list
      const list = await fetchCases();
      setCases(list);
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
      const updatedCase = await updateDraftDocument(activeCase.caseId, newContent);
      setActiveCase(updatedCase);
      
      const list = await fetchCases();
      setCases(list);
    } catch (e) {
      console.error(e);
      alert("Error saving draft modifications");
    } finally {
      setLoading(false);
    }
  };

  const handleExportDraft = () => {
    if (!activeCase || !activeCase.draftDocument) return;
    
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
      const updatedCase = await submitStatus(activeCase.caseId);
      setActiveCase(updatedCase);
      
      const list = await fetchCases();
      setCases(list);
    } catch (e) {
      console.error(e);
    }
  };

  const handleRegisterMock = () => {
    setAuthModalOpen(true);
  };

  const handleReset = () => {
    setActiveCase(null);
    setLocality('');
    if (user || cases.length > 0) {
      setView('dashboard');
    } else {
      setView('landing');
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      {/* Header bar */}
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 cursor-pointer" onClick={handleReset}>
            <Scale className="w-6 h-6 text-indigo-500" />
            <span className="font-display font-bold text-lg tracking-wide text-slate-100">NYAYA</span>
          </div>

          <div className="flex items-center gap-4">
            {user ? (
              <div className="flex items-center gap-3 text-xs">
                <span className="text-slate-400 hidden sm:inline">{user.email}</span>
                <button
                  onClick={() => { setActiveCase(null); setView('dashboard'); }}
                  className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-lg border border-slate-800 transition-colors"
                >
                  {t('dashboard')}
                </button>
                <button
                  onClick={() => { setActiveCase(null); setView('workspace'); }}
                  className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors font-semibold"
                >
                  {t('newCase')}
                </button>
                <button
                  onClick={async () => { await logout(); handleReset(); }}
                  className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-rose-400 rounded-lg border border-slate-800 transition-colors"
                >
                  {t('logout')}
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3 text-xs">
                {cases.length > 0 && (
                  <button
                    onClick={() => { setActiveCase(null); setView('dashboard'); }}
                    className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-lg border border-slate-800 transition-colors"
                  >
                    {t('myGuestCases')} ({cases.length})
                  </button>
                )}
                <button
                  onClick={() => setAuthModalOpen(true)}
                  className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors font-semibold"
                >
                  {t('signIn')}
                </button>
              </div>
            )}
            <LanguageToggle currentLanguage={lang} onToggle={setLang} />
          </div>
        </div>
      </header>

      {/* Main body */}
      <main className="flex-1 flex flex-col justify-center py-12 px-6">
        {view === 'landing' && (
          /* Landing Screen */
          <div className="max-w-4xl mx-auto text-center space-y-8 animate-fadeIn">
            <div className="space-y-4">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-indigo-500/10 text-indigo-400 rounded-full text-xs font-semibold uppercase tracking-wider">
                ⚖️ {t('tagline')}
              </span>
              <h1 className="text-4xl md:text-6xl font-display font-extrabold tracking-tight text-white leading-tight">
                {t('heroTitle')} <br />
                <span className="text-gradient">{t('heroHighlight')}</span>
              </h1>
              <p className="text-slate-400 text-lg max-w-2xl mx-auto leading-relaxed">
                {t('heroDesc')}
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <button
                onClick={() => setView('workspace')}
                className="glow-btn flex items-center gap-2 px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold shadow-lg shadow-indigo-600/20 transition-all w-full sm:w-auto justify-center"
              >
                {t('tryNyaya')}
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>

            <div className="border-t border-slate-900 pt-8 max-w-lg mx-auto">
              <p className="text-xs text-slate-500 uppercase tracking-widest font-semibold mb-4">{t('corePrinciples')}</p>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <span className="text-xs font-semibold text-slate-300 block">{t('evidenceBacked')}</span>
                  <span className="text-[10px] text-slate-500 mt-1 block">{t('evidenceDesc')}</span>
                </div>
                <div>
                  <span className="text-xs font-semibold text-slate-300 block">{t('personalizedTasks')}</span>
                  <span className="text-[10px] text-slate-500 mt-1 block">{t('tasksDesc')}</span>
                </div>
                <div>
                  <span className="text-xs font-semibold text-slate-300 block">{t('docDrafting')}</span>
                  <span className="text-[10px] text-slate-500 mt-1 block">{t('draftingDesc')}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {view === 'dashboard' && (
          <CaseDashboard 
            cases={cases} 
            onSelectCase={(c) => {
              setActiveCase(c);
              setView('workspace');
            }} 
          />
        )}

        {view === 'workspace' && (
          /* Active Case Workspace */
          <div className="space-y-8 max-w-6xl mx-auto w-full">
            {activeCase && <TimelineTracker currentStatus={activeCase.status} />}

            {/* Step 1: Intake Form */}
            {!activeCase && (
              <IntakePanel onSubmit={handleIntakeSubmit} isLoading={loading} lang={lang} />
            )}

            {/* Step 2: Clarification prompt */}
            {activeCase && activeCase.status === 'TRIAGED' && (
              <div className="w-full max-w-2xl mx-auto glass-panel p-8 rounded-2xl border border-slate-800 shadow-xl space-y-6">
                <div className="flex items-start gap-3">
                  <div className="p-2.5 bg-amber-500/10 text-amber-500 rounded-xl mt-1">
                    <Info className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-slate-100">{t('jurisdictionClarification')}</h3>
                    <p className="text-xs text-slate-400 mt-0.5">{t('confirmLocality')}</p>
                  </div>
                </div>

                <form onSubmit={handleClarifySubmit} className="space-y-4">
                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-slate-400">{t('wardOrLocality')}</label>
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
                    {t('submitDetails')}
                  </button>
                </form>
              </div>
            )}

            {/* Step 3: Rights Navigator & Citations */}
            {activeCase && activeCase.status !== 'TRIAGED' && (
              <div className="space-y-8 animate-fadeIn">
                <div className="border-b border-slate-900 pb-4">
                  <h2 className="text-2xl font-display font-bold text-white">{t('navigatorPanel')}</h2>
                  <p className="text-xs text-slate-400 mt-1">{t('navigatorDesc')}</p>
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
                    <h3 className="text-sm font-semibold text-slate-200">{t('actionPlanReady')}</h3>
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
                        {t('filedComplaint')}
                      </button>
                    )}
                    {activeCase.userId === null && (
                      <button
                        onClick={handleRegisterMock}
                        className="flex items-center gap-1.5 px-5 py-2.5 bg-slate-850 hover:bg-slate-800 text-indigo-400 hover:text-indigo-300 text-xs font-semibold rounded-xl border border-slate-800 transition-all"
                      >
                        <UserPlus className="w-4 h-4" />
                        {t('saveToAccount')}
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
          {t('footerNotice')}
        </p>
      </footer>

      {/* Authentication Modal */}
      <AuthModal 
        isOpen={authModalOpen} 
        onClose={() => setAuthModalOpen(false)} 
        onSuccess={handleAuthSuccess} 
      />
    </div>
  );
}
