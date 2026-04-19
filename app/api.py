from fastapi import APIRouter

from app.modules.autenticacion_seguridad.router import router as auth_router
from app.modules.gestion_clientes.router import router as clientes_router
from app.modules.gestion_incidentes_atencion.router import router as incidentes_router
from app.modules.seguimiento_monitoreo_servicio.router import router as seguimiento_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(clientes_router)
api_router.include_router(incidentes_router)
api_router.include_router(seguimiento_router)


@api_router.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "autoassist-ai-backend",
    }