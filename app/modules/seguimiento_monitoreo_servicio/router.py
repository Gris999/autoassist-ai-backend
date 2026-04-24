from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.modules.autenticacion_seguridad.models import Usuario
from app.modules.autenticacion_seguridad.permissions import require_roles
from app.modules.seguimiento_monitoreo_servicio.schemas import (
    AsignacionAuxilioDetalleResponse,
    ClienteIncidenteListResponse,
    EstadoServicioDetalleResponse,
)
from app.modules.seguimiento_monitoreo_servicio.service import (
    consultar_asignacion_auxilio_service,
    get_estado_servicio_service,
    listar_incidentes_cliente_service,
)

router = APIRouter(
    prefix="/seguimiento",
    tags=["Seguimiento y Monitoreo del Servicio"],
)


@router.get(
    "/cliente/incidentes",
    response_model=list[ClienteIncidenteListResponse],
    status_code=status.HTTP_200_OK,
)
def listar_incidentes_cliente(
    current_user: Usuario = Depends(require_roles("CLIENTE")),
    db: Session = Depends(get_db),
):
    try:
        return listar_incidentes_cliente_service(db, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/cliente/incidentes/{id_incidente}/asignacion",
    response_model=AsignacionAuxilioDetalleResponse,
    status_code=status.HTTP_200_OK,
)
def consultar_asignacion_auxilio(
    id_incidente: int,
    current_user: Usuario = Depends(require_roles("CLIENTE")),
    db: Session = Depends(get_db),
):
    try:
        return consultar_asignacion_auxilio_service(db, current_user, id_incidente)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
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
