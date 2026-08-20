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
    DraftDocument
)
from app.services.orchestrator import transition_case, InvalidStateTransitionError
from app.api.auth import get_current_user
from app.services.agents import TriageAgent, ClarificationAgent
from app.services.rag import KnowledgeRepository, Retriever
from app.services.verification import VerificationEngine
from app.services.document import DocumentGeneratorService

router = APIRouter(prefix="/cases", tags=["cases"])

# In-memory database for testing Phase 1
cases_db: Dict[str, CaseDocument] = {}

# Paths to seed resources
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CORPUS_PATH = os.path.join(BASE_DIR, "data", "corpus.json")
TEMPLATES_PATH = os.path.join(BASE_DIR, "data", "templates.json")

@router.post("/triage", response_model=CaseDocument)
def triage_case(
    problem_text: str, 
    guest_session_id: Optional[str] = Header(None),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Initial Problem Intake.
    Runs TriageAgent keyword logic to determine category, subcategory, urgency,
    creates a case, and transitions state NEW -> TRIAGED.
    """
    case_id = str(uuid.uuid4())
    
    # 1. Instantiate TriageAgent
    triage_agent = TriageAgent()
    triage_res = triage_agent.triage_problem(problem_text)
    
    # 2. Create NEW Case
    case = CaseDocument(
        caseId=case_id,
        userId=current_user["uid"] if current_user else None,
        guestSessionId=guest_session_id,
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
    
    # 3. Transition NEW -> TRIAGED
    try:
        case.status = transition_case(case.status, CaseStatus.TRIAGED)
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # Store in memory
    cases_db[case_id] = case
    return case

@router.post("/{case_id}/respond", response_model=CaseDocument)
def respond_case(
    case_id: str,
    question_id: str,
    answer: str,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Respond to clarification question.
    Extracts City/State from reply.
    Transitions TRIAGED -> NEEDS_INFORMATION -> RESEARCHING.
    """
    case = cases_db.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if case.userId and (not current_user or case.userId != current_user["uid"]):
        raise HTTPException(status_code=403, detail="Not authorized to edit this case")

    # Transition to NEEDS_INFORMATION if not already there
    try:
        if case.status == CaseStatus.TRIAGED:
            case.status = transition_case(case.status, CaseStatus.NEEDS_INFORMATION)
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Add question/response record
    clarification_agent = ClarificationAgent()
    clarify_question = clarification_agent.generate_question(case.initialProblem, case.conversationHistory)
    
    question = ClarificationQuestion(
        questionId=question_id, 
        question=clarify_question.question, 
        answer=answer
    )
    case.clarificationSteps.append(question)
    
    # Parse city & state from user response (Kanpur, Uttar Pradesh / Bengaluru, Karnataka)
    parts = [p.strip() for p in answer.split(",")]
    state = "Karnataka"      # Default fallback
    city = "Bengaluru"       # Default fallback
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
        # Locality is everything besides the matched state/city
        locality = ", ".join([p for p in parts if p.lower() not in ["karnataka", "uttar pradesh", "bengaluru", "bangalore", "kanpur"]])

    # Save resolved jurisdiction attributes
    case.jurisdiction = Jurisdiction(
        country="India",
        state=state,
        city=city,
        localityOrWard=locality or "Unknown",
        department=None,
        authority=None
    )

    # Transition to RESEARCHING
    try:
        case.status = transition_case(case.status, CaseStatus.RESEARCHING)
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    cases_db[case_id] = case
    return case

@router.post("/{case_id}/analyze", response_model=CaseDocument)
def analyze_case(case_id: str, current_user: Optional[dict] = Depends(get_current_user)):
    """
    RAG Retriever execution and claim validation pipeline.
    Transitions state RESEARCHING -> EVIDENCE_READY.
    """
    case = cases_db.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    try:
        case.status = transition_case(case.status, CaseStatus.EVIDENCE_READY)
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # Instantiate RAG Retriever
    repo = KnowledgeRepository(CORPUS_PATH)
    retriever = Retriever(repo)
    
    # Configure retriever parameters
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
        # Avoid loading extremely penalized sources in the active panel
        if r["similarityScore"] < -1.0:
            continue
            
        evidence_items.append(
            EvidenceItem(
                sourceId=r["sourceId"],
                title=repo.get_source_by_id(r["sourceId"]).title,
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
        
    case.evidence = evidence_items
    
    # Formulate claim mappings
    claims = []
    if evidence_items:
        primary_ev = evidence_items[0]
        
        # Build category-aware claims
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
        
    # Run claim validation via VerificationEngine
    verifier = VerificationEngine()
    case.claims = verifier.verify_claims(claims, evidence_items, case.jurisdiction)
    
    # Store mapped authority/department
    if evidence_items and case.jurisdiction:
        case.jurisdiction.authority = evidence_items[0].authority
        
        dept_map = {
            "solid_waste": "Solid Waste Management Division",
            "street_lighting": "Electrical/Lighting Infrastructure Division",
            "road_maintenance": "Engineering & Road Works Division",
            "sewerage_drainage": "Sewerage Operations Division",
            "water_supply": "Water Supply Division",
            "illegal_dumping": "Sanitation Enforcement & Environment Division"
        }
        case.jurisdiction.department = dept_map.get(case.subcategory, "Grievance Operations Division")
        
    cases_db[case_id] = case
    return case

@router.post("/{case_id}/action-plan", response_model=CaseDocument)
def create_action_plan(case_id: str, current_user: Optional[dict] = Depends(get_current_user)):
    """
    Compiles dynamic, category-specific action steps.
    Transitions case state EVIDENCE_READY -> ACTION_PLAN_READY.
    """
    case = cases_db.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    try:
        case.status = transition_case(case.status, CaseStatus.ACTION_PLAN_READY)
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    source_ids = [e.sourceId for e in case.evidence]
    authority = case.jurisdiction.authority if (case.jurisdiction and case.jurisdiction.authority) else "Local Authority"
    
    # Compile dynamic steps
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
        
    case.actionPlan = steps
    cases_db[case_id] = case
    return case

@router.post("/{case_id}/draft", response_model=CaseDocument)
def generate_draft_document(case_id: str, current_user: Optional[dict] = Depends(get_current_user)):
    """
    Renders templates dynamically using DocumentGeneratorService.
    Transitions case state ACTION_PLAN_READY -> DRAFT_READY.
    """
    case = cases_db.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    try:
        case.status = transition_case(case.status, CaseStatus.DRAFT_READY)
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # Triage template configuration
    doc_type = "grievance"
    if case.category == "rti":
        doc_type = "rti"
        
    doc_service = DocumentGeneratorService(TEMPLATES_PATH)
    
    # Formulate inputs mapping
    user_inputs = {
        "name": current_user.get("displayName") if current_user else None,
        "address": case.jurisdiction.localityOrWard if case.jurisdiction else None,
        "authority": case.jurisdiction.authority if case.jurisdiction else None,
        "subject": f"Complaint regarding non-collection of {case.subcategory.replace('_', ' ')}",
        "details": f"The issue of {case.subcategory.replace('_', ' ')} has been unresolved for two weeks, causing extreme inconvenience."
    }
    
    # Custom contextual templates
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
    case.draftDocument = draft
    
    cases_db[case_id] = case
    return case

@router.put("/{case_id}/draft", response_model=CaseDocument)
def update_draft_document(
    case_id: str, 
    content: str, 
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Saves user modifications on draft and updates status to READY_TO_SUBMIT."""
    case = cases_db.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if not case.draftDocument:
        raise HTTPException(status_code=400, detail="No draft document created to update")
        
    case.draftDocument.content = content
    
    try:
        case.status = transition_case(case.status, CaseStatus.READY_TO_SUBMIT)
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    cases_db[case_id] = case
    return case

@router.post("/{case_id}/submit-status", response_model=CaseDocument)
def submit_status(case_id: str, current_user: Optional[dict] = Depends(get_current_user)):
    """Citizen confirms they manually submitted complaint, transitions to SUBMITTED_BY_USER."""
    case = cases_db.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    try:
        case.status = transition_case(case.status, CaseStatus.SUBMITTED_BY_USER)
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    cases_db[case_id] = case
    return case

@router.post("/{case_id}/claim", response_model=CaseDocument)
def claim_case(case_id: str, current_user: dict = Depends(get_current_user)):
    """Merges a guest case into the newly authenticated user profile."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Must be authenticated to claim a case")
        
    case = cases_db.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    # Associate user
    case.userId = current_user["uid"]
    cases_db[case_id] = case
    return case

@router.get("", response_model=List[CaseDocument])
def list_cases(
    guest_session_id: Optional[str] = Header(None),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Lists cases associated with user ID or active guest session ID."""
    results = []
    for case in cases_db.values():
        if current_user and case.userId == current_user["uid"]:
            results.append(case)
        elif not current_user and guest_session_id and case.guestSessionId == guest_session_id and case.userId is None:
            results.append(case)
    return results
