from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.seed import seed_plants
from app.routers import auth, plants, dashboard, stores, disease, plant_assistant

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    # Ensure seed starter plants are populated safely
    seed_plants()
    # Initialize ML model safely in background
    from app.services.disease_model import disease_model_service
    disease_model_service.initialize_model()
    yield

app = FastAPI(
    title="CropShield AI API",
    version="1.2.0",
    description="Backend API for CropShield AI: Authentication, Plantopedia, Conversational AI Plant Assistant, User Dashboard, Demo Stores, and Plant Disease Detection.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(plants.router)
app.include_router(plant_assistant.router)
app.include_router(dashboard.router)
app.include_router(stores.router)
app.include_router(disease.router)

# Direct alias matching prompt specification GET /api/disease-history
@app.get("/api/disease-history", tags=["Disease Detection"])
def get_disease_history_alias(
    limit: int = 20,
    offset: int = 0,
    current_user = Depends(auth.get_current_user),
    db = Depends(disease.get_db)
):
    return disease.get_user_detection_history(limit=limit, offset=offset, current_user=current_user, db=db)

@app.get("/")
def root():
    return {
        "app": "CropShield AI API",
        "phase": "Phase 1 Implementation",
        "docs_url": "/docs",
        "status": "healthy"
    }
