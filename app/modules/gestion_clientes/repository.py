from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.gestion_clientes.models import Cliente, TipoVehiculo, Vehiculo


def get_cliente_by_usuario_id(db: Session, id_usuario: int) -> Cliente | None:
    return db.execute(
        select(Cliente).where(Cliente.id_usuario == id_usuario)
    ).scalar_one_or_none()


def get_tipo_vehiculo_by_id(db: Session, id_tipo_vehiculo: int) -> TipoVehiculo | None:
    return db.execute(
        select(TipoVehiculo).where(TipoVehiculo.id_tipo_vehiculo == id_tipo_vehiculo)
    ).scalar_one_or_none()


def get_vehiculo_by_placa(db: Session, placa: str) -> Vehiculo | None:
    return db.execute(
        select(Vehiculo).where(Vehiculo.placa == placa)
    ).scalar_one_or_none()


def create_vehiculo(
    db: Session,
    *,
    id_cliente: int,
    id_tipo_vehiculo: int,
    placa: str,
    marca: str,
    modelo: str,
    anio: int,
    color: str | None,
    descripcion_referencia: str | None,
) -> Vehiculo:
    vehiculo = Vehiculo(
        id_cliente=id_cliente,
        id_tipo_vehiculo=id_tipo_vehiculo,
        placa=placa,
        marca=marca,
        modelo=modelo,
        anio=anio,
        color=color,
        descripcion_referencia=descripcion_referencia,
        estado=True,
    )
    db.add(vehiculo)
    db.flush()
    db.refresh(vehiculo)
    return vehiculo


def get_vehiculos_by_cliente_id(db: Session, id_cliente: int) -> list[Vehiculo]:
    return db.execute(
        select(Vehiculo).where(Vehiculo.id_cliente == id_cliente)
    ).scalars().all()