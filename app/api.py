from fastapi import APIRouter

from app.modules.autenticacion_seguridad.router import router as auth_router
from app.modules.gestion_clientes.router import router as clientes_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(clientes_router)


@api_router.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "autoassist-ai-backend",
    }