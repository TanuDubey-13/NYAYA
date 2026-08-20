import sys
import json
import os
import traceback

def run_tests():
    print("---------------------------------------------")
    print("NYAYA - REGRESSION AND RAG TESTS")
    print("---------------------------------------------")

    # Clear/prepare environment imports
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
        from app.services.rag import KnowledgeRepository, Retriever
        print("[OK] Import Check: All models and API modules imported successfully.")
    except Exception as e:
        print(f"[ERROR] Import Check: Failed. Error: {e}")
        traceback.print_exc()
        sys.exit(1)

    # Helper to clear in-memory db
    def reset_db():
        cases_db.clear()

    # --------------------------------------------------
    # TEST A: Garbage Collection (Solid Waste)
    # --------------------------------------------------
    try:
        reset_db()
        problem = "My area has not had garbage collection for two weeks."
        
        # 1. Intake
        case = triage_case(problem_text=problem, guest_session_id="guest-1", current_user=None)
        assert case.category == "municipal_grievance", f"Expected municipal_grievance, got {case.category}"
        assert case.subcategory == "solid_waste", f"Expected solid_waste, got {case.subcategory}"
        
        # 2. Clarification
        case = respond_case(case_id=case.caseId, question_id="q_locality", answer="Ward 150, Bengaluru, Karnataka", current_user=None)
        
        # 3. Analyze / RAG
        case = analyze_case(case_id=case.caseId, current_user=None)
        
        # Verify evidence
        assert len(case.evidence) > 0, "No evidence retrieved for garbage"
        primary_source = case.evidence[0]
        assert primary_source.sourceId == "SRC-001", f"Expected SRC-001 as primary source, got {primary_source.sourceId}"
        assert case.claims[0].verificationStatus == "VERIFIED", f"Expected VERIFIED claim, got {case.claims[0].verificationStatus}"
        
        print("[OK] TEST A Passed: Garbage collection correctly triaged, retrieved SRC-001, and verified.")
    except Exception as e:
        print(f"[ERROR] TEST A Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # --------------------------------------------------
    # TEST B: Street Light Failure
    # --------------------------------------------------
    try:
        reset_db()
        problem = "The street light outside my house has been broken for three weeks."
        
        case = triage_case(problem_text=problem, guest_session_id="guest-1", current_user=None)
        assert case.subcategory == "street_lighting", f"Expected street_lighting, got {case.subcategory}"
        
        case = respond_case(case_id=case.caseId, question_id="q_locality", answer="Ward 150, Bengaluru, Karnataka", current_user=None)
        case = analyze_case(case_id=case.caseId, current_user=None)
        
        assert len(case.evidence) > 0, "No evidence retrieved for streetlight"
        primary_source = case.evidence[0]
        assert primary_source.sourceId == "SRC-002", f"Expected SRC-002 as primary streetlight source, got {primary_source.sourceId}"
        
        print("[OK] TEST B Passed: Streetlight issue triaged, retrieved SRC-002 primary source.")
    except Exception as e:
        print(f"[ERROR] TEST B Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # --------------------------------------------------
    # TEST C: Pothole (Road Maintenance)
    # --------------------------------------------------
    try:
        reset_db()
        problem = "There is a large pothole on the road near my locality."
        
        case = triage_case(problem_text=problem, guest_session_id="guest-1", current_user=None)
        assert case.subcategory == "road_maintenance", f"Expected road_maintenance, got {case.subcategory}"
        
        case = respond_case(case_id=case.caseId, question_id="q_locality", answer="Ward 150, Bengaluru, Karnataka", current_user=None)
        case = analyze_case(case_id=case.caseId, current_user=None)
        
        assert len(case.evidence) > 0, "No evidence retrieved for potholes"
        primary_source = case.evidence[0]
        assert primary_source.sourceId == "SRC-003", f"Expected SRC-003, got {primary_source.sourceId}"
        
        print("[OK] TEST C Passed: Pothole issue triaged, retrieved SRC-003 road maintenance source.")
    except Exception as e:
        print(f"[ERROR] TEST C Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # --------------------------------------------------
    # TEST D: Overflowing Sewage (Sewerage & Drainage)
    # --------------------------------------------------
    try:
        reset_db()
        problem = "There is sewage overflowing onto the road."
        
        case = triage_case(problem_text=problem, guest_session_id="guest-1", current_user=None)
        assert case.subcategory == "sewerage_drainage", f"Expected sewerage_drainage, got {case.subcategory}"
        
        case = respond_case(case_id=case.caseId, question_id="q_locality", answer="Ward 150, Bengaluru, Karnataka", current_user=None)
        case = analyze_case(case_id=case.caseId, current_user=None)
        
        assert len(case.evidence) > 0, "No evidence retrieved for sewage"
        primary_source = case.evidence[0]
        assert primary_source.sourceId == "SRC-004", f"Expected SRC-004, got {primary_source.sourceId}"
        
        print("[OK] TEST D Passed: Sewage overflow triaged, retrieved SRC-004 drainage source.")
    except Exception as e:
        print(f"[ERROR] TEST D Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # --------------------------------------------------
    # TEST E: Jurisdiction Mismatch Penalty
    # --------------------------------------------------
    try:
        reset_db()
        problem = "My area has not had garbage collection for two weeks."
        
        case = triage_case(problem_text=problem, guest_session_id="guest-1", current_user=None)
        case = respond_case(case_id=case.caseId, question_id="q_locality", answer="Kanpur, Uttar Pradesh", current_user=None)
        case = analyze_case(case_id=case.caseId, current_user=None)
        
        # Verify that Bengaluru specific source is filtered out
        for ev in case.evidence:
            assert ev.sourceId != "SRC-001", "Bengaluru garbage bye-laws must not be returned for Kanpur jurisdiction!"
            
        print("[OK] TEST E Passed: Bengaluru source correctly filtered out for Kanpur jurisdiction query.")
    except Exception as e:
        print(f"[ERROR] TEST E Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # --------------------------------------------------
    # TEST F: NO_EVIDENCE Case
    # --------------------------------------------------
    try:
        reset_db()
        problem = "I need help with my international passport application query."
        
        case = triage_case(problem_text=problem, guest_session_id="guest-1", current_user=None)
        case = respond_case(case_id=case.caseId, question_id="q_locality", answer="Ward 150, Bengaluru, Karnataka", current_user=None)
        case = analyze_case(case_id=case.caseId, current_user=None)
        
        # Verify NO_EVIDENCE mapping
        assert len(case.evidence) == 0, "Expected no evidence for unsupported passport query"
        assert case.claims[0].verificationStatus == "NO_EVIDENCE", f"Expected NO_EVIDENCE, got {case.claims[0].verificationStatus}"
        
        print("[OK] TEST F Passed: Unsupported passport query correctly resolved to NO_EVIDENCE.")
    except Exception as e:
        print(f"[ERROR] TEST F Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # --------------------------------------------------
    # TEST G: Stale Case State Prevention
    # --------------------------------------------------
    try:
        reset_db()
        
        # Create Case 1
        case1 = triage_case("Streetlights are broken", "guest-session", current_user=None)
        case1 = respond_case(case1.caseId, "q_locality", "Bengaluru, Karnataka", current_user=None)
        case1 = analyze_case(case1.caseId, current_user=None)
        
        # Create Case 2 (new intake)
        case2 = triage_case("Garbage is piling up", "guest-session", current_user=None)
        
        # Ensure Case 2 is completely isolated
        assert case2.caseId != case1.caseId, "New intake must produce a unique caseId"
        assert len(case2.evidence) == 0, "New case must initialize with empty evidence lists"
        assert len(case2.claims) == 0, "New case must initialize with empty claims list"
        
        print("[OK] TEST G Passed: Case state isolation and stale data prevention verified.")
    except Exception as e:
        print(f"[ERROR] TEST G Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    print("---------------------------------------------")
    print("ALL REGRESSION TESTS COMPLETED SUCCESSFULLY!")
    print("---------------------------------------------")

if __name__ == "__main__":
    run_tests()
