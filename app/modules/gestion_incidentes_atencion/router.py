from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.modules.autenticacion_seguridad.models import Usuario
from app.modules.autenticacion_seguridad.permissions import require_roles
from app.modules.gestion_incidentes_atencion.schemas import (
    IncidenteCreateRequest,
    IncidenteResponse,
    IncidenteDisponibleResponse,
    ResponderSolicitudAtencionRequest,
    RespuestaSolicitudAtencionResponse,
    SolicitudAtencionDetalleResponse,
)
from app.modules.gestion_incidentes_atencion.service import (
    get_mis_incidentes_service,
    get_solicitud_atencion_detalle_service,
    report_incidente_service,
    get_incidentes_disponibles_service,
    responder_solicitud_atencion_service,
)

router = APIRouter(prefix="/incidentes", tags=["Gestión Incidentes y Atención"])


@router.post(
    "",
    response_model=IncidenteResponse,
    status_code=status.HTTP_201_CREATED,
)
def report_incidente(
    payload: IncidenteCreateRequest,
    current_user: Usuario = Depends(require_roles("CLIENTE")),
    db: Session = Depends(get_db),
):
    try:
        return report_incidente_service(db, current_user, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/mis",
    response_model=list[IncidenteResponse],
    status_code=status.HTTP_200_OK,
)
def get_mis_incidentes(
    current_user: Usuario = Depends(require_roles("CLIENTE")),
    db: Session = Depends(get_db),
):
    try:
        return get_mis_incidentes_service(db, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    

@router.get(
    "/disponibles",
    response_model=list[IncidenteDisponibleResponse],
    status_code=status.HTTP_200_OK,
)
def get_incidentes_disponibles(
    current_user: Usuario = Depends(require_roles("TALLER")),
    db: Session = Depends(get_db),
):
    try:
        return get_incidentes_disponibles_service(db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/taller/solicitudes-atencion/{id_solicitud_taller}",
    response_model=SolicitudAtencionDetalleResponse,
    status_code=status.HTTP_200_OK,
)
def get_solicitud_atencion_detalle(
    id_solicitud_taller: int,
    current_user: Usuario = Depends(require_roles("TALLER")),
    db: Session = Depends(get_db),
):
    try:
        return get_solicitud_atencion_detalle_service(db, current_user, id_solicitud_taller)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/taller/solicitudes-atencion/{id_solicitud_taller}/respuesta",
    response_model=RespuestaSolicitudAtencionResponse,
    status_code=status.HTTP_200_OK,
)
def responder_solicitud_atencion(
    id_solicitud_taller: int,
    payload: ResponderSolicitudAtencionRequest,
    current_user: Usuario = Depends(require_roles("TALLER")),
    db: Session = Depends(get_db),
):
    try:
        return responder_solicitud_atencion_service(
            db,
            current_user,
            id_solicitud_taller,
            payload,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
