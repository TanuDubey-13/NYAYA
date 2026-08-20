from typing import List, Optional
from app.schemas.models import Claim, EvidenceItem, Jurisdiction

class VerificationEngine:
    """
    Evaluates claims and assigns verification statuses based on strict metadata checks.
    Verification status rules:
    - VERIFIED: Claim matches retrieved evidence, official URL is present and ends with/contains .gov.in or .gov,
                and the source's state/city matches the user's active state/city.
    - NEEDS_VERIFICATION: Source is a national fallback, state-level rule with city conflict, or non-official URL.
    - NO_EVIDENCE: Claim has no matching source IDs retrieved.
    """
    def verify_claims(
        self, 
        claims: List[Claim], 
        evidence_items: List[EvidenceItem], 
        user_jurisdiction: Optional[Jurisdiction] = None
    ) -> List[Claim]:
        evidence_map = {e.sourceId: e for e in evidence_items}
        
        updated_claims = []
        for c in claims:
            if not c.sourceIds:
                c.verificationStatus = "NO_EVIDENCE"
                updated_claims.append(c)
                continue
                
            has_matching_evidence = False
            all_verified = True
            
            for sid in c.sourceIds:
                ev = evidence_map.get(sid)
                if not ev:
                    all_verified = False
                    continue
                    
                has_matching_evidence = True
                
                # Check 1: URL must be present
                url = ev.officialUrl or ""
                if not url:
                    all_verified = False
                    continue
                    
                # Check 2: Authoritative domain check (.gov or .gov.in)
                is_official = any(domain in url.lower() for domain in [".gov.in", ".gov"])
                if not is_official:
                    all_verified = False
                    continue
                    
                # Check 3: Jurisdiction match
                if user_jurisdiction:
                    user_state = user_jurisdiction.state.lower().strip() if user_jurisdiction.state else ""
                    user_city = user_jurisdiction.city.lower().strip() if user_jurisdiction.city else ""
                    
                    src_state = ev.jurisdiction.state.lower().strip() if ev.jurisdiction.state else ""
                    src_city = ev.jurisdiction.city.lower().strip() if ev.jurisdiction.city else ""
                    
                    # Exact City and State match
                    if src_state == user_state and src_city == user_city:
                        # Direct local match
                        pass
                    # If it's a national fallback state
                    elif src_state == "national":
                        all_verified = False
                    # State matches but city conflicts
                    elif src_state == user_state and src_city != user_city:
                        all_verified = False
                    # Any other mismatch
                    else:
                        all_verified = False
                else:
                    all_verified = False
                    
            if not has_matching_evidence:
                c.verificationStatus = "NO_EVIDENCE"
            elif all_verified:
                c.verificationStatus = "VERIFIED"
            else:
                c.verificationStatus = "NEEDS_VERIFICATION"
                
            updated_claims.append(c)
            
        return updated_claims
