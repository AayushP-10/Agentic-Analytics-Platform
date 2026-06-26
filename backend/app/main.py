from fastapi import FastAPI

from backend.app.api.intake import router as intake_router

APP_NAME = "Agentic Analytics Platform"
APP_VERSION = "0.1.0"

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Local-first scaffold for an agentic analytics and data operations platform.",
)

app.include_router(intake_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "name": APP_NAME,
        "version": APP_VERSION,
    }
