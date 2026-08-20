from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class CaseStatus(str, Enum):
    NEW = "NEW"
    TRIAGED = "TRIAGED"
    NEEDS_INFORMATION = "NEEDS_INFORMATION"
    RESEARCHING = "RESEARCHING"
    EVIDENCE_READY = "EVIDENCE_READY"
    ACTION_PLAN_READY = "ACTION_PLAN_READY"
    DRAFT_READY = "DRAFT_READY"
    READY_TO_SUBMIT = "READY_TO_SUBMIT"
    SUBMITTED_BY_USER = "SUBMITTED_BY_USER"
    RESOLVED = "RESOLVED"

class Jurisdiction(BaseModel):
    country: str = Field(..., description="Country (e.g. India)")
    state: str = Field(..., description="State or Union Territory")
    city: str = Field(..., description="City or District")
    localityOrWard: str = Field(..., description="Locality, ward number or village name")
    department: Optional[str] = Field(None, description="Target department if identified")
    authority: Optional[str] = Field(None, description="Responsible authority if identified")

class TriageResult(BaseModel):
    category: str
    subcategory: str
    urgency: str = Field("normal", description="urgency level: low, normal, or high")
    country: str
    state: str
    city: str
    locality_or_ward: str
    department: Optional[str] = None
    authority: Optional[str] = None
    problem_summary: str
    key_entities: List[str] = []
    missing_information: List[str] = []
    clarification_question: str
    confidence: float

    @field_validator("urgency")
    @classmethod
    def validate_urgency(cls, v: str) -> str:
        if v.lower() not in ["low", "normal", "high"]:
            raise ValueError("Urgency must be 'low', 'normal', or 'high'")
        return v.lower()

class ClarificationQuestion(BaseModel):
    questionId: str
    question: str
    answer: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class EvidenceItem(BaseModel):
    sourceId: str
    title: str
    authority: str
    excerpt: str
    officialUrl: str
    jurisdiction: Jurisdiction
    similarityScore: Optional[float] = None

class Claim(BaseModel):
    claim: str
    sourceIds: List[str]
    verificationStatus: str = Field("NO_EVIDENCE", description="VERIFIED, NEEDS_VERIFICATION, or NO_EVIDENCE")

    @field_validator("verificationStatus")
    @classmethod
    def validate_verification_status(cls, v: str) -> str:
        valid = ["VERIFIED", "NEEDS_VERIFICATION", "NO_EVIDENCE"]
        if v.upper() not in valid:
            raise ValueError(f"verificationStatus must be one of {valid}")
        return v.upper()

class ActionStep(BaseModel):
    stepNumber: int
    action: str
    whyItMatters: str
    requiredEvidence: List[str] = []
    authority: str
    sourceIds: List[str] = []
    completed: bool = False
    officialSubmissionUrl: Optional[str] = None

class ActionPlan(BaseModel):
    caseId: str
    steps: List[ActionStep]

class DraftDocument(BaseModel):
    docType: str = Field(..., description="Type: grievance, rti, or general")
    title: str
    content: str
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @field_validator("docType")
    @classmethod
    def validate_doc_type(cls, v: str) -> str:
        valid = ["grievance", "rti", "general"]
        if v.lower() not in valid:
            raise ValueError(f"docType must be one of {valid}")
        return v.lower()

class CaseDocument(BaseModel):
    caseId: str
    userId: Optional[str] = None
    guestSessionId: Optional[str] = None
    status: CaseStatus = CaseStatus.NEW
    initialProblem: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    urgency: str = "normal"
    jurisdiction: Optional[Jurisdiction] = None
    conversationHistory: List[dict] = []
    clarificationSteps: List[ClarificationQuestion] = []
    claims: List[Claim] = []
    evidence: List[EvidenceItem] = []
    actionPlan: List[ActionStep] = []
    draftDocument: Optional[DraftDocument] = None
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class KnowledgeSource(BaseModel):
    sourceId: str
    title: str
    authority: str
    jurisdiction: Jurisdiction
    category: str
    subcategory: str = "general"
    officialUrl: str
    content: str
    lastVerified: str
    tags: List[str] = []
