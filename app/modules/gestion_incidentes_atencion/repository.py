from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.gestion_clientes.models import Vehiculo
from app.modules.gestion_incidentes_atencion.models import (
    EstadoServicio,
    Incidente,
    Prioridad,
    TipoIncidente,
)


def get_tipo_incidente_by_id(db: Session, id_tipo_incidente: int) -> TipoIncidente | None:
    return db.execute(
        select(TipoIncidente).where(TipoIncidente.id_tipo_incidente == id_tipo_incidente)
    ).scalar_one_or_none()


def get_prioridad_by_nombre(db: Session, nombre: str) -> Prioridad | None:
    return db.execute(
        select(Prioridad).where(Prioridad.nombre == nombre)
    ).scalar_one_or_none()


def get_estado_servicio_by_nombre(db: Session, nombre: str) -> EstadoServicio | None:
    return db.execute(
        select(EstadoServicio).where(EstadoServicio.nombre == nombre)
    ).scalar_one_or_none()


def get_vehiculo_by_id_and_cliente(db: Session, id_vehiculo: int, id_cliente: int) -> Vehiculo | None:
    return db.execute(
        select(Vehiculo).where(
            Vehiculo.id_vehiculo == id_vehiculo,
            Vehiculo.id_cliente == id_cliente,
        )
    ).scalar_one_or_none()


def create_incidente(
    db: Session,
    *,
    id_cliente: int,
    id_vehiculo: int,
    id_tipo_incidente: int,
    id_prioridad: int,
    id_estado_servicio_actual: int,
    titulo: str,
    descripcion_texto: str | None,
    direccion_referencia: str | None,
    latitud,
    longitud,
) -> Incidente:
    incidente = Incidente(
        id_cliente=id_cliente,
        id_vehiculo=id_vehiculo,
        id_tipo_incidente=id_tipo_incidente,
        id_prioridad=id_prioridad,
        id_estado_servicio_actual=id_estado_servicio_actual,
        titulo=titulo,
        descripcion_texto=descripcion_texto,
        direccion_referencia=direccion_referencia,
        latitud=latitud,
        longitud=longitud,
        clasificacion_ia=None,
        confianza_clasificacion=None,
        resumen_ia=None,
        requiere_mas_info=False,
    )
    db.add(incidente)
    db.flush()
    db.refresh(incidente)
    return incidente


def get_incidentes_by_cliente_id(db: Session, id_cliente: int) -> list[Incidente]:
    return db.execute(
        select(Incidente).where(Incidente.id_cliente == id_cliente)
    ).scalars().all()