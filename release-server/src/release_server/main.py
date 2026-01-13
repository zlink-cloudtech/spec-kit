from fastapi import FastAPI
from contextlib import asynccontextmanager
from release_server.config import get_settings
from release_server.router import router
from release_server.logger import configure_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    configure_logging()
    settings = get_settings()
    # Ensure storage path exists on startup? storage.py __init__ does it.
    yield
    # Shutdown logic

def create_app() -> FastAPI:
    app = FastAPI(
        title="Spec Kit Release Server",
        version="0.1.0",
        lifespan=lifespan
    )
    
    app.include_router(router)
    
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
        
    return app

app = create_app()
