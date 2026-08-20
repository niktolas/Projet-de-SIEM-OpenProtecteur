from fastapi import FastAPI

app = FastAPI(
    title="API OpenProtecteur",
    description="Detection et réponse aux incidents",
    version="0.1.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "application": "OpenProtecteur",
        "status": "running",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
    }
