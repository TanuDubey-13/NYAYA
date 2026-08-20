// Centralized Typed API Client for NYAYA Backend

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface HealthResponse {
  status: string;
  service: string;
}

export interface CaseDocument {
  caseId: string;
  userId: string | null;
  guestSessionId: string | null;
  status: string;
  initialProblem: string;
  category?: string;
  subcategory?: string;
  urgency: string;
  jurisdiction?: {
    country: string;
    state: string;
    city: string;
    localityOrWard: string;
    department?: string | null;
    authority?: string | null;
  };
  conversationHistory: Array<{ role: string; content: string; timestamp: string }>;
  claims: Array<{ claim: string; sourceIds: string[]; verificationStatus: string }>;
  evidence: Array<{
    sourceId: string;
    title: string;
    authority: string;
    excerpt: string;
    officialUrl: string;
    jurisdiction: { country: string; state: string; city: string; localityOrWard?: string };
  }>;
  actionPlan: Array<{
    stepNumber: number;
    action: string;
    whyItMatters: string;
    requiredEvidence: string[];
    authority: string;
    sourceIds: string[];
    completed: boolean;
  }>;
  draftDocument: {
    docType: string;
    title: string;
    content: string;
    updatedAt: string;
  } | null;
}

// Active connection tokens
let activeAuthToken: string | null = null;
let activeGuestSessionId: string | null = null;

export function setAuthToken(token: string | null) {
  activeAuthToken = token;
}

export function setGuestSessionId(sessionId: string | null) {
  activeGuestSessionId = sessionId;
}

export function getOrCreateGuestSessionId(): string {
  let gid = localStorage.getItem('nyaya_guest_session_id');
  if (!gid) {
    gid = 'guest_' + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('nyaya_guest_session_id', gid);
  }
  return gid;
}

async function apiRequest(
  path: string, 
  method: string = 'GET', 
  body: any = null,
  searchParams: Record<string, string> = {}
) {
  const url = new URL(`${API_BASE}${path}`);
  Object.entries(searchParams).forEach(([k, v]) => {
    url.searchParams.append(k, v);
  });
  
  const headers: Record<string, string> = {};
  if (body) {
    headers['Content-Type'] = 'application/json';
  }
  if (activeGuestSessionId) {
    headers['guest-session-id'] = activeGuestSessionId;
  }
  if (activeAuthToken) {
    headers['Authorization'] = `Bearer ${activeAuthToken}`;
  }
  
  const response = await fetch(url.toString(), {
    method,
    headers,
    body: body ? JSON.stringify(body) : null
  });
  
  if (response.status === 401) {
    setAuthToken(null);
    throw new Error("Session expired or unauthorized. Please log in again.");
  }
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `API error: ${response.statusText}`);
  }
  
  return response.json();
}

export async function checkBackendHealth(): Promise<HealthResponse> {
  return apiRequest('/health');
}

export async function fetchCases(): Promise<CaseDocument[]> {
  return apiRequest('/api/v1/cases');
}

export async function getCase(caseId: string): Promise<CaseDocument> {
  return apiRequest(`/api/v1/cases/${caseId}`);
}

export async function submitIntake(problemText: string): Promise<CaseDocument> {
  return apiRequest('/api/v1/cases/triage', 'POST', null, { problem_text: problemText });
}

export async function respondCase(caseId: string, questionId: string, answer: string): Promise<CaseDocument> {
  return apiRequest(`/api/v1/cases/${caseId}/respond`, 'POST', null, { question_id: questionId, answer });
}

export async function analyzeCase(caseId: string): Promise<CaseDocument> {
  return apiRequest(`/api/v1/cases/${caseId}/analyze`, 'POST');
}

export async function createActionPlan(caseId: string): Promise<CaseDocument> {
  return apiRequest(`/api/v1/cases/${caseId}/action-plan`, 'POST');
}

export async function generateDraftDocument(caseId: string): Promise<CaseDocument> {
  return apiRequest(`/api/v1/cases/${caseId}/draft`, 'POST');
}

export async function updateDraftDocument(caseId: string, content: string): Promise<CaseDocument> {
  return apiRequest(`/api/v1/cases/${caseId}/draft`, 'PUT', null, { content });
}

export async function submitStatus(caseId: string): Promise<CaseDocument> {
  return apiRequest(`/api/v1/cases/${caseId}/submit-status`, 'POST');
}

export async function claimCase(caseId: string): Promise<CaseDocument> {
  return apiRequest(`/api/v1/cases/${caseId}/claim`, 'POST');
}
