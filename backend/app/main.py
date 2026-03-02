from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base, SessionLocal
from app.seed import seed_database

# Import routers
from app.routes import auth, models, incidents, policies, audit, alerts, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup: Create tables and seed database
    print("Starting up...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created")
    
    # Seed database
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    
    yield
    
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="AI Safety & Governance Dashboard API",
    description="Backend API for AI Safety & Governance Dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker healthcheck"""
    return {"status": "healthy"}


@app.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    return {"status": "healthy", "service": "ai-safety-governance-api"}


# Include routers
app.include_router(auth.router)
app.include_router(models.router)
app.include_router(incidents.router)
app.include_router(policies.router)
app.include_router(audit.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Safety & Governance Dashboard API",
        "version": "1.0.0",
        "docs": "/docs"
    }
