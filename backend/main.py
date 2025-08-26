"""
Smart Payment Optimization Engine - Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
import logging
from dotenv import load_dotenv, find_dotenv

# Load environment variables (search up the tree for .env)
load_dotenv(find_dotenv())

# Import routers
from api import optimization
from database.database import init_db, seed_demo_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Resolve absolute paths relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and seed data on startup"""
    logger.info("Starting Smart Payment Engine...")
    init_db()
    seed_demo_data()
    logger.info("Database initialized and seeded")
    yield
    logger.info("Shutting down Smart Payment Engine...")

# Create FastAPI app
app = FastAPI(
    title="Smart Payment Optimization Engine",
    description="AI-powered credit card optimization for maximum rewards",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(optimization.router, prefix="/api", tags=["optimization"])

# Serve frontend files
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'))

@app.get("/app.js")
async def serve_app_js():
    return FileResponse(os.path.join(FRONTEND_DIR, 'app.js'))

@app.get("/styles.css")
async def serve_styles_css():
    return FileResponse(os.path.join(FRONTEND_DIR, 'styles.css'))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Smart Payment Engine",
        "api_keys_configured": {
            "claude": bool(os.getenv("CLAUDE_API_KEY") and os.getenv("CLAUDE_API_KEY") != "your_claude_api_key_here"),
            "brave": bool(os.getenv("BRAVE_SEARCH_API_KEY") and os.getenv("BRAVE_SEARCH_API_KEY") != "your_brave_api_key_here")
        }
    }

# Demo mode exception handler for safe failures
@app.exception_handler(Exception)
async def demo_exception_handler(request, exc):
    """Graceful error handling for demo"""
    logger.error(f"Demo error: {exc}")
    return {
        "error": "Demo mode: showing sample recommendation",
        "recommendation": {
            "best_overall": {
                "name": "Chase Sapphire Preferred",
                "reward_amount": 0.47,
                "reward_rate": "3x points on dining",
                "annual_fee": 95,
                "ai_reasoning": "Best dining rewards card (demo fallback)"
            }
        },
        "note": "This would normally show live market data"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RELOAD", "True").lower() == "true"
    )
