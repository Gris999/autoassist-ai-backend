from sqlalchemy.orm import Session

from app.modules.gestion_clientes.repository import get_cliente_by_usuario_id
from app.modules.gestion_incidentes_atencion.repository import (
    create_incidente,
    get_estado_servicio_by_nombre,
    get_incidente_by_id_and_cliente,
    get_incidentes_by_cliente_id,
    get_prioridad_by_nombre,
    get_tipo_incidente_by_id,
    get_vehiculo_by_id_and_cliente,
)
from app.modules.gestion_incidentes_atencion.schemas import (
    IncidenteCreateRequest,
    IncidenteDetalleResponse,
    IncidenteResponse,
)


def report_incidente_service(
    db: Session,
    current_user,
    payload: IncidenteCreateRequest,
) -> IncidenteResponse:
    cliente = get_cliente_by_usuario_id(db, current_user.id_usuario)
    if not cliente:
        raise ValueError("El usuario autenticado no tiene perfil de cliente.")

    vehiculo = get_vehiculo_by_id_and_cliente(db, payload.id_vehiculo, cliente.id_cliente)
    if not vehiculo:
        raise ValueError("El vehículo no existe o no pertenece al cliente autenticado.")

    tipo_incidente = get_tipo_incidente_by_id(db, payload.id_tipo_incidente)
    if not tipo_incidente:
        raise ValueError("El tipo de incidente seleccionado no existe.")

    prioridad = get_prioridad_by_nombre(db, "MEDIA")
    if not prioridad:
        raise ValueError("No existe la prioridad MEDIA en la base de datos.")

    estado_reportado = get_estado_servicio_by_nombre(db, "REPORTADO")
    if not estado_reportado:
        raise ValueError("No existe el estado REPORTADO en la base de datos.")

    try:
        incidente = create_incidente(
            db,
            id_cliente=cliente.id_cliente,
            id_vehiculo=payload.id_vehiculo,
            id_tipo_incidente=payload.id_tipo_incidente,
            id_prioridad=prioridad.id_prioridad,
            id_estado_servicio_actual=estado_reportado.id_estado_servicio,
            titulo=payload.titulo,
            descripcion_texto=payload.descripcion_texto,
            direccion_referencia=payload.direccion_referencia,
            latitud=payload.latitud,
            longitud=payload.longitud,
        )

        db.commit()
        db.refresh(incidente)

        return IncidenteResponse.model_validate(incidente)
    except Exception:
        db.rollback()
        raise


def get_mis_incidentes_service(
    db: Session,
    current_user,
) -> list[IncidenteResponse]:
    cliente = get_cliente_by_usuario_id(db, current_user.id_usuario)
    if not cliente:
        raise ValueError("El usuario autenticado no tiene perfil de cliente.")

    incidentes = get_incidentes_by_cliente_id(db, cliente.id_cliente)
    return [IncidenteResponse.model_validate(i) for i in incidentes]


def get_incidente_detalle_service(
    db: Session,
    current_user,
    id_incidente: int,
) -> IncidenteDetalleResponse:
    cliente = get_cliente_by_usuario_id(db, current_user.id_usuario)
    if not cliente:
        raise ValueError("El usuario autenticado no tiene perfil de cliente.")

    incidente = get_incidente_by_id_and_cliente(db, id_incidente, cliente.id_cliente)
    if not incidente:
        raise ValueError("El incidente no existe o no pertenece al cliente autenticado.")

    return IncidenteDetalleResponse(
        id_incidente=incidente.id_incidente,
        titulo=incidente.titulo,
        descripcion_texto=incidente.descripcion_texto,
        direccion_referencia=incidente.direccion_referencia,
        latitud=incidente.latitud,
        longitud=incidente.longitud,
        fecha_reporte=incidente.fecha_reporte,
        id_vehiculo=incidente.id_vehiculo,
        id_tipo_incidente=incidente.id_tipo_incidente,
        tipo_incidente=incidente.tipo_incidente.nombre,
        id_prioridad=incidente.id_prioridad,
        prioridad=incidente.prioridad.nombre,
        id_estado_servicio_actual=incidente.id_estado_servicio_actual,
        estado_servicio_actual=incidente.estado_servicio_actual.nombre,
        clasificacion_ia=incidente.clasificacion_ia,
        confianza_clasificacion=incidente.confianza_clasificacion,
        resumen_ia=incidente.resumen_ia,
        requiere_mas_info=incidente.requiere_mas_info,
    )