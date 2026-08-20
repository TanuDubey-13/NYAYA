import sys
import os
import uuid
import traceback
from fastapi import HTTPException

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    print("---------------------------------------------")
    print("NYAYA - PHASE 4 AUTH & FIRESTORE TESTS")
    print("---------------------------------------------")

    # 1. Imports
    try:
        from app.schemas.models import CaseDocument, CaseStatus, AuditLogEntry, Jurisdiction
        from app.services.firestore import CaseRepository, mock_cases_db, firebase_initialized
        from app.api.auth import get_current_user
        from app.api.cases import (
            triage_case,
            respond_case,
            analyze_case,
            create_action_plan,
            generate_draft_document,
            submit_status,
            claim_case,
            list_cases,
            get_case
        )
        print("[OK] Import Check: Firestore repository and API handlers imported successfully.")
    except Exception as e:
        print(f"[ERROR] Import Check: Failed. Error: {e}")
        sys.exit(1)

    # --------------------------------------------------
    # A & B. REPOSITORY AND FALLBACK TESTS
    # --------------------------------------------------
    try:
        repo = CaseRepository()
        assert not repo.use_firestore, "Firestore should be false during local test executions (no keys)"
        print("[OK] Test A/B: In-memory fallback mode is active when Firebase keys are missing.")
        
        # Test create / read / update on repository
        case_id = str(uuid.uuid4())
        test_case = CaseDocument(
            caseId=case_id,
            userId=None,
            guestSessionId="session-abc",
            status=CaseStatus.NEW,
            initialProblem="Garbage piling up",
            jurisdiction=Jurisdiction(country="India", state="Karnataka", city="Bengaluru", localityOrWard="Ward 12")
        )
        repo.create_case(test_case)
        
        retrieved = repo.get_case(case_id)
        assert retrieved is not None
        assert retrieved.initialProblem == "Garbage piling up"
        
        repo.update_case(case_id, {"urgency": "high"})
        updated = repo.get_case(case_id)
        assert updated.urgency == "high"
        
        print("[OK] Test A: Repository create, read, and update functions verified successfully.")
    except Exception as e:
        print(f"[ERROR] Repository Tests Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # --------------------------------------------------
    # C, D & E. AUTHENTICATION SERVICE TESTS
    # --------------------------------------------------
    try:
        # Invalid format
        try:
            get_current_user(authorization="Token 12345")
            assert False, "Should raise HTTP 401 for invalid format"
        except HTTPException as e:
            assert e.status_code == 401
            
        # Empty token
        try:
            get_current_user(authorization="Bearer ")
            assert False, "Should raise HTTP 401 for empty token"
        except HTTPException as e:
            assert e.status_code == 401
            
        # Invalid Token
        try:
            get_current_user(authorization="Bearer bad-key")
            assert False, "Should raise HTTP 401 for invalid dev keys"
        except HTTPException as e:
            assert e.status_code == 401
            
        # Valid Citizen Token
        user_payload = get_current_user(authorization="Bearer mock-user-token")
        assert user_payload["uid"] == "user-uid"
        assert user_payload["role"] == "citizen"
        
        # Valid Admin Token
        admin_payload = get_current_user(authorization="Bearer mock-admin-token")
        assert admin_payload["uid"] == "admin-uid"
        assert admin_payload["role"] == "admin"
        
        # Guest (None) Token
        guest_payload = get_current_user(authorization=None)
        assert guest_payload is None
        
        print("[OK] Test C/D/E: Auth verify middleware (valid, invalid, guest) matches constraints.")
    except Exception as e:
        print(f"[ERROR] Auth Tests Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # --------------------------------------------------
    # F & J. GUEST SESSIONS & OWNER ACCESS TESTS
    # --------------------------------------------------
    try:
        mock_cases_db.clear()
        
        # Create a guest case
        case = triage_case(
            problem_text="Trash is piling up outside.", 
            guest_session_id="guest-session-123", 
            current_user=None
        )
        assert case.userId is None
        assert case.guestSessionId == "guest-session-123"
        print("[OK] Test F: Guest case created with valid guest session association.")
        
        # Attempt to access with wrong guest session
        try:
            get_case(case_id=case.caseId, guest_session_id="wrong-session-xyz", current_user=None)
            assert False, "Should forbid access for wrong guest session ID"
        except HTTPException as e:
            assert e.status_code == 403
            
        # Access with correct guest session
        case_access = get_case(case_id=case.caseId, guest_session_id="guest-session-123", current_user=None)
        assert case_access.caseId == case.caseId
        
        print("[OK] Test J: Access controls prevent mismatched guest access.")
    except Exception as e:
        print(f"[ERROR] Case Access Control Tests Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # --------------------------------------------------
    # G, H & I. CLAIM GUEST CASE FLOW
    # --------------------------------------------------
    try:
        mock_cases_db.clear()
        
        # Create guest case
        case = triage_case(
            problem_text="Road has potholes", 
            guest_session_id="guest-session-p4", 
            current_user=None
        )
        
        # 1. Claim case with wrong guest session ID header
        try:
            claim_case(
                case_id=case.caseId,
                guest_session_id="wrong-guest-session",
                current_user={"uid": "user-uid-p4", "role": "citizen"}
            )
            assert False, "Should raise ValueError mismatch"
        except HTTPException as e:
            assert e.status_code == 400
            assert "guest session mismatch" in e.detail.lower()
            
        # 2. Claim case successfully
        claimed = claim_case(
            case_id=case.caseId,
            guest_session_id="guest-session-p4",
            current_user={"uid": "user-uid-p4", "role": "citizen"}
        )
        assert claimed.userId == "user-uid-p4"
        assert claimed.guestSessionId is None
        print("[OK] Test G: Guest case claimed successfully by authenticated user.")
        
        # 3. Attempt claiming a case that is already claimed
        try:
            claim_case(
                case_id=case.caseId,
                guest_session_id="guest-session-p4",
                current_user={"uid": "another-user-uid", "role": "citizen"}
            )
            assert False, "Should not claim already claimed case"
        except HTTPException as e:
            assert e.status_code == 400
            assert "already claimed" in e.detail.lower()
            
        print("[OK] Test H/I: Re-claiming or wrong session claiming rejected successfully.")
    except Exception as e:
        print(f"[ERROR] Claim Case Tests Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # --------------------------------------------------
    # K, L & M. LISTING, SUBMISSIONS, AND AUDIT CHECKS
    # --------------------------------------------------
    try:
        mock_cases_db.clear()
        
        # Create cases under multiple owners
        triage_case("Waste problem", "session-1", None)
        c2 = triage_case("Street light issue", "session-2", None)
        claim_case(c2.caseId, "session-2", {"uid": "user-a", "role": "citizen"})
        
        # List cases under user-a
        user_a_cases = list_cases(guest_session_id=None, current_user={"uid": "user-a"})
        assert len(user_a_cases) == 1
        assert user_a_cases[0].caseId == c2.caseId
        
        # Check audit log timestamps & transitions
        audit = c2.auditLog
        assert len(audit) >= 3  # CASE_CREATED, STATE_TRANSITION_TRIAGED, CASE_CLAIMED
        events = [entry.event for entry in audit]
        assert "CASE_CREATED" in events
        assert "STATE_TRANSITION_TRIAGED" in events
        assert "CASE_CLAIMED" in events
        print("[OK] Test M: Audit event logs correctly register case lifecycle events.")
        
        # Transition state and check status
        # First transition c2 through timeline to enable submission status check
        c2.status = CaseStatus.READY_TO_SUBMIT
        repo.update_case(c2.caseId, {"status": CaseStatus.READY_TO_SUBMIT})
        
        submitted = submit_status(c2.caseId, guest_session_id=None, current_user={"uid": "user-a"})
        assert submitted.status == CaseStatus.SUBMITTED_BY_USER
        print("[OK] Test L: Citizen confirmation transitions state to SUBMITTED_BY_USER.")
        
    except Exception as e:
        print(f"[ERROR] Case Listing/Audit Tests Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    print("---------------------------------------------")
    print("ALL PHASE 4 AUTH & FIRESTORE TEST CHECKPOINTS PASSED!")
    print("---------------------------------------------")

if __name__ == "__main__":
    run_tests()
