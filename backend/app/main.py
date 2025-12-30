# backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from .api import router
from .database import Base, engine
import os
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Middleware to log request time
class TimingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    process_time = time.time() - start_time
                    logger.info(f"{scope['method']} {scope['path']} - {process_time:.3f}s")
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)

def create_app():
    app = FastAPI(
        title="ATS Resume Matcher",
        description="AI-powered ATS resume analysis and optimization",
        version="1.0.0"
    )
    
    # Add timing middleware
    app.add_middleware(TimingMiddleware)
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Create tables on startup
    @app.on_event("startup")
    async def startup_event():
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created successfully")
        except Exception as e:
            logger.error(f"❌ Error creating database tables: {str(e)}")
    
    # Include API router FIRST (before static files)
    app.include_router(router, prefix="/api")
    
    # Health check endpoint
    @app.get("/health")
    def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "ATS Resume Matcher"}
    
    # Root endpoint - serve index.html
    @app.get("/")
    async def read_root():
        frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
        index_file = os.path.join(frontend_dir, "index.html")
        
        if os.path.exists(index_file):
            return FileResponse(index_file)
        else:
            return HTMLResponse(content="""
            <html>
                <head><title>Error</title></head>
                <body>
                    <h1>Frontend Not Found</h1>
                    <p>Frontend directory: {}</p>
                    <p>Looking for: {}</p>
                </body>
            </html>
            """.format(frontend_dir, index_file), status_code=404)
    
    # Serve static files (CSS, JS, etc.)
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
    if os.path.exists(frontend_dir):
        app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
        logger.info(f"✅ Frontend served from: {frontend_dir}")
    else:
        logger.warning(f"⚠️ Frontend directory not found: {frontend_dir}")
    
    return app

app = create_app()

# Run locally with:
# uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

