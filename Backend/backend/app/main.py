# Reload trigger comment
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app import __version__
from app.api.routes import router
from app.utils.config import CORS_ORIGINS, ensure_reports_dir, REPO_ROOT

ensure_reports_dir()

app = FastAPI(
    title="AI Security Code Review Platform",
    description="Static analysis + ML risk scoring for source code security review",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


# Serve compiled frontend assets if they exist
frontend_dist = REPO_ROOT / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/")
    def serve_root():
        return FileResponse(str(frontend_dist / "index.html"))

    @app.get("/{path_name:path}")
    def serve_frontend(path_name: str):
        # Exclude API endpoints and docs
        if path_name.startswith("api") or path_name.startswith("docs") or path_name.startswith("openapi.json"):
            return None
        
        # Check if file exists in dist directory
        file_path = frontend_dist / path_name
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
            
        return FileResponse(str(frontend_dist / "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "service": "AI Security Code Review Platform",
            "version": __version__,
            "docs": "/docs",
            "health": "/health",
        }

