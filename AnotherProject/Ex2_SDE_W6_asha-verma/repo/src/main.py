import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.routes.projects import router as projects_router
from src.api.routes.tasks import router as tasks_router
from src.db.config import get_settings

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger("projectflow")

app = FastAPI(
    title="ProjectFlow Project Management API",
    version="1.0.0-week6",
    description="Week 6 capstone API for projects, members, tasks and project health.",
)
app.include_router(projects_router)
app.include_router(tasks_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
