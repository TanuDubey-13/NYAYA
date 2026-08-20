from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.cases import router as cases_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="NYAYA — AI Civic & Legal Action Navigator Backend",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon local development, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(cases_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    """Service health verification endpoint."""
    return {
        "status": "ok",
        "service": "nyaya-backend"
    }
