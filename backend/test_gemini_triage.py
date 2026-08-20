import os
import sys
import traceback

def run_tests():
    print("---------------------------------------------")
    print("NYAYA - GEMINI STRUCTURED TRIAGE TESTS")
    print("---------------------------------------------")

    # 1. Imports
    try:
        from app.schemas.models import TriageResult
        from app.services.agents import TriageAgent
        print("[OK] Import Check: TriageAgent and TriageResult loaded successfully.")
    except Exception as e:
        print(f"[ERROR] Import Check: Failed. Error: {e}")
        sys.exit(1)

    agent = TriageAgent()

    # Save original key if exists
    original_key = os.getenv("GEMINI_API_KEY")

    # Force fallback mode by removing API key for local baseline tests
    os.environ["GEMINI_API_KEY"] = ""

    print("\n--- RUNNING BASELINE FALLBACK HEURISTIC TESTS ---")

    # TEST A: Garbage collection (solid_waste)
    try:
        res = agent.triage_problem("My area has not had garbage collection for two weeks.")
        assert res.category == "municipal_grievance"
        assert res.subcategory == "solid_waste"
        assert "state" in res.missing_information or "city" in res.missing_information
        assert len(res.clarification_question) > 0
        print("[OK] Test A: Natural language garbage collection correctly triaged.")
    except Exception as e:
        print(f"[ERROR] Test A Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # TEST B: Municipal waste piling up (solid_waste)
    try:
        res = agent.triage_problem("The municipal vehicle hasn't come for days and waste is piling up outside our houses.")
        assert res.subcategory == "solid_waste"
        print("[OK] Test B: Semantic waste piling variation correctly triaged.")
    except Exception as e:
        print(f"[ERROR] Test B Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # TEST C: Street light failure (street_lighting)
    try:
        res = agent.triage_problem("The lamp outside my house has stopped working and the whole lane is dark at night.")
        assert res.subcategory == "street_lighting"
        print("[OK] Test C: Streetlight lane dark variation correctly triaged.")
    except Exception as e:
        print(f"[ERROR] Test C Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # TEST D: Crater on the road (road_maintenance)
    try:
        res = agent.triage_problem("There is a huge crater on the road and vehicles are struggling to pass.")
        assert res.subcategory == "road_maintenance"
        print("[OK] Test D: Pothole road crater variation correctly triaged.")
    except Exception as e:
        print(f"[ERROR] Test D Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # TEST E: Sewerage overflow (sewerage_drainage)
    try:
        res = agent.triage_problem("Dirty water and sewage are flowing onto the street.")
        assert res.subcategory == "sewerage_drainage"
        assert res.urgency == "high"
        print("[OK] Test E: Sewage overflow on road variation correctly triaged.")
    except Exception as e:
        print(f"[ERROR] Test E Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # TEST F: RTI request
    try:
        res = agent.triage_problem("I want information from a government department about how public funds were spent.")
        assert res.category == "rti"
        assert res.subcategory == "rti_request"
        print("[OK] Test F: Public funds RTI information request correctly triaged.")
    except Exception as e:
        print(f"[ERROR] Test F Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # TEST G: Already-provided jurisdiction
    try:
        res = agent.triage_problem("Garbage has not been collected for two weeks in Ward 12, Kanpur, Uttar Pradesh.")
        assert res.city.lower() == "kanpur"
        assert res.state.lower() == "uttar pradesh"
        assert res.locality_or_ward.lower() == "ward 12"
        # Since details are fully present, missing_information should be empty
        assert len(res.missing_information) == 0
        assert res.clarification_question == ""
        print("[OK] Test G: Fully provided jurisdiction parsed, avoiding duplicate clarification queries.")
    except Exception as e:
        print(f"[ERROR] Test G Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # TEST H: Low-confidence input
    try:
        res = agent.triage_problem("hi")
        assert res.confidence < 0.6
        assert "not yet confident" in res.clarification_question.lower()
        print("[OK] Test H: Low confidence query returned explanatory clarification question.")
    except Exception as e:
        print(f"[ERROR] Test H Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # TEST I: Gemini Failure Fallback with invalid key
    try:
        os.environ["GEMINI_API_KEY"] = "INVALID_MOCK_GEMINI_KEY"
        res = agent.triage_problem("The street light lamp outside my house has stopped working.")
        # Ensure it falls back to rule-based parser without throwing exception
        assert res.subcategory == "street_lighting"
        print("[OK] Test I: Triage handled invalid API key gracefully via heuristic fallback.")
    except Exception as e:
        print(f"[ERROR] Test I Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # Restore key
    if original_key:
        os.environ["GEMINI_API_KEY"] = original_key
    else:
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]

    print("---------------------------------------------")
    print("ALL GEMINI TRIAGE TEST CHECKPOINTS PASSED!")
    print("---------------------------------------------")

if __name__ == "__main__":
    run_tests()
