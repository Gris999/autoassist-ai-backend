from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.modules.autenticacion_seguridad.models import Usuario
from app.modules.autenticacion_seguridad.permissions import require_roles
from app.modules.seguimiento_monitoreo_servicio.schemas import (
    EstadoServicioDetalleResponse,
)
from app.modules.seguimiento_monitoreo_servicio.service import (
    get_estado_servicio_service,
)

router = APIRouter(
    prefix="/seguimiento",
    tags=["Seguimiento y Monitoreo del Servicio"],
)


@router.get(
    "/estado/{id_incidente}",
    response_model=EstadoServicioDetalleResponse,
    status_code=status.HTTP_200_OK,
)
def get_estado_servicio(
    id_incidente: int,
    current_user: Usuario = Depends(require_roles("CLIENTE")),
    db: Session = Depends(get_db),
):
    try:
        return get_estado_servicio_service(db, current_user, id_incidente)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )