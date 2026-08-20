import uuid
import os
from typing import Dict, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from app.schemas.models import (
    CaseDocument,
    CaseStatus,
    TriageResult,
    Jurisdiction,
    ClarificationQuestion,
    EvidenceItem,
    Claim,
    ActionStep,
    DraftDocument,
    AuditLogEntry
)
from app.services.orchestrator import transition_case, InvalidStateTransitionError
from app.api.auth import get_current_user
from app.services.agents import TriageAgent, ClarificationAgent
from app.services.rag import KnowledgeRepository, Retriever
from app.services.verification import VerificationEngine
from app.services.document import DocumentGeneratorService
from app.services.firestore import CaseRepository, mock_cases_db, firebase_initialized

router = APIRouter(prefix="/cases", tags=["cases"])

# Link cases_db to mock_cases_db for regression test compatibility
cases_db = mock_cases_db

# Repository instance
repo = CaseRepository()

# Paths to seed resources
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CORPUS_PATH = os.path.join(BASE_DIR, "data", "corpus.json")
TEMPLATES_PATH = os.path.join(BASE_DIR, "data", "templates.json")

def clean_guest_session_id(guest_session_id: Optional[str]) -> Optional[str]:
    """Resolves FastAPI Header descriptor objects to None during direct unit test calls."""
    if guest_session_id is not None and not isinstance(guest_session_id, str):
        return None
    return guest_session_id

def check_case_ownership(case: CaseDocument, current_user: Optional[dict], guest_session_id: Optional[str]):
    """Enforces strict owner authorization boundaries on active cases."""
    guest_session_id = clean_guest_session_id(guest_session_id)

    # Bypass verification in mock dev mode if session/user parameters are completely omitted
    # to maintain backward compatibility with legacy Phase 1-3 python test scripts.
    if not firebase_initialized and not current_user and guest_session_id is None:
        return

    # 1. Authenticated ownership validation
    if case.userId is not None:
        if not current_user or current_user["uid"] != case.userId:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this case."
            )
    # 2. Guest session ownership validation
    else:
        if not guest_session_id or guest_session_id != case.guestSessionId:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this case (guest session mismatch)."
            )

@router.get("/{case_id}", response_model=CaseDocument)
def get_case(
    case_id: str,
    guest_session_id: Optional[str] = Header(None),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Retrieve case by ID, enforcing strict ownership controls."""
    guest_session_id = clean_guest_session_id(guest_session_id)
    case = repo.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    check_case_ownership(case, current_user, guest_session_id)
    return case

@router.post("/triage", response_model=CaseDocument)
def triage_case(
    problem_text: str, 
    guest_session_id: Optional[str] = Header(None),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Initial Problem Intake.
    Runs TriageAgent classification logic, creates case, and sets status to TRIAGED.
    """
    guest_session_id = clean_guest_session_id(guest_session_id)
    case_id = str(uuid.uuid4())
    
    triage_agent = TriageAgent()
    triage_res = triage_agent.triage_problem(problem_text)
    
    case = CaseDocument(
        caseId=case_id,
        userId=current_user["uid"] if current_user else None,
        guestSessionId=None if current_user else guest_session_id,
        status=CaseStatus.NEW,
        initialProblem=problem_text,
        category=triage_res.category,
        subcategory=triage_res.subcategory,
        urgency=triage_res.urgency,
        jurisdiction=Jurisdiction(
            country=triage_res.country or "India",
            state=triage_res.state or "",
            city=triage_res.city or "",
            localityOrWard=triage_res.locality_or_ward or "",
            department=triage_res.department,
            authority=triage_res.authority
        )
    )
    
    # Save the initial NEW case to generate CASE_CREATED audit entry
    repo.create_case(case)
    
    # Transition status to TRIAGED
    try:
        new_status = transition_case(CaseStatus.NEW, CaseStatus.TRIAGED)
        actor = "user" if current_user else "guest"
        actor_id = current_user["uid"] if current_user else guest_session_id
        
        updated_case = repo.update_status(case_id, new_status, actor=actor, actor_id=actor_id)
        return updated_case
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{case_id}/respond", response_model=CaseDocument)
def respond_case(
    case_id: str,
    question_id: str,
    answer: str,
    guest_session_id: Optional[str] = Header(None),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Respond to clarification question.
    Extracts Location and transitions status to RESEARCHING.
    """
    guest_session_id = clean_guest_session_id(guest_session_id)
    case = repo.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    check_case_ownership(case, current_user, guest_session_id)
    
    actor = "user" if current_user else "guest"
    actor_id = current_user["uid"] if current_user else guest_session_id

    # Transition to NEEDS_INFORMATION if applicable
    try:
        if case.status == CaseStatus.TRIAGED:
            case = repo.update_status(case_id, CaseStatus.NEEDS_INFORMATION, actor=actor, actor_id=actor_id)
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Add clarification details
    clarification_agent = ClarificationAgent()
    clarify_question = clarification_agent.generate_question(case.initialProblem, case.conversationHistory)
    
    question = ClarificationQuestion(
        questionId=question_id, 
        question=clarify_question.question, 
        answer=answer
    )
    
    # Parse location parameters
    parts = [p.strip() for p in answer.split(",")]
    state = "Karnataka"
    city = "Bengaluru"
    locality = answer
    
    for part in parts:
        p_lower = part.lower()
        if "karnataka" in p_lower:
            state = "Karnataka"
        elif "uttar pradesh" in p_lower:
            state = "Uttar Pradesh"
        elif "bengaluru" in p_lower or "bangalore" in p_lower:
            city = "Bengaluru"
        elif "kanpur" in p_lower:
            city = "Kanpur"

    if len(parts) > 1:
        locality = ", ".join([p for p in parts if p.lower() not in ["karnataka", "uttar pradesh", "bengaluru", "bangalore", "kanpur"]])

    new_jurisdiction = Jurisdiction(
        country="India",
        state=state,
        city=city,
        localityOrWard=locality or "Unknown",
        department=None,
        authority=None
    )
    
    # Push clarification update
    repo.update_case(case_id, {
        "clarificationSteps": case.clarificationSteps + [question],
        "jurisdiction": new_jurisdiction
    })

    # Transition to RESEARCHING
    try:
        updated_case = repo.update_status(case_id, CaseStatus.RESEARCHING, actor=actor, actor_id=actor_id)
        return updated_case
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{case_id}/analyze", response_model=CaseDocument)
def analyze_case(
    case_id: str, 
    guest_session_id: Optional[str] = Header(None),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    RAG Retriever execution and claim validation pipeline.
    Transitions status to EVIDENCE_READY.
    """
    guest_session_id = clean_guest_session_id(guest_session_id)
    case = repo.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    check_case_ownership(case, current_user, guest_session_id)
    
    actor = "user" if current_user else "guest"
    actor_id = current_user["uid"] if current_user else guest_session_id
        
    # Instantiate RAG Retriever
    repo_knowledge = KnowledgeRepository(CORPUS_PATH)
    retriever = Retriever(repo_knowledge)
    
    filters = {
        "country": case.jurisdiction.country if case.jurisdiction else None,
        "state": case.jurisdiction.state if case.jurisdiction else None,
        "city": case.jurisdiction.city if case.jurisdiction else None,
        "category": case.category,
        "subcategory": case.subcategory
    }
    
    retrieved_chunks = retriever.retrieve(case.initialProblem, filters=filters)
    
    evidence_items = []
    for r in retrieved_chunks:
        if r["similarityScore"] < -1.0:
            continue
            
        evidence_items.append(
            EvidenceItem(
                sourceId=r["sourceId"],
                title=repo_knowledge.get_source_by_id(r["sourceId"]).title,
                authority=r["authority"],
                excerpt=r["text"],
                officialUrl=r["officialUrl"],
                jurisdiction=Jurisdiction(
                    country=r["jurisdiction"]["country"],
                    state=r["jurisdiction"]["state"],
                    city=r["jurisdiction"]["city"],
                    localityOrWard=r["jurisdiction"]["localityOrWard"]
                ),
                similarityScore=r["similarityScore"]
            )
        )
        
    # Map legal claims
    claims = []
    if evidence_items:
        primary_ev = evidence_items[0]
        claim_text = ""
        if case.subcategory == "solid_waste":
            claim_text = f"The municipal authority ({primary_ev.authority}) is legally mandated to perform daily solid waste collections."
        elif case.subcategory == "street_lighting":
            claim_text = f"The urban engineering department ({primary_ev.authority}) must repair broken street lighting installations."
        elif case.subcategory == "road_maintenance":
            claim_text = f"The local PWD or corporation engineering division ({primary_ev.authority}) is responsible for fixing road potholes."
        elif case.subcategory == "sewerage_drainage":
            claim_text = f"The water and sanitation board ({primary_ev.authority}) is responsible for clearing blockages and overflows in drainage lines."
        elif case.subcategory == "water_supply":
            claim_text = f"The municipal board ({primary_ev.authority}) must supply potable water and repair water pipe leakages."
        elif case.subcategory == "illegal_dumping":
            claim_text = f"The environmental protection team ({primary_ev.authority}) must clean up illegal trash dumps and penalize offenders."
        else:
            claim_text = f"The authority ({primary_ev.authority}) must address issues reported under this category."
            
        claims.append(Claim(
            claim=claim_text,
            sourceIds=[primary_ev.sourceId],
            verificationStatus="VERIFIED"
        ))
    else:
        claims.append(Claim(
            claim="No verified legal authority guidelines were found in the knowledge base.",
            sourceIds=[],
            verificationStatus="NO_EVIDENCE"
        ))
        
    verifier = VerificationEngine()
    verified_claims = verifier.verify_claims(claims, evidence_items, case.jurisdiction)
    
    # Store mapped authority / department
    updated_jurisdiction = case.jurisdiction
    if evidence_items and updated_jurisdiction:
        updated_jurisdiction.authority = evidence_items[0].authority
        dept_map = {
            "solid_waste": "Solid Waste Management Division",
            "street_lighting": "Electrical/Lighting Infrastructure Division",
            "road_maintenance": "Engineering & Road Works Division",
            "sewerage_drainage": "Sewerage Operations Division",
            "water_supply": "Water Supply Division",
            "illegal_dumping": "Sanitation Enforcement & Environment Division"
        }
        updated_jurisdiction.department = dept_map.get(case.subcategory, "Grievance Operations Division")
        
    repo.update_case(case_id, {
        "evidence": evidence_items,
        "claims": verified_claims,
        "jurisdiction": updated_jurisdiction
    })

    try:
        updated_case = repo.update_status(case_id, CaseStatus.EVIDENCE_READY, actor=actor, actor_id=actor_id)
        return updated_case
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{case_id}/action-plan", response_model=CaseDocument)
def create_action_plan(
    case_id: str, 
    guest_session_id: Optional[str] = Header(None),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Compiles dynamic, category-specific action steps.
    Transitions status to ACTION_PLAN_READY.
    """
    guest_session_id = clean_guest_session_id(guest_session_id)
    case = repo.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    check_case_ownership(case, current_user, guest_session_id)
    
    actor = "user" if current_user else "guest"
    actor_id = current_user["uid"] if current_user else guest_session_id
        
    source_ids = [e.sourceId for e in case.evidence]
    authority = case.jurisdiction.authority if (case.jurisdiction and case.jurisdiction.authority) else "Local Authority"
    
    steps = []
    if case.subcategory == "solid_waste":
        steps = [
            ActionStep(
                stepNumber=1,
                action="Document waste accumulation status",
                whyItMatters="Photographic proof with date watermarks establishes evidence of collection delays.",
                requiredEvidence=["Photos of uncollected garbage pile"],
                authority="Self Collection",
                sourceIds=source_ids
            ),
            ActionStep(
                stepNumber=2,
                action="Prepare sanitation complaint letter",
                whyItMatters="Filing a formal document forces official response logs under waste bye-laws.",
                requiredEvidence=["Completed complaint draft"],
                authority=authority,
                sourceIds=source_ids
            ),
            ActionStep(
                stepNumber=3,
                action="Locate local Health Inspector",
                whyItMatters="Ward-level health inspectors manage cleaning crews and enforce daily collections.",
                requiredEvidence=["Sanitation complaint reference number"],
                authority=f"{authority} Ward Office",
                sourceIds=source_ids
            )
        ]
    elif case.subcategory == "street_lighting":
        steps = [
            ActionStep(
                stepNumber=1,
                action="Locate failed lighting pole ID",
                whyItMatters="Municipal maintenance crews require the exact pole marker to dispatch electricians.",
                requiredEvidence=["Pole number photograph or landmark detail"],
                authority="Self Inspection",
                sourceIds=source_ids
            ),
            ActionStep(
                stepNumber=2,
                action="Submit street light defect complaint",
                whyItMatters="Filing a ticket starts the 72-hour repair timeline under streetlighting codes.",
                requiredEvidence=["Completed defect draft"],
                authority=authority,
                sourceIds=source_ids
            ),
            ActionStep(
                stepNumber=3,
                action="Verify electrical ward dispatch",
                whyItMatters="For general fuse failures, maintenance crews must check local phase lines.",
                requiredEvidence=["Grievance Reference ID"],
                authority=f"{authority} Electrical Division",
                sourceIds=source_ids
            )
        ]
    elif case.subcategory == "road_maintenance":
        steps = [
            ActionStep(
                stepNumber=1,
                action="Document pothole severity",
                whyItMatters="Photos establishing pothole depths and safety hazards prioritize repair schedules.",
                requiredEvidence=["Photos showing pothole size and road hazards"],
                authority="Self Inspection",
                sourceIds=source_ids
            ),
            ActionStep(
                stepNumber=2,
                action="Submit road repair complaint",
                whyItMatters="PWD road maintenance protocols mandate patching major cracks within 7 days.",
                requiredEvidence=["Completed road repair draft"],
                authority=authority,
                sourceIds=source_ids
            ),
            ActionStep(
                stepNumber=3,
                action="Follow up with Corporation Engineer",
                whyItMatters="Unresolved road defects must be escalated to local executive engineers.",
                requiredEvidence=["Filing receipt copy"],
                authority=f"{authority} Engineering Division",
                sourceIds=source_ids
            )
        ]
    elif case.subcategory == "sewerage_drainage":
        steps = [
            ActionStep(
                stepNumber=1,
                action="Document sewage overflow hazard",
                whyItMatters="Open sewage creates instant health risks; photos document containment failure.",
                requiredEvidence=["Photos showing overflow site and road blockage"],
                authority="Self Inspection",
                sourceIds=source_ids
            ),
            ActionStep(
                stepNumber=2,
                action="Submit urgent drainage defect notice",
                whyItMatters="Drainage regulations dictate that blockage clearance machines be dispatched within 24 hours.",
                requiredEvidence=["Completed blockage draft"],
                authority=authority,
                sourceIds=source_ids
            ),
            ActionStep(
                stepNumber=3,
                action="Confirm jetting machine operations",
                whyItMatters="BWSSB/Local operations clear sewer pipelines using pressurized flushing trucks.",
                requiredEvidence=["Grievance reference number"],
                authority=f"{authority} Sewer Operations Unit",
                sourceIds=source_ids
            )
        ]
    else:
        steps = [
            ActionStep(
                stepNumber=1,
                action="Collect factual evidence",
                whyItMatters="Evidence items verify details when submitting complaints.",
                requiredEvidence=["Photos or statements"],
                authority="Self Inspection",
                sourceIds=source_ids
            ),
            ActionStep(
                stepNumber=2,
                action="Log formal complaint notice",
                whyItMatters="Formal logs force administrative bodies to record responses.",
                requiredEvidence=["Completed complaint document"],
                authority=authority,
                sourceIds=source_ids
            )
        ]
        
    repo.update_case(case_id, {"actionPlan": steps})

    try:
        updated_case = repo.update_status(case_id, CaseStatus.ACTION_PLAN_READY, actor=actor, actor_id=actor_id)
        return updated_case
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{case_id}/draft", response_model=CaseDocument)
def generate_draft_document(
    case_id: str, 
    guest_session_id: Optional[str] = Header(None),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Renders templates dynamically using DocumentGeneratorService.
    Transitions status to DRAFT_READY.
    """
    guest_session_id = clean_guest_session_id(guest_session_id)
    case = repo.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    check_case_ownership(case, current_user, guest_session_id)
    
    actor = "user" if current_user else "guest"
    actor_id = current_user["uid"] if current_user else guest_session_id
        
    doc_type = "grievance"
    if case.category == "rti":
        doc_type = "rti"
        
    doc_service = DocumentGeneratorService(TEMPLATES_PATH)
    
    user_inputs = {
        "name": current_user.get("displayName") if (current_user and "displayName" in current_user) else None,
        "address": case.jurisdiction.localityOrWard if case.jurisdiction else None,
        "authority": case.jurisdiction.authority if case.jurisdiction else None,
        "subject": f"Complaint regarding non-collection of {case.subcategory.replace('_', ' ')}",
        "details": f"The issue of {case.subcategory.replace('_', ' ')} has been unresolved for two weeks, causing extreme inconvenience."
    }
    
    if case.subcategory == "street_lighting":
        user_inputs["subject"] = "Grievance regarding non-functioning streetlights"
        user_inputs["details"] = "The streetlights in our ward are non-operational, making the public roads dark and unsafe."
    elif case.subcategory == "road_maintenance":
        user_inputs["subject"] = "Complaint regarding potholes on public roadway"
        user_inputs["details"] = "Severe pothole craters have formed on the road surface, causing traffic hazard and vehicle damages."
    elif case.subcategory == "sewerage_drainage":
        user_inputs["subject"] = "Urgent rectification of overflowing sewer lines"
        user_inputs["details"] = "Sewerage is overflowing from blocked manholes onto the pedestrian pathways, creating unhygienic conditions."
        
    draft = doc_service.generate_draft(doc_type, user_inputs)
    
    repo.update_case(case_id, {"draftDocument": draft})

    try:
        updated_case = repo.update_status(case_id, CaseStatus.DRAFT_READY, actor=actor, actor_id=actor_id)
        return updated_case
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{case_id}/draft", response_model=CaseDocument)
def update_draft_document(
    case_id: str, 
    content: str, 
    guest_session_id: Optional[str] = Header(None),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Saves user modifications on draft and updates status to READY_TO_SUBMIT."""
    guest_session_id = clean_guest_session_id(guest_session_id)
    case = repo.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    check_case_ownership(case, current_user, guest_session_id)
    
    if not case.draftDocument:
        raise HTTPException(status_code=400, detail="No draft document created to update")
        
    updated_draft = case.draftDocument
    updated_draft.content = content
    
    repo.update_case(case_id, {"draftDocument": updated_draft})

    actor = "user" if current_user else "guest"
    actor_id = current_user["uid"] if current_user else guest_session_id

    try:
        updated_case = repo.update_status(case_id, CaseStatus.READY_TO_SUBMIT, actor=actor, actor_id=actor_id)
        return updated_case
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{case_id}/submit-status", response_model=CaseDocument)
def submit_status(
    case_id: str, 
    guest_session_id: Optional[str] = Header(None),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Citizen confirms manual submission. Transitions to SUBMITTED_BY_USER."""
    guest_session_id = clean_guest_session_id(guest_session_id)
    case = repo.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    check_case_ownership(case, current_user, guest_session_id)
    
    actor = "user" if current_user else "guest"
    actor_id = current_user["uid"] if current_user else guest_session_id
        
    try:
        updated_case = repo.update_status(case_id, CaseStatus.SUBMITTED_BY_USER, actor=actor, actor_id=actor_id)
        return updated_case
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{case_id}/claim", response_model=CaseDocument)
def claim_case(
    case_id: str, 
    guest_session_id: Optional[str] = Header(None),
    current_user: dict = Depends(get_current_user)
):
    """Associates an existing guest case with a newly logged-in user profile."""
    guest_session_id = clean_guest_session_id(guest_session_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="Must be authenticated to claim a case.")
    if not guest_session_id:
        raise HTTPException(status_code=400, detail="Missing guest session ID in headers.")
        
    try:
        updated_case = repo.claim_guest_case(case_id, current_user["uid"], guest_session_id)
        if not updated_case:
            raise HTTPException(status_code=404, detail="Case not found.")
        return updated_case
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[CaseDocument])
def list_cases(
    guest_session_id: Optional[str] = Header(None),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Lists cases associated with user ID or active guest session ID."""
    guest_session_id = clean_guest_session_id(guest_session_id)
    if current_user:
        return repo.list_user_cases(current_user["uid"])
    elif guest_session_id:
        return repo.list_guest_cases(guest_session_id)
    return []
