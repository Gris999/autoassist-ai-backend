from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.modules.autenticacion_seguridad.models import Usuario
from app.modules.autenticacion_seguridad.permissions import require_roles
from app.modules.seguimiento_monitoreo_servicio.schemas import (
    AsignacionAuxilioDetalleResponse,
    ClienteIncidenteListResponse,
    EstadoServicioDetalleResponse,
    IncidenteHistorialDetailResponse,
    IncidenteHistorialListResponse,
    NotificacionDetailResponse,
    NotificacionLeidaResponse,
    NotificacionListResponse,
)
from app.modules.seguimiento_monitoreo_servicio.service import (
    consultar_asignacion_auxilio_service,
    get_estado_servicio_service,
    listar_incidentes_historial_service,
    listar_incidentes_cliente_service,
    listar_notificaciones_service,
    marcar_notificacion_leida_service,
    obtener_historial_incidente_service,
    obtener_notificacion_service,
)

router = APIRouter(
    prefix="/seguimiento",
    tags=["Seguimiento y Monitoreo del Servicio"],
)


@router.get(
    "/incidentes/historial",
    response_model=list[IncidenteHistorialListResponse],
    status_code=status.HTTP_200_OK,
)
def listar_incidentes_historial(
    current_user: Usuario = Depends(
        require_roles("CLIENTE", "TECNICO", "TALLER", "ADMIN")
    ),
    db: Session = Depends(get_db),
):
    try:
        return listar_incidentes_historial_service(db, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/incidentes/{id_incidente}/historial",
    response_model=IncidenteHistorialDetailResponse,
    status_code=status.HTTP_200_OK,
)
def obtener_historial_incidente(
    id_incidente: int,
    current_user: Usuario = Depends(
        require_roles("CLIENTE", "TECNICO", "TALLER", "ADMIN")
    ),
    db: Session = Depends(get_db),
):
    try:
        return obtener_historial_incidente_service(db, current_user, id_incidente)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/notificaciones",
    response_model=list[NotificacionListResponse],
    status_code=status.HTTP_200_OK,
)
def listar_notificaciones(
    current_user: Usuario = Depends(require_roles("CLIENTE", "TALLER", "TECNICO")),
    db: Session = Depends(get_db),
):
    try:
        return listar_notificaciones_service(db, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/notificaciones/{id_notificacion}",
    response_model=NotificacionDetailResponse,
    status_code=status.HTTP_200_OK,
)
def obtener_notificacion(
    id_notificacion: int,
    current_user: Usuario = Depends(require_roles("CLIENTE", "TALLER", "TECNICO")),
    db: Session = Depends(get_db),
):
    try:
        return obtener_notificacion_service(db, current_user, id_notificacion)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch(
    "/notificaciones/{id_notificacion}/leer",
    response_model=NotificacionLeidaResponse,
    status_code=status.HTTP_200_OK,
)
def marcar_notificacion_leida(
    id_notificacion: int,
    current_user: Usuario = Depends(require_roles("CLIENTE", "TALLER", "TECNICO")),
    db: Session = Depends(get_db),
):
    try:
        return marcar_notificacion_leida_service(db, current_user, id_notificacion)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
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
