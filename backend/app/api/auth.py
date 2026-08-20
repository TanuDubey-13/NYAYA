from typing import Optional
from fastapi import Header, HTTPException, status

def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """
    Dependency to fetch the authenticated user's profile.
    For Phase 1 / Guest Mode, missing auth headers return None (Guest).
    If Bearer token is provided, it simulates token verification.
    """
    if not authorization:
        return None
        
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Must start with 'Bearer '"
        )
        
    token = authorization.replace("Bearer ", "").strip()
    
    # Mock Token mapping for testing
    if token == "mock-admin-token":
        return {"uid": "admin-uid", "role": "admin", "email": "admin@nyaya.org"}
    elif token == "mock-user-token":
        return {"uid": "user-uid", "role": "citizen", "email": "user@nyaya.org"}
        
    return {"uid": f"uid-{token[:8]}", "role": "citizen", "email": "citizen@nyaya.org"}
