from sqlalchemy.orm import Session

from app.modules.gestion_clientes.repository import get_cliente_by_usuario_id
from app.modules.gestion_operativa_taller_tecnico.repository import (
    get_taller_by_usuario_id,
    get_tecnico_by_usuario_id,
)
from app.modules.seguimiento_monitoreo_servicio.models import Notificacion
from app.modules.seguimiento_monitoreo_servicio.schemas import (
    AsignacionAuxilioDetalleResponse,
    ClienteIncidenteListResponse,
    EstadoServicioDetalleResponse,
    HistorialIncidenteEventoResponse,
    IncidenteHistorialDetailResponse,
    IncidenteHistorialListResponse,
    NotificacionCreateRequest,
    NotificacionDetailResponse,
    NotificacionLeidaResponse,
    NotificacionListResponse,
    TallerAsignadoResponse,
    TecnicoAsignadoResponse,
    UnidadMovilAsignadaResponse,
)
from app.modules.seguimiento_monitoreo_servicio.repository import (
    create_notificacion,
    get_incidente_asignacion_by_id_and_cliente,
    get_incidente_historial_by_id,
    get_incidentes_by_cliente_id,
    get_incidentes_historial_all,
    get_incidentes_historial_by_taller_id,
    get_incidentes_historial_by_tecnico_id,
    get_incidente_by_id,
    get_notificacion_by_id_and_usuario,
    get_notificaciones_by_usuario_id,
    get_roles_by_usuario_id,
    get_usuario_by_id,
    update_notificacion_leido,
)
from app.modules.gestion_incidentes_atencion.repository import get_incidente_by_id_and_cliente


def _get_cliente_autenticado(db: Session, current_user):
    cliente = get_cliente_by_usuario_id(db, current_user.id_usuario)
    if not cliente:
        raise ValueError("El usuario autenticado no tiene perfil de cliente.")
    return cliente


def _get_taller_autenticado(db: Session, current_user):
    taller = get_taller_by_usuario_id(db, current_user.id_usuario)
    if not taller:
        raise ValueError("El usuario autenticado no tiene perfil de taller.")
    return taller


def _get_tecnico_autenticado(db: Session, current_user):
    tecnico = get_tecnico_by_usuario_id(db, current_user.id_usuario)
    if not tecnico:
        raise ValueError("El usuario autenticado no tiene perfil de tecnico.")
    if not tecnico.estado:
        raise ValueError("El tecnico no se encuentra habilitado en la plataforma.")
    return tecnico


def _resolver_rol_historial_service(db: Session, current_user) -> str:
    roles = set(get_roles_by_usuario_id(db, current_user.id_usuario))
    if "ADMIN" in roles:
        return "ADMIN"
    if "TALLER" in roles:
        return "TALLER"
    if "TECNICO" in roles:
        return "TECNICO"
    if "CLIENTE" in roles:
        return "CLIENTE"
    raise ValueError("El usuario autenticado no tiene un rol valido para consultar historial.")


def _to_notificacion_list_response(notificacion: Notificacion) -> NotificacionListResponse:
    return NotificacionListResponse(
        id_notificacion=notificacion.id_notificacion,
        id_incidente=notificacion.id_incidente,
        titulo=notificacion.titulo,
        mensaje=notificacion.mensaje,
        tipo_notificacion=notificacion.tipo_notificacion,
        leido=notificacion.leido,
        fecha_envio=notificacion.fecha_envio,
    )


def _to_notificacion_detail_response(notificacion: Notificacion) -> NotificacionDetailResponse:
    return NotificacionDetailResponse(
        id_notificacion=notificacion.id_notificacion,
        id_usuario=notificacion.id_usuario,
        id_incidente=notificacion.id_incidente,
        titulo=notificacion.titulo,
        mensaje=notificacion.mensaje,
        tipo_notificacion=notificacion.tipo_notificacion,
        leido=notificacion.leido,
        fecha_envio=notificacion.fecha_envio,
    )


def crear_notificacion_service(
    db: Session,
    payload: NotificacionCreateRequest,
) -> NotificacionDetailResponse:
    usuario = get_usuario_by_id(db, payload.id_usuario)
    if not usuario:
        raise ValueError("El destinatario de la notificacion no existe.")

    if payload.id_incidente is not None:
        incidente = get_incidente_by_id(db, payload.id_incidente)
        if not incidente:
            raise ValueError("El incidente asociado a la notificacion no existe.")

    notificacion = create_notificacion(
        db,
        id_usuario=payload.id_usuario,
        id_incidente=payload.id_incidente,
        titulo=payload.titulo,
        mensaje=payload.mensaje,
        tipo_notificacion=payload.tipo_notificacion,
    )
    return _to_notificacion_detail_response(notificacion)


def listar_notificaciones_service(
    db: Session,
    current_user,
) -> list[NotificacionListResponse]:
    notificaciones = get_notificaciones_by_usuario_id(db, current_user.id_usuario)
    return [_to_notificacion_list_response(notificacion) for notificacion in notificaciones]


def obtener_notificacion_service(
    db: Session,
    current_user,
    id_notificacion: int,
) -> NotificacionDetailResponse:
    notificacion = get_notificacion_by_id_and_usuario(
        db,
        id_notificacion=id_notificacion,
        id_usuario=current_user.id_usuario,
    )
    if not notificacion:
        raise ValueError("La notificacion no existe o no pertenece al usuario autenticado.")
    return _to_notificacion_detail_response(notificacion)


def marcar_notificacion_leida_service(
    db: Session,
    current_user,
    id_notificacion: int,
) -> NotificacionLeidaResponse:
    notificacion = get_notificacion_by_id_and_usuario(
        db,
        id_notificacion=id_notificacion,
        id_usuario=current_user.id_usuario,
    )
    if not notificacion:
        raise ValueError("La notificacion no existe o no pertenece al usuario autenticado.")

    update_notificacion_leido(db, notificacion, leido=True)
    return NotificacionLeidaResponse(
        id_notificacion=notificacion.id_notificacion,
        leido=notificacion.leido,
        mensaje="Notificacion marcada como leida.",
    )


def _to_incidente_historial_list_response(incidente) -> IncidenteHistorialListResponse:
    return IncidenteHistorialListResponse(
        id_incidente=incidente.id_incidente,
        titulo=incidente.titulo,
        fecha_reporte=incidente.fecha_reporte,
        tipo_incidente=incidente.tipo_incidente.nombre,
        id_estado_servicio_actual=incidente.id_estado_servicio_actual,
        estado_servicio_actual=incidente.estado_servicio_actual.nombre,
    )


def _to_actor_nombre(usuario_actor) -> str | None:
    if not usuario_actor:
        return None
    return f"{usuario_actor.nombres} {usuario_actor.apellidos}"


def _construir_eventos_historial(incidente) -> list[HistorialIncidenteEventoResponse]:
    eventos: list[HistorialIncidenteEventoResponse] = []

    solicitud_aceptada = next(
        (
            solicitud
            for solicitud in incidente.solicitudes_taller
            if solicitud.estado_solicitud == "ACEPTADA"
        ),
        None,
    )
    if solicitud_aceptada and solicitud_aceptada.taller:
        eventos.append(
            HistorialIncidenteEventoResponse(
                fecha_hora=solicitud_aceptada.fecha_respuesta or solicitud_aceptada.fecha_envio,
                tipo_evento="SOLICITUD_TALLER",
                detalle="Solicitud de atencion aceptada por el taller.",
                estado_solicitud=solicitud_aceptada.estado_solicitud,
                id_taller=solicitud_aceptada.id_taller,
                nombre_taller=solicitud_aceptada.taller.nombre_taller,
            )
        )

    asignacion = incidente.asignacion_servicio
    if asignacion:
        nombre_tecnico = None
        if asignacion.tecnico and asignacion.tecnico.usuario:
            nombre_tecnico = (
                f"{asignacion.tecnico.usuario.nombres} "
                f"{asignacion.tecnico.usuario.apellidos}"
            )

        eventos.append(
            HistorialIncidenteEventoResponse(
                fecha_hora=asignacion.fecha_asignacion,
                tipo_evento="ASIGNACION_SERVICIO",
                detalle=asignacion.observaciones,
                id_taller=asignacion.id_taller,
                nombre_taller=asignacion.taller.nombre_taller if asignacion.taller else None,
                id_tecnico=asignacion.id_tecnico,
                nombre_tecnico=nombre_tecnico,
                id_unidad_movil=asignacion.id_unidad_movil,
                placa_unidad_movil=(
                    asignacion.unidad_movil.placa if asignacion.unidad_movil else None
                ),
            )
        )

    for historial in incidente.historial:
        eventos.append(
            HistorialIncidenteEventoResponse(
                fecha_hora=historial.fecha_hora,
                tipo_evento="CAMBIO_ESTADO",
                actor=_to_actor_nombre(historial.usuario_actor),
                detalle=historial.detalle,
                estado_anterior=(
                    historial.estado_anterior.nombre if historial.estado_anterior else None
                ),
                estado_nuevo=historial.estado_nuevo.nombre,
            )
        )

    eventos.sort(key=lambda evento: evento.fecha_hora)
    return eventos


def _validar_acceso_historial_incidente(db: Session, current_user, incidente) -> None:
    rol = _resolver_rol_historial_service(db, current_user)
    if rol == "ADMIN":
        return

    if rol == "CLIENTE":
        cliente = _get_cliente_autenticado(db, current_user)
        if incidente.id_cliente != cliente.id_cliente:
            raise ValueError("El incidente no esta disponible para el cliente autenticado.")
        return

    if rol == "TECNICO":
        tecnico = _get_tecnico_autenticado(db, current_user)
        if not incidente.asignacion_servicio or incidente.asignacion_servicio.id_tecnico != tecnico.id_tecnico:
            raise ValueError("El incidente no esta disponible para el tecnico autenticado.")
        return

    taller = _get_taller_autenticado(db, current_user)
    asignacion = incidente.asignacion_servicio
    if asignacion and asignacion.id_taller == taller.id_taller:
        return

    solicitud_aceptada = next(
        (
            solicitud
            for solicitud in incidente.solicitudes_taller
            if solicitud.id_taller == taller.id_taller and solicitud.estado_solicitud == "ACEPTADA"
        ),
        None,
    )
    if not solicitud_aceptada:
        raise ValueError("El incidente no esta disponible para el taller autenticado.")


def listar_incidentes_historial_service(
    db: Session,
    current_user,
) -> list[IncidenteHistorialListResponse]:
    rol = _resolver_rol_historial_service(db, current_user)

    if rol == "ADMIN":
        incidentes = get_incidentes_historial_all(db)
    elif rol == "CLIENTE":
        cliente = _get_cliente_autenticado(db, current_user)
        incidentes = get_incidentes_by_cliente_id(db, cliente.id_cliente)
    elif rol == "TECNICO":
        tecnico = _get_tecnico_autenticado(db, current_user)
        incidentes = get_incidentes_historial_by_tecnico_id(db, tecnico.id_tecnico)
    else:
        taller = _get_taller_autenticado(db, current_user)
        incidentes = get_incidentes_historial_by_taller_id(db, taller.id_taller)

    return [_to_incidente_historial_list_response(incidente) for incidente in incidentes]


def obtener_historial_incidente_service(
    db: Session,
    current_user,
    id_incidente: int,
) -> IncidenteHistorialDetailResponse:
    incidente = get_incidente_historial_by_id(db, id_incidente)
    if not incidente:
        raise ValueError("El incidente especificado no existe.")

    _validar_acceso_historial_incidente(db, current_user, incidente)
    eventos = _construir_eventos_historial(incidente)

    return IncidenteHistorialDetailResponse(
        id_incidente=incidente.id_incidente,
        titulo=incidente.titulo,
        fecha_reporte=incidente.fecha_reporte,
        tipo_incidente=incidente.tipo_incidente.nombre,
        prioridad=incidente.prioridad.nombre,
        id_estado_servicio_actual=incidente.id_estado_servicio_actual,
        estado_servicio_actual=incidente.estado_servicio_actual.nombre,
        descripcion_texto=incidente.descripcion_texto,
        direccion_referencia=incidente.direccion_referencia,
        latitud=incidente.latitud,
        longitud=incidente.longitud,
        historial=eventos,
        mensaje=(
            "No existen registros adicionales de historial para el incidente."
            if not eventos
            else None
        ),
    )


def listar_incidentes_cliente_service(
    db: Session,
    current_user,
) -> list[ClienteIncidenteListResponse]:
    cliente = _get_cliente_autenticado(db, current_user)
    incidentes = get_incidentes_by_cliente_id(db, cliente.id_cliente)

    return [
        ClienteIncidenteListResponse(
            id_incidente=incidente.id_incidente,
            titulo=incidente.titulo,
            fecha_reporte=incidente.fecha_reporte,
            id_estado_servicio_actual=incidente.id_estado_servicio_actual,
            estado_servicio_actual=incidente.estado_servicio_actual.nombre,
            tiene_asignacion=incidente.asignacion_servicio is not None,
        )
        for incidente in incidentes
    ]


def consultar_asignacion_auxilio_service(
    db: Session,
    current_user,
    id_incidente: int,
) -> AsignacionAuxilioDetalleResponse:
    cliente = _get_cliente_autenticado(db, current_user)
    incidente = get_incidente_asignacion_by_id_and_cliente(
        db,
        id_incidente=id_incidente,
        id_cliente=cliente.id_cliente,
    )
    if not incidente:
        raise ValueError("El incidente no existe o no pertenece al cliente autenticado.")

    asignacion = incidente.asignacion_servicio
    if not asignacion:
        return AsignacionAuxilioDetalleResponse(
            id_incidente=incidente.id_incidente,
            titulo=incidente.titulo,
            fecha_reporte=incidente.fecha_reporte,
            tipo_incidente=incidente.tipo_incidente.nombre,
            descripcion_texto=incidente.descripcion_texto,
            direccion_referencia=incidente.direccion_referencia,
            latitud=incidente.latitud,
            longitud=incidente.longitud,
            id_estado_servicio_actual=incidente.id_estado_servicio_actual,
            estado_servicio_actual=incidente.estado_servicio_actual.nombre,
            asignacion_definida=False,
            mensaje="El incidente aun no tiene una asignacion registrada.",
            placa_vehiculo=incidente.vehiculo.placa if incidente.vehiculo else None,
            marca_vehiculo=incidente.vehiculo.marca if incidente.vehiculo else None,
            modelo_vehiculo=incidente.vehiculo.modelo if incidente.vehiculo else None,
        )

    tecnico = None
    if asignacion.tecnico and asignacion.tecnico.usuario:
        tecnico = TecnicoAsignadoResponse(
            id_tecnico=asignacion.tecnico.id_tecnico,
            nombres=asignacion.tecnico.usuario.nombres,
            apellidos=asignacion.tecnico.usuario.apellidos,
            telefono_contacto=asignacion.tecnico.telefono_contacto,
        )

    unidad_movil = None
    if asignacion.unidad_movil:
        unidad_movil = UnidadMovilAsignadaResponse(
            id_unidad_movil=asignacion.unidad_movil.id_unidad_movil,
            placa=asignacion.unidad_movil.placa,
            tipo_unidad=asignacion.unidad_movil.tipo_unidad,
        )

    return AsignacionAuxilioDetalleResponse(
        id_incidente=incidente.id_incidente,
        titulo=incidente.titulo,
        fecha_reporte=incidente.fecha_reporte,
        tipo_incidente=incidente.tipo_incidente.nombre,
        descripcion_texto=incidente.descripcion_texto,
        direccion_referencia=incidente.direccion_referencia,
        latitud=incidente.latitud,
        longitud=incidente.longitud,
        id_estado_servicio_actual=incidente.id_estado_servicio_actual,
        estado_servicio_actual=incidente.estado_servicio_actual.nombre,
        estado_asignacion=asignacion.estado_asignacion,
        tiempo_estimado_min=asignacion.tiempo_estimado_min,
        asignacion_definida=True,
        mensaje=(
            None
            if tecnico or unidad_movil
            else "La asignacion fue registrada, pero aun no se definieron todos los recursos."
        ),
        taller=TallerAsignadoResponse(
            id_taller=asignacion.taller.id_taller,
            nombre_taller=asignacion.taller.nombre_taller,
            direccion=asignacion.taller.direccion,
        ),
        tecnico=tecnico,
        unidad_movil=unidad_movil,
        placa_vehiculo=incidente.vehiculo.placa if incidente.vehiculo else None,
        marca_vehiculo=incidente.vehiculo.marca if incidente.vehiculo else None,
        modelo_vehiculo=incidente.vehiculo.modelo if incidente.vehiculo else None,
    )


def get_estado_servicio_service(
    db: Session,
    current_user,
    id_incidente: int,
) -> EstadoServicioDetalleResponse:
    cliente = _get_cliente_autenticado(db, current_user)

    incidente = get_incidente_by_id_and_cliente(db, id_incidente, cliente.id_cliente)
    if not incidente:
        raise ValueError("El incidente no existe o no pertenece al cliente autenticado.")

    return EstadoServicioDetalleResponse(
        id_incidente=incidente.id_incidente,
        titulo=incidente.titulo,
        fecha_reporte=incidente.fecha_reporte,
        id_vehiculo=incidente.id_vehiculo,
        id_tipo_incidente=incidente.id_tipo_incidente,
        tipo_incidente=incidente.tipo_incidente.nombre,
        id_prioridad=incidente.id_prioridad,
        prioridad=incidente.prioridad.nombre,
        id_estado_servicio_actual=incidente.id_estado_servicio_actual,
        estado_servicio_actual=incidente.estado_servicio_actual.nombre,
        direccion_referencia=incidente.direccion_referencia,
        latitud=incidente.latitud,
        longitud=incidente.longitud,
        clasificacion_ia=incidente.clasificacion_ia,
        confianza_clasificacion=incidente.confianza_clasificacion,
        resumen_ia=incidente.resumen_ia,
        requiere_mas_info=incidente.requiere_mas_info,
    )
