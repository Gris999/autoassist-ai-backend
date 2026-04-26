from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.core.db.session import SessionLocal, get_db
from app.modules.autenticacion_seguridad.models import Usuario
from app.modules.autenticacion_seguridad.permissions import require_roles
from app.modules.seguimiento_monitoreo_servicio.realtime import incident_location_manager
from app.shared.dependencies.auth import get_current_user_from_token
from app.modules.seguimiento_monitoreo_servicio.schemas import (
    ActualizarUbicacionActualRequest,
    AsignacionAuxilioDetalleResponse,
    ClienteIncidenteListResponse,
    EstadoServicioDetalleResponse,
    IncidenteHistorialDetailResponse,
    IncidenteHistorialListResponse,
    NotificacionDetailResponse,
    NotificacionLeidaResponse,
    NotificacionListResponse,
    UbicacionActualTecnicoResponse,
)
from app.modules.seguimiento_monitoreo_servicio.service import (
    actualizar_ubicacion_actual_tecnico_service,
    consultar_asignacion_auxilio_service,
    get_estado_servicio_service,
    listar_incidentes_historial_service,
    listar_incidentes_cliente_service,
    listar_notificaciones_service,
    marcar_notificacion_leida_service,
    obtener_historial_incidente_service,
    obtener_notificacion_service,
    validar_acceso_incidente_seguimiento_service,
)

router = APIRouter(
    prefix="/seguimiento",
    tags=["Seguimiento y Monitoreo del Servicio"],
)


@router.websocket("/ws/incidentes/{id_incidente}")
async def websocket_seguimiento_incidente(
    websocket: WebSocket,
    id_incidente: int,
    token: str = Query(...),
):
    db = SessionLocal()
    try:
        current_user = get_current_user_from_token(token, db)
        incidente = validar_acceso_incidente_seguimiento_service(db, current_user, id_incidente)
    except HTTPException:
        await websocket.close(code=1008)
        db.close()
        return
    except ValueError:
        await websocket.close(code=1008)
        db.close()
        return

    await incident_location_manager.connect(id_incidente, websocket)
    try:
        await incident_location_manager.send_personal_message(
            websocket,
            {
                "type": "conexion_establecida",
                "payload": {
                    "id_incidente": incidente.id_incidente,
                    "estado_servicio_actual": incidente.estado_servicio_actual.nombre,
                    "latitud": float(incidente.latitud) if incidente.latitud is not None else None,
                    "longitud": float(incidente.longitud) if incidente.longitud is not None else None,
                },
            },
        )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        incident_location_manager.disconnect(id_incidente, websocket)
    finally:
        db.close()


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


@router.patch(
    "/incidentes/{id_incidente}/ubicacion-actual",
    response_model=UbicacionActualTecnicoResponse,
    status_code=status.HTTP_200_OK,
)
def actualizar_ubicacion_actual_tecnico(
    id_incidente: int,
    payload: ActualizarUbicacionActualRequest,
    current_user: Usuario = Depends(require_roles("TECNICO")),
    db: Session = Depends(get_db),
):
    try:
        return actualizar_ubicacion_actual_tecnico_service(
            db,
            current_user,
            id_incidente,
            payload,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
