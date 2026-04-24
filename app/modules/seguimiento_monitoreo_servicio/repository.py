from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.modules.gestion_incidentes_atencion.models import AsignacionServicio, Incidente
from app.modules.gestion_operativa_taller_tecnico.models import Tecnico, Taller, UnidadMovil


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
