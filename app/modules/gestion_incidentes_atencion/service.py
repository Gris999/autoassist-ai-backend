from sqlalchemy.orm import Session

from app.modules.gestion_operativa_taller_tecnico.repository import get_taller_by_usuario_id
from app.modules.gestion_clientes.repository import get_cliente_by_usuario_id
from app.modules.gestion_incidentes_atencion.repository import (
    create_asignacion_servicio,
    create_incidente,
    get_asignacion_servicio_by_incidente_id,
    get_asignacion_servicio_by_incidente_id_for_update,
    get_incidente_by_id_for_update,
    get_incidente_by_id,
    get_estado_servicio_by_nombre,
    get_incidentes_by_cliente_id,
    get_prioridad_by_nombre,
    get_solicitud_aceptada_by_incidente_id,
    get_solicitud_aceptada_by_incidente_and_taller_id,
    get_solicitud_taller_by_id,
    get_solicitud_taller_by_id_for_update,
    get_tecnico_by_id_for_update,
    get_tecnicos_disponibles_by_taller_id,
    get_tipo_incidente_by_id,
    get_unidad_movil_by_id_for_update,
    get_unidades_moviles_disponibles_by_taller_id,
    get_vehiculo_by_id_and_cliente,
    get_incidentes_disponibles,
    update_tecnico_disponibilidad,
    update_incidente_estado_servicio_actual,
    update_solicitud_taller_respuesta,
    update_unidad_movil_disponibilidad,
)
from app.modules.gestion_incidentes_atencion.schemas import (
    AsignacionIncidenteRequest,
    AsignacionIncidenteResponse,
    IncidenteCreateRequest,
    IncidenteResponse,
    IncidenteDisponibleResponse,
    ResponderSolicitudAtencionRequest,
    RespuestaSolicitudAtencionResponse,
    SolicitudAtencionDetalleResponse,
    TecnicoDisponibleAsignacionResponse,
    UnidadMovilDisponibleAsignacionResponse,
)

ESTADO_SOLICITUD_PENDIENTE = "PENDIENTE"
ESTADO_SOLICITUD_ACEPTADA = "ACEPTADA"
ESTADO_SOLICITUD_RECHAZADA = "RECHAZADA"
ESTADO_ASIGNACION_SERVICIO = "ASIGNADO"
ESTADOS_INCIDENTE_NO_DISPONIBLE_RESPUESTA = {
    "ASIGNADO",
    "EN_CAMINO",
    "EN_ATENCION",
    "FINALIZADO",
    "CANCELADO",
}


def _get_taller_actor_service(db: Session, current_user):
    taller = get_taller_by_usuario_id(db, current_user.id_usuario)
    if not taller:
        raise ValueError("El usuario autenticado no tiene perfil de taller.")
    return taller


def _validar_solicitud_del_taller(solicitud_taller, id_taller: int):
    if not solicitud_taller:
        raise ValueError("La solicitud de atencion especificada no existe.")
    if solicitud_taller.id_taller != id_taller:
        raise ValueError("La solicitud no pertenece al taller autenticado.")
    return solicitud_taller


def _to_solicitud_atencion_detalle_response(
    solicitud_taller,
) -> SolicitudAtencionDetalleResponse:
    incidente = solicitud_taller.incidente
    return SolicitudAtencionDetalleResponse(
        id_solicitud_taller=solicitud_taller.id_solicitud_taller,
        id_incidente=solicitud_taller.id_incidente,
        id_taller=solicitud_taller.id_taller,
        distancia_km=solicitud_taller.distancia_km,
        puntaje_asignacion=solicitud_taller.puntaje_asignacion,
        estado_solicitud=solicitud_taller.estado_solicitud,
        fecha_envio=solicitud_taller.fecha_envio,
        fecha_respuesta=solicitud_taller.fecha_respuesta,
        titulo_incidente=incidente.titulo,
        descripcion_texto=incidente.descripcion_texto,
        direccion_referencia=incidente.direccion_referencia,
        latitud=incidente.latitud,
        longitud=incidente.longitud,
        fecha_reporte=incidente.fecha_reporte,
        id_tipo_incidente=incidente.id_tipo_incidente,
        tipo_incidente=incidente.tipo_incidente.nombre,
        id_prioridad=incidente.id_prioridad,
        prioridad=incidente.prioridad.nombre,
        id_estado_servicio_actual=incidente.id_estado_servicio_actual,
        estado_servicio_actual=incidente.estado_servicio_actual.nombre,
    )


def _to_respuesta_solicitud_atencion_response(
    solicitud_taller,
    *,
    accion: str,
) -> RespuestaSolicitudAtencionResponse:
    incidente = solicitud_taller.incidente
    return RespuestaSolicitudAtencionResponse(
        id_solicitud_taller=solicitud_taller.id_solicitud_taller,
        id_incidente=solicitud_taller.id_incidente,
        id_taller=solicitud_taller.id_taller,
        accion=accion,
        estado_solicitud=solicitud_taller.estado_solicitud,
        fecha_respuesta=solicitud_taller.fecha_respuesta,
        id_estado_servicio_actual=incidente.id_estado_servicio_actual,
        estado_servicio_actual=incidente.estado_servicio_actual.nombre,
    )


def _validar_incidente_disponible_para_respuesta(incidente) -> None:
    if incidente.estado_servicio_actual.nombre in ESTADOS_INCIDENTE_NO_DISPONIBLE_RESPUESTA:
        raise ValueError("El incidente ya no se encuentra disponible para responder esta solicitud.")


def _to_tecnico_disponible_asignacion_response(
    tecnico,
) -> TecnicoDisponibleAsignacionResponse:
    return TecnicoDisponibleAsignacionResponse(
        id_tecnico=tecnico.id_tecnico,
        id_usuario=tecnico.id_usuario,
        nombres=tecnico.usuario.nombres,
        apellidos=tecnico.usuario.apellidos,
        telefono_contacto=tecnico.telefono_contacto,
        disponible=tecnico.disponible,
        estado=tecnico.estado,
    )


def _to_unidad_movil_disponible_asignacion_response(
    unidad_movil,
) -> UnidadMovilDisponibleAsignacionResponse:
    return UnidadMovilDisponibleAsignacionResponse(
        id_unidad_movil=unidad_movil.id_unidad_movil,
        id_taller=unidad_movil.id_taller,
        placa=unidad_movil.placa,
        tipo_unidad=unidad_movil.tipo_unidad,
        disponible=unidad_movil.disponible,
        estado=unidad_movil.estado,
    )


def _to_asignacion_incidente_response(
    asignacion,
    incidente,
) -> AsignacionIncidenteResponse:
    return AsignacionIncidenteResponse(
        id_asignacion=asignacion.id_asignacion,
        id_incidente=asignacion.id_incidente,
        id_taller=asignacion.id_taller,
        id_tecnico=asignacion.id_tecnico,
        id_unidad_movil=asignacion.id_unidad_movil,
        fecha_asignacion=asignacion.fecha_asignacion,
        tiempo_estimado_min=asignacion.tiempo_estimado_min,
        estado_asignacion=asignacion.estado_asignacion,
        observaciones=asignacion.observaciones,
        id_estado_servicio_actual=incidente.id_estado_servicio_actual,
        estado_servicio_actual=incidente.estado_servicio_actual.nombre,
    )


def _validar_incidente_aceptado_para_taller(db: Session, *, id_incidente: int, id_taller: int):
    incidente = get_incidente_by_id(db, id_incidente)
    if not incidente:
        raise ValueError("El incidente especificado no existe.")

    solicitud_aceptada = get_solicitud_aceptada_by_incidente_id(db, id_incidente)
    if not solicitud_aceptada:
        raise ValueError("El incidente no tiene una solicitud aceptada para atencion.")
    if solicitud_aceptada.id_taller != id_taller:
        raise ValueError("El incidente no corresponde al taller autenticado.")

    if incidente.estado_servicio_actual.nombre != "ASIGNADO":
        raise ValueError("El incidente no se encuentra en un estado apto para asignacion.")

    asignacion_existente = get_asignacion_servicio_by_incidente_id(db, id_incidente)
    if asignacion_existente:
        raise ValueError("El incidente ya tiene una asignacion registrada.")

    return incidente


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



def get_incidentes_disponibles_service(db: Session) -> list[IncidenteDisponibleResponse]:
    incidentes = get_incidentes_disponibles(db)

    return [
        IncidenteDisponibleResponse(
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
        )
        for incidente in incidentes
    ]


def get_solicitud_atencion_detalle_service(
    db: Session,
    current_user,
    id_solicitud_taller: int,
) -> SolicitudAtencionDetalleResponse:
    taller = _get_taller_actor_service(db, current_user)
    solicitud_taller = get_solicitud_taller_by_id(db, id_solicitud_taller)
    solicitud_taller = _validar_solicitud_del_taller(solicitud_taller, taller.id_taller)
    return _to_solicitud_atencion_detalle_response(solicitud_taller)


def responder_solicitud_atencion_service(
    db: Session,
    current_user,
    id_solicitud_taller: int,
    payload: ResponderSolicitudAtencionRequest,
) -> RespuestaSolicitudAtencionResponse:
    taller = _get_taller_actor_service(db, current_user)

    try:
        solicitud_taller = get_solicitud_taller_by_id_for_update(db, id_solicitud_taller)
        solicitud_taller = _validar_solicitud_del_taller(solicitud_taller, taller.id_taller)

        if solicitud_taller.estado_solicitud != ESTADO_SOLICITUD_PENDIENTE:
            raise ValueError("La solicitud ya fue respondida y no admite una nueva respuesta.")

        incidente = get_incidente_by_id_for_update(db, solicitud_taller.id_incidente)
        if not incidente:
            raise ValueError("El incidente asociado a la solicitud no existe.")
        _validar_incidente_disponible_para_respuesta(incidente)

        solicitud_aceptada = get_solicitud_aceptada_by_incidente_id(db, solicitud_taller.id_incidente)
        if solicitud_aceptada and solicitud_aceptada.id_solicitud_taller != solicitud_taller.id_solicitud_taller:
            raise ValueError("La solicitud ya fue tomada por otro taller.")

        if payload.accion == "aceptar":
            estado_asignado = get_estado_servicio_by_nombre(db, "ASIGNADO")
            if not estado_asignado:
                raise ValueError("No existe el estado ASIGNADO en la base de datos.")

            update_solicitud_taller_respuesta(
                db,
                solicitud_taller,
                estado_solicitud=ESTADO_SOLICITUD_ACEPTADA,
            )
            update_incidente_estado_servicio_actual(
                db,
                incidente,
                id_estado_servicio_actual=estado_asignado.id_estado_servicio,
            )
        else:
            update_solicitud_taller_respuesta(
                db,
                solicitud_taller,
                estado_solicitud=ESTADO_SOLICITUD_RECHAZADA,
            )

        db.commit()
        solicitud_taller_actualizada = get_solicitud_taller_by_id(db, solicitud_taller.id_solicitud_taller)
        return _to_respuesta_solicitud_atencion_response(
            solicitud_taller_actualizada,
            accion=payload.accion,
        )
    except Exception:
        db.rollback()
        raise


def listar_tecnicos_disponibles_para_incidente_service(
    db: Session,
    current_user,
    id_incidente: int,
) -> list[TecnicoDisponibleAsignacionResponse]:
    taller = _get_taller_actor_service(db, current_user)
    _validar_incidente_aceptado_para_taller(
        db,
        id_incidente=id_incidente,
        id_taller=taller.id_taller,
    )
    tecnicos = get_tecnicos_disponibles_by_taller_id(db, taller.id_taller)
    return [_to_tecnico_disponible_asignacion_response(tecnico) for tecnico in tecnicos]


def listar_unidades_moviles_disponibles_para_incidente_service(
    db: Session,
    current_user,
    id_incidente: int,
) -> list[UnidadMovilDisponibleAsignacionResponse]:
    taller = _get_taller_actor_service(db, current_user)
    _validar_incidente_aceptado_para_taller(
        db,
        id_incidente=id_incidente,
        id_taller=taller.id_taller,
    )
    unidades_moviles = get_unidades_moviles_disponibles_by_taller_id(db, taller.id_taller)
    return [
        _to_unidad_movil_disponible_asignacion_response(unidad_movil)
        for unidad_movil in unidades_moviles
    ]


def asignar_tecnico_unidad_incidente_service(
    db: Session,
    current_user,
    id_incidente: int,
    payload: AsignacionIncidenteRequest,
) -> AsignacionIncidenteResponse:
    taller = _get_taller_actor_service(db, current_user)

    try:
        incidente = get_incidente_by_id_for_update(db, id_incidente)
        if not incidente:
            raise ValueError("El incidente especificado no existe.")

        solicitud_aceptada = get_solicitud_aceptada_by_incidente_and_taller_id(
            db,
            id_incidente=id_incidente,
            id_taller=taller.id_taller,
        )
        if not solicitud_aceptada:
            solicitud_aceptada_otro_taller = get_solicitud_aceptada_by_incidente_id(db, id_incidente)
            if solicitud_aceptada_otro_taller:
                raise ValueError("El incidente fue aceptado por otro taller.")
            raise ValueError("El incidente no fue aceptado previamente por el taller autenticado.")

        if incidente.estado_servicio_actual.nombre != "ASIGNADO":
            raise ValueError("El incidente no se encuentra en un estado apto para asignacion.")

        asignacion_existente = get_asignacion_servicio_by_incidente_id_for_update(db, id_incidente)
        if asignacion_existente:
            raise ValueError("El incidente ya tiene una asignacion registrada.")

        tecnico = get_tecnico_by_id_for_update(db, payload.id_tecnico)
        if not tecnico:
            raise ValueError("El tecnico especificado no existe.")
        if tecnico.id_taller != taller.id_taller:
            raise ValueError("El tecnico no pertenece al taller autenticado.")
        if not tecnico.estado or not tecnico.disponible:
            raise ValueError("El tecnico seleccionado no se encuentra disponible.")

        unidad_movil = get_unidad_movil_by_id_for_update(db, payload.id_unidad_movil)
        if not unidad_movil:
            raise ValueError("La unidad movil especificada no existe.")
        if unidad_movil.id_taller != taller.id_taller:
            raise ValueError("La unidad movil no pertenece al taller autenticado.")
        if not unidad_movil.estado or not unidad_movil.disponible:
            raise ValueError("La unidad movil seleccionada no se encuentra disponible.")

        estado_asignado = get_estado_servicio_by_nombre(db, "ASIGNADO")
        if not estado_asignado:
            raise ValueError("No existe el estado ASIGNADO en la base de datos.")

        asignacion = create_asignacion_servicio(
            db,
            id_incidente=id_incidente,
            id_taller=taller.id_taller,
            id_tecnico=payload.id_tecnico,
            id_unidad_movil=payload.id_unidad_movil,
            tiempo_estimado_min=payload.tiempo_estimado_min,
            estado_asignacion=ESTADO_ASIGNACION_SERVICIO,
            observaciones=payload.observaciones,
        )
        update_tecnico_disponibilidad(db, tecnico, disponible=False)
        update_unidad_movil_disponibilidad(db, unidad_movil, disponible=False)
        update_incidente_estado_servicio_actual(
            db,
            incidente,
            id_estado_servicio_actual=estado_asignado.id_estado_servicio,
        )

        db.commit()
        incidente_actualizado = get_incidente_by_id(db, id_incidente)
        return _to_asignacion_incidente_response(asignacion, incidente_actualizado)
    except Exception:
        db.rollback()
        raise
