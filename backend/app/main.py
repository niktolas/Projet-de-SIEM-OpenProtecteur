from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes.alerts import router as alerts_router
from app.api.routes.events import router as events_router
from app.api.routes.health import router as health_router
from app.core.config import settings

from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router

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
app.include_router(alerts_router)

app.include_router(auth_router)
app.include_router(users_router)

@app.exception_handler(SQLAlchemyError)
def sqlalchemy_exception_handler(
    request: Request,
    exception: SQLAlchemyError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "Database operation unavailable",
        },
    )


@app.get("/", tags=["Application"])
def root() -> dict[str, str]:
    return {
        "application": settings.app_name,
        "environment": settings.app_env,
        "status": "running",
    }
