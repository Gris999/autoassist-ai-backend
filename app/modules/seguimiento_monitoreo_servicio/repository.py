from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.modules.autenticacion_seguridad.models import Usuario
from app.modules.gestion_incidentes_atencion.models import AsignacionServicio, Incidente
from app.modules.gestion_operativa_taller_tecnico.models import Tecnico, Taller, UnidadMovil
from app.modules.seguimiento_monitoreo_servicio.models import Notificacion


def get_incidentes_by_cliente_id(db: Session, id_cliente: int) -> list[Incidente]:
    return list(
        db.execute(
            select(Incidente)
            .options(
                joinedload(Incidente.estado_servicio_actual),
                joinedload(Incidente.asignacion_servicio),
            )
            .where(Incidente.id_cliente == id_cliente)
            .order_by(Incidente.fecha_reporte.desc())
        ).scalars()
    )


def get_incidente_asignacion_by_id_and_cliente(
    db: Session,
    *,
    id_incidente: int,
    id_cliente: int,
) -> Incidente | None:
    return db.execute(
        select(Incidente)
        .options(
            joinedload(Incidente.tipo_incidente),
            joinedload(Incidente.estado_servicio_actual),
            joinedload(Incidente.vehiculo),
            joinedload(Incidente.asignacion_servicio)
            .joinedload(AsignacionServicio.taller.of_type(Taller)),
            joinedload(Incidente.asignacion_servicio)
            .joinedload(AsignacionServicio.tecnico.of_type(Tecnico))
            .joinedload(Tecnico.usuario),
            joinedload(Incidente.asignacion_servicio)
            .joinedload(AsignacionServicio.unidad_movil.of_type(UnidadMovil)),
        )
        .where(
            Incidente.id_incidente == id_incidente,
            Incidente.id_cliente == id_cliente,
        )
    ).scalar_one_or_none()


def get_usuario_by_id(db: Session, id_usuario: int) -> Usuario | None:
    return db.execute(
        select(Usuario).where(Usuario.id_usuario == id_usuario)
    ).scalar_one_or_none()


def get_incidente_by_id(db: Session, id_incidente: int) -> Incidente | None:
    return db.execute(
        select(Incidente).where(Incidente.id_incidente == id_incidente)
    ).scalar_one_or_none()


def get_notificaciones_by_usuario_id(db: Session, id_usuario: int) -> list[Notificacion]:
    return list(
        db.execute(
            select(Notificacion)
            .where(Notificacion.id_usuario == id_usuario)
            .order_by(Notificacion.leido.asc(), Notificacion.fecha_envio.desc())
        ).scalars()
    )


def get_notificacion_by_id_and_usuario(
    db: Session,
    *,
    id_notificacion: int,
    id_usuario: int,
) -> Notificacion | None:
    return db.execute(
        select(Notificacion).where(
            Notificacion.id_notificacion == id_notificacion,
            Notificacion.id_usuario == id_usuario,
        )
    ).scalar_one_or_none()


def create_notificacion(
    db: Session,
    *,
    id_usuario: int,
    id_incidente: int | None,
    titulo: str,
    mensaje: str,
    tipo_notificacion: str,
) -> Notificacion:
    notificacion = Notificacion(
        id_usuario=id_usuario,
        id_incidente=id_incidente,
        titulo=titulo,
        mensaje=mensaje,
        tipo_notificacion=tipo_notificacion,
        leido=False,
    )
    db.add(notificacion)
    db.flush()
    db.refresh(notificacion)
    return notificacion


def update_notificacion_leido(
    db: Session,
    notificacion: Notificacion,
    *,
    leido: bool,
) -> Notificacion:
    notificacion.leido = leido
    db.flush()
    db.refresh(notificacion)
    return notificacion
