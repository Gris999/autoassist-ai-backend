from fastapi import FastAPI

from app.api import api_router
from app.core.config.settings import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "AutoAssist AI Backend running"
    }