from fastapi import FastAPI

from app.api.routes.events import router as events_router
from app.api.routes.health import router as health_router
from app.core.config import settings


app = FastAPI(
    title=f"{settings.app_name} API",
    description=(
        "Plateforme de détection, d'investigation "
        "et de réponse aux incidents de sécurité"
    ),
    version="0.1.0",
    debug=settings.debug,
)

app.include_router(health_router)
app.include_router(events_router)


@app.get("/", tags=["Application"])
def root() -> dict[str, str]:
    return {
        "application": settings.app_name,
        "environment": settings.app_env,
        "status": "running",
    }
