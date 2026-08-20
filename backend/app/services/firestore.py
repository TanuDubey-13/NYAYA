import os
from typing import Dict, List, Optional
from datetime import datetime
from app.schemas.models import CaseDocument, CaseStatus, AuditLogEntry

# Initialize Firebase Admin SDK
firebase_initialized = False
db_client = None

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    # Check credentials in standard locations or specific variables
    cred = None
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    elif os.getenv("FIREBASE_PROJECT_ID") and os.getenv("FIREBASE_CLIENT_EMAIL") and os.getenv("FIREBASE_PRIVATE_KEY"):
        private_key = os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n")
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "private_key": private_key,
            "token_uri": "https://oauth2.googleapis.com/token",
        })
        
    if cred:
        # Initialize app if not already initialized
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db_client = firestore.client()
        firebase_initialized = True
        print("[FIRESTORE] Successfully connected to Firebase Firestore.")
    else:
        print("[FIRESTORE WARNING] No Firebase credentials available. Falling back to LOCAL DEV MOCK storage.")
except Exception as e:
    print(f"[FIRESTORE WARNING] Firebase initialization failed: {e}. Falling back to LOCAL DEV MOCK storage.")

# Local in-memory dictionary acting as the developer mock fallback
mock_cases_db: Dict[str, CaseDocument] = {}

class CaseRepository:
    """
    Abstractions for case storage and retrieval.
    Wraps Firestore database operations and automatically falls back to in-memory development dictionary if Firestore is unconfigured.
    """
    def __init__(self):
        self.use_firestore = firebase_initialized and db_client is not None
        self.db = db_client

    def create_case(self, case: CaseDocument) -> CaseDocument:
        # Add initial audit log entry
        if not any(entry.event == "CASE_CREATED" for entry in case.auditLog):
            case.auditLog.append(AuditLogEntry(
                event="CASE_CREATED",
                fromStatus=None,
                toStatus=case.status.value,
                actor="guest" if case.userId is None else "user",
                actorId=case.userId or case.guestSessionId
            ))
            
        if self.use_firestore:
            doc_ref = self.db.collection("cases").document(case.caseId)
            doc_ref.set(case.dict())
        else:
            mock_cases_db[case.caseId] = case
        return case

    def get_case(self, case_id: str) -> Optional[CaseDocument]:
        if self.use_firestore:
            doc_ref = self.db.collection("cases").document(case_id)
            doc = doc_ref.get()
            if doc.exists:
                return CaseDocument(**doc.to_dict())
            return None
        else:
            return mock_cases_db.get(case_id)

    def update_case(self, case_id: str, updates: dict) -> Optional[CaseDocument]:
        case = self.get_case(case_id)
        if not case:
            return None
            
        # Update fields on CaseDocument
        for key, val in updates.items():
            if hasattr(case, key):
                setattr(case, key, val)
                
        case.updatedAt = datetime.utcnow().isoformat()
        
        # Keep Pydantic schemas serialized in Firestore
        serialized_updates = {}
        for key, val in updates.items():
            if hasattr(val, 'dict'):
                serialized_updates[key] = val.dict()
            else:
                serialized_updates[key] = val
        serialized_updates["updatedAt"] = case.updatedAt

        if self.use_firestore:
            doc_ref = self.db.collection("cases").document(case_id)
            doc_ref.update(serialized_updates)
        else:
            mock_cases_db[case_id] = case
            
        return case

    def append_conversation(self, case_id: str, message: dict) -> Optional[CaseDocument]:
        case = self.get_case(case_id)
        if not case:
            return None
            
        case.conversationHistory.append(message)
        case.updatedAt = datetime.utcnow().isoformat()
        
        if self.use_firestore:
            doc_ref = self.db.collection("cases").document(case_id)
            doc_ref.update({
                "conversationHistory": firestore.ArrayUnion([message]),
                "updatedAt": case.updatedAt
            })
        else:
            mock_cases_db[case_id] = case
            
        return case

    def update_status(self, case_id: str, to_status: CaseStatus, actor: str = "guest", actor_id: Optional[str] = None) -> Optional[CaseDocument]:
        case = self.get_case(case_id)
        if not case:
            return None
            
        from_status = case.status
        case.status = to_status
        
        # Log transition in Audit History
        audit_entry = AuditLogEntry(
            event=f"STATE_TRANSITION_{to_status.value}",
            fromStatus=from_status.value,
            toStatus=to_status.value,
            actor=actor,
            actorId=actor_id or case.userId or case.guestSessionId
        )
        case.auditLog.append(audit_entry)
        case.updatedAt = datetime.utcnow().isoformat()
        
        if self.use_firestore:
            doc_ref = self.db.collection("cases").document(case_id)
            doc_ref.update({
                "status": to_status.value,
                "auditLog": firestore.ArrayUnion([audit_entry.dict()]),
                "updatedAt": case.updatedAt
            })
        else:
            mock_cases_db[case_id] = case
            
        return case

    def claim_guest_case(self, case_id: str, user_id: str, guest_session_id: str) -> Optional[CaseDocument]:
        case = self.get_case(case_id)
        if not case:
            return None
            
        if case.userId is not None:
            raise ValueError("Case is already claimed by an authenticated user.")
            
        if case.guestSessionId != guest_session_id:
            raise ValueError("Guest session mismatch. Cannot claim this case.")
            
        case.userId = user_id
        case.guestSessionId = None
        
        audit_entry = AuditLogEntry(
            event="CASE_CLAIMED",
            fromStatus=case.status.value,
            toStatus=case.status.value,
            actor="user",
            actorId=user_id
        )
        case.auditLog.append(audit_entry)
        case.updatedAt = datetime.utcnow().isoformat()
        
        if self.use_firestore:
            doc_ref = self.db.collection("cases").document(case_id)
            doc_ref.update({
                "userId": user_id,
                "guestSessionId": None,
                "auditLog": firestore.ArrayUnion([audit_entry.dict()]),
                "updatedAt": case.updatedAt
            })
        else:
            mock_cases_db[case_id] = case
            
        return case

    def list_user_cases(self, user_id: str) -> List[CaseDocument]:
        if self.use_firestore:
            docs = self.db.collection("cases").where("userId", "==", user_id).stream()
            results = []
            for doc in docs:
                results.append(CaseDocument(**doc.to_dict()))
            results.sort(key=lambda x: x.createdAt, reverse=True)
            return results
        else:
            user_cases = [c for c in mock_cases_db.values() if c.userId == user_id]
            user_cases.sort(key=lambda x: x.createdAt, reverse=True)
            return user_cases

    def list_guest_cases(self, guest_session_id: str) -> List[CaseDocument]:
        if self.use_firestore:
            docs = self.db.collection("cases").where("guestSessionId", "==", guest_session_id).where("userId", "==", None).stream()
            results = []
            for doc in docs:
                results.append(CaseDocument(**doc.to_dict()))
            results.sort(key=lambda x: x.createdAt, reverse=True)
            return results
        else:
            guest_cases = [c for c in mock_cases_db.values() if c.guestSessionId == guest_session_id and c.userId is None]
            guest_cases.sort(key=lambda x: x.createdAt, reverse=True)
            return guest_cases
