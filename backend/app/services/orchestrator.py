from typing import Dict, List
from app.schemas.models import CaseStatus

# Define allowed transitions in the case state machine
ALLOWED_TRANSITIONS: Dict[CaseStatus, List[CaseStatus]] = {
    CaseStatus.NEW: [CaseStatus.TRIAGED],
    CaseStatus.TRIAGED: [CaseStatus.NEEDS_INFORMATION, CaseStatus.RESEARCHING],
    CaseStatus.NEEDS_INFORMATION: [CaseStatus.RESEARCHING, CaseStatus.NEEDS_INFORMATION],
    CaseStatus.RESEARCHING: [CaseStatus.EVIDENCE_READY],
    CaseStatus.EVIDENCE_READY: [CaseStatus.ACTION_PLAN_READY, CaseStatus.NEEDS_INFORMATION, CaseStatus.RESEARCHING],
    CaseStatus.ACTION_PLAN_READY: [CaseStatus.DRAFT_READY, CaseStatus.NEEDS_INFORMATION, CaseStatus.RESEARCHING],
    CaseStatus.DRAFT_READY: [CaseStatus.READY_TO_SUBMIT, CaseStatus.NEEDS_INFORMATION, CaseStatus.RESEARCHING],
    CaseStatus.READY_TO_SUBMIT: [CaseStatus.SUBMITTED_BY_USER, CaseStatus.NEEDS_INFORMATION, CaseStatus.RESEARCHING],
    CaseStatus.SUBMITTED_BY_USER: [CaseStatus.RESOLVED],
    CaseStatus.RESOLVED: [CaseStatus.RESEARCHING]  # Re-open if new info arises
}

class InvalidStateTransitionError(ValueError):
    """Raised when an invalid case state transition is attempted."""
    pass

def can_transition(current: CaseStatus, target: CaseStatus) -> bool:
    """Checks if a transition from current to target state is allowed."""
    allowed = ALLOWED_TRANSITIONS.get(current, [])
    return target in allowed

def transition_case(current: CaseStatus, target: CaseStatus) -> CaseStatus:
    """
    Attempts to transition a case to a target status.
    Raises InvalidStateTransitionError if the transition is illegal.
    """
    if can_transition(current, target):
        return target
    raise InvalidStateTransitionError(
        f"Invalid transition: Cannot change case status from {current.value} to {target.value}"
    )

class CaseOrchestrator:
    """
    Manages the step-by-step pipeline execution for cases.
    For Phase 1, it provides the shell for coordinate tasks.
    """
    def __init__(self):
        pass

    def run_pipeline(self, case_id: str):
        # Shell method for coordinate execution in later phases
        pass
