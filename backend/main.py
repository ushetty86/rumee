"""
Rumee Backend - FastAPI Application
AI-powered assistant for notes, meetings, reminders, and data linking
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from config.database import connect_db, close_db
from config.settings import settings
from routes import notes, people, meetings, reminders, auth, summary, knowledge_graph
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    logger.info("Starting Rumee Backend...")
    await connect_db()
    logger.info("Connected to MongoDB")
    yield
    # Shutdown
    logger.info("Shutting down Rumee Backend...")
    await close_db()
    logger.info("Closed MongoDB connection")


# Initialize FastAPI app
app = FastAPI(
    title="Rumee API",
    description="AI-powered assistant for notes, meetings, reminders, and data linking",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "rumee-backend"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Rumee API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(notes.router, prefix="/api/notes", tags=["Notes"])
app.include_router(people.router, prefix="/api/people", tags=["People"])
app.include_router(meetings.router, prefix="/api/meetings", tags=["Meetings"])
app.include_router(reminders.router, prefix="/api/reminders", tags=["Reminders"])
app.include_router(summary.router, prefix="/api/summary", tags=["Summary"])
app.include_router(knowledge_graph.router, prefix="/api/knowledge-graph", tags=["Knowledge Graph"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
