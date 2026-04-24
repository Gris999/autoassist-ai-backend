from sqlalchemy.orm import Session

from app.modules.gestion_clientes.repository import get_cliente_by_usuario_id
from app.modules.seguimiento_monitoreo_servicio.schemas import (
    AsignacionAuxilioDetalleResponse,
    ClienteIncidenteListResponse,
    EstadoServicioDetalleResponse,
    TallerAsignadoResponse,
    TecnicoAsignadoResponse,
    UnidadMovilAsignadaResponse,
)
from app.modules.seguimiento_monitoreo_servicio.repository import (
    get_incidente_asignacion_by_id_and_cliente,
    get_incidentes_by_cliente_id,
)
from app.modules.gestion_incidentes_atencion.repository import get_incidente_by_id_and_cliente


def _get_cliente_autenticado(db: Session, current_user):
    cliente = get_cliente_by_usuario_id(db, current_user.id_usuario)
    if not cliente:
        raise ValueError("El usuario autenticado no tiene perfil de cliente.")
    return cliente


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
