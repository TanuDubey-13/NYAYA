from typing import Optional
from fastapi import Header, HTTPException, status

# Import firebase_initialized status from firestore service
from app.services.firestore import firebase_initialized

def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """
    Dependency to verify Firebase ID tokens passed in the Authorization header.
    Returns the verified user's payload (uid, email, role) or None for guest requests.
    Supports mock tokens in development fallback mode.
    """
    if not authorization:
        return None
        
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Must start with 'Bearer '"
        )
        
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is empty."
        )

    # 1. Production Mode: Verify with Firebase Admin SDK
    if firebase_initialized:
        try:
            from firebase_admin import auth
            decoded_token = auth.verify_id_token(token)
            return {
                "uid": decoded_token.get("uid"),
                "email": decoded_token.get("email"),
                "role": decoded_token.get("role", "citizen")
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Firebase token verification failed: {e}"
            )
            
    # 2. Local Fallback/Development Mode: Check mock tokens
    else:
        if token == "mock-admin-token":
            return {"uid": "admin-uid", "role": "admin", "email": "admin@nyaya.org"}
        elif token == "mock-user-token":
            return {"uid": "user-uid", "role": "citizen", "email": "user@nyaya.org"}
        elif token.startswith("mock-token-"):
            return {"uid": f"uid-{token[11:19]}", "role": "citizen", "email": "citizen@nyaya.org"}
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid dev bearer token. (Use 'mock-user-token' for local testing)"
        )
