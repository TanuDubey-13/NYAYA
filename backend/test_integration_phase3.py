import sys
import os
import traceback

def run_tests():
    print("---------------------------------------------")
    print("NYAYA - PHASE 3 INTEGRATION TESTS")
    print("---------------------------------------------")

    # 1. Verify API router imports
    try:
        from app.schemas.models import CaseStatus, Claim
        from app.api.cases import (
            triage_case,
            respond_case,
            analyze_case,
            create_action_plan,
            generate_draft_document,
            cases_db
        )
        print("[OK] Import Check: Backend API handlers loaded successfully.")
    except Exception as e:
        print(f"[ERROR] Import Check: Failed. Error: {e}")
        sys.exit(1)

    # Reset utility
    def reset_db():
        cases_db.clear()

    # --------------------------------------------------
    # TEST 1: DYNAMIC END-TO-END CASE TEST
    # --------------------------------------------------
    try:
        reset_db()
        problem = "My area has not had garbage collection for two weeks. I live in Ward 12, Kanpur, Uttar Pradesh."
        
        # Timeline step 1: NEW -> TRIAGED
        case = triage_case(problem_text=problem, guest_session_id="guest-session-p3", current_user=None)
        assert case.status == CaseStatus.TRIAGED, f"Expected TRIAGED status, got {case.status}"
        assert case.category == "municipal_grievance"
        assert case.subcategory == "solid_waste"
        assert case.jurisdiction.state == "Uttar Pradesh", f"Expected state Uttar Pradesh, got {case.jurisdiction.state}"
        assert case.jurisdiction.city == "Kanpur", f"Expected city Kanpur, got {case.jurisdiction.city}"
        assert case.jurisdiction.localityOrWard == "Ward 12", f"Expected ward Ward 12, got {case.jurisdiction.localityOrWard}"
        
        # Timeline step 2: TRIAGED -> RESEARCHING (Location is already provided, but we transition to complete details)
        case = respond_case(case_id=case.caseId, question_id="q_locality", answer="Ward 12, Kanpur, Uttar Pradesh", current_user=None)
        assert case.status == CaseStatus.RESEARCHING, f"Expected RESEARCHING status, got {case.status}"

        # Timeline step 3: RESEARCHING -> EVIDENCE_READY
        case = analyze_case(case_id=case.caseId, current_user=None)
        assert case.status == CaseStatus.EVIDENCE_READY, f"Expected EVIDENCE_READY status, got {case.status}"
        
        # Verify that Bengaluru-specific solid waste source is NOT returned as VERIFIED
        for ev in case.evidence:
            assert ev.sourceId != "SRC-001" or ev.jurisdiction.city == "Kanpur", "Bengaluru source must not be returned for Kanpur jurisdiction!"

        # Timeline step 4: EVIDENCE_READY -> ACTION_PLAN_READY
        case = create_action_plan(case_id=case.caseId, current_user=None)
        assert case.status == CaseStatus.ACTION_PLAN_READY, f"Expected ACTION_PLAN_READY, got {case.status}"
        
        # Timeline step 5: ACTION_PLAN_READY -> DRAFT_READY
        case = generate_draft_document(case_id=case.caseId, current_user=None)
        assert case.status == CaseStatus.DRAFT_READY, f"Expected DRAFT_READY, got {case.status}"
        
        # Verify draft document properties
        assert case.draftDocument is not None, "Draft document is missing"
        assert "[ENTER NAME]" in case.draftDocument.content, "Placeholder [ENTER NAME] is missing"
        assert "Ward 12" in case.draftDocument.content, "Address 'Ward 12' is missing from draft"
        assert "*Disclaimer: AI-generated draft — review before submission.*" in case.draftDocument.content, "AI disclaimer is missing"

        print("[OK] Test 1: Dynamic End-to-End case flow and timeline transitions verified successfully.")
    except Exception as e:
        print(f"[ERROR] Test 1 Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # --------------------------------------------------
    # TEST 2: CROSS-JURISDICTION TEST (Kanpur vs Bengaluru)
    # --------------------------------------------------
    try:
        reset_db()
        problem = "My area has garbage piling up in Kanpur, Uttar Pradesh."
        
        case = triage_case(problem_text=problem, guest_session_id="guest-session-p3", current_user=None)
        case = respond_case(case_id=case.caseId, question_id="q_locality", answer="Kanpur, Uttar Pradesh", current_user=None)
        case = analyze_case(case_id=case.caseId, current_user=None)
        
        # Double check evidence list
        for ev in case.evidence:
            # Bengaluru source SRC-001 must not be included
            assert ev.sourceId != "SRC-001", "Bengaluru source returned for Kanpur case"
            
        print("[OK] Test 2: Cross-jurisdiction rules correctly enforced. Bengaluru sources blocked for Kanpur cases.")
    except Exception as e:
        print(f"[ERROR] Test 2 Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # --------------------------------------------------
    # TEST 3: CROSS-CATEGORY REGRESSION TEST
    # --------------------------------------------------
    try:
        categories = {
            "garbage collection delays": "solid_waste",
            "street light lamp broken": "street_lighting",
            "craters and pothole damage": "road_maintenance",
            "sewage overflow on street": "sewerage_drainage",
            "information from rti department": "rti_request"
        }
        
        for text, expected_sub in categories.items():
            reset_db()
            case = triage_case(problem_text=text, guest_session_id="guest-session-p3", current_user=None)
            assert case.subcategory == expected_sub, f"Text '{text}' expected '{expected_sub}', got '{case.subcategory}'"
            
        print("[OK] Test 3: Cross-category classification isolation verified.")
    except Exception as e:
        print(f"[ERROR] Test 3 Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    print("---------------------------------------------")
    print("ALL PHASE 3 INTEGRATION TESTS PASSED!")
    print("---------------------------------------------")

if __name__ == "__main__":
    run_tests()
