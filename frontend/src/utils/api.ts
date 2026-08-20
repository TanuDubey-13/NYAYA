// Simple Typed API Client for NYAYA Backend

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
    department?: string;
    authority?: string;
  };
  conversationHistory: Array<{ role: string; content: string; timestamp: string }>;
  claims: Array<{ claim: string; sourceIds: string[]; verificationStatus: string }>;
  evidence: Array<{
    sourceId: string;
    title: string;
    authority: string;
    excerpt: string;
    officialUrl: string;
    jurisdiction: { country: string; state: string; city: string };
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

export async function checkBackendHealth(): Promise<HealthResponse> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Health check error:", error);
    throw error;
  }
}

export async function fetchCases(guestSessionId?: string, authToken?: string): Promise<CaseDocument[]> {
  const headers: Record<string, string> = {};
  if (guestSessionId) headers['guest-session-id'] = guestSessionId;
  if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

  const response = await fetch(`${API_BASE}/api/v1/cases`, { headers });
  if (!response.ok) {
    throw new Error(`Failed to fetch cases: ${response.statusText}`);
  }
  return response.json();
}

export async function submitIntake(
  problemText: string,
  guestSessionId?: string,
  authToken?: string
): Promise<CaseDocument> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  };
  if (guestSessionId) headers['guest-session-id'] = guestSessionId;
  if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

  // Since it accepts query params or JSON body depending on routing, 
  // our FastAPI endpoint defines it as query parameters: triage_case(problem_text: str, ...)
  const url = new URL(`${API_BASE}/api/v1/cases/triage`);
  url.searchParams.append("problem_text", problemText);

  const response = await fetch(url.toString(), {
    method: 'POST',
    headers
  });
  if (!response.ok) {
    throw new Error(`Intake submission failed: ${response.statusText}`);
  }
  return response.json();
}
