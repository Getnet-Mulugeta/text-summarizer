"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import (
    authRoute,
    userRoute,
    messagesRoute,
    summarizeRoute,
    historyRoute,
    profileRoute
)
from app.database import client

# Initialize FastAPI app
app = FastAPI(
    title="Text Summarizer API",
    version="1.0.0",
    description="FastAPI backend for Text Summarizer with MongoDB integration"
)

# CORS middleware

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database connection lifecycle
@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection on startup"""
    print("Connected to MongoDB")


@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown"""
    if client:
        client.close()
        print("Disconnected from MongoDB")


# Include routers
app.include_router(authRoute.router)
app.include_router(userRoute.router)
app.include_router(messagesRoute.router)
app.include_router(summarizeRoute.router)
app.include_router(historyRoute.router)
app.include_router(profileRoute.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Text Summarizer API",
        "status": "running",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
