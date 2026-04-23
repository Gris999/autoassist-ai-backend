from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.gestion_operativa_taller_tecnico.models import (
    Taller,
    TallerAuxilio,
    TipoAuxilio,
)


def get_taller_by_usuario_id(db: Session, id_usuario: int) -> Taller | None:
    return db.execute(
        select(Taller).where(Taller.id_usuario == id_usuario)
    ).scalar_one_or_none()


def get_taller_by_id(db: Session, id_taller: int) -> Taller | None:
    return db.execute(
        select(Taller).where(Taller.id_taller == id_taller)
    ).scalar_one_or_none()


def update_disponibilidad_taller(
    db: Session,
    *,
    id_taller: int,
    disponible: bool,
) -> Taller:
    taller = get_taller_by_id(db, id_taller)
    if taller:
        taller.disponible = disponible
        db.flush()
        db.refresh(taller)
    return taller


def get_talleres_disponibles(db: Session) -> list[Taller]:
    return list(
        db.execute(
            select(Taller).where(Taller.disponible == True)
        ).scalars()
    )


def get_tipo_auxilio_by_id(db: Session, id_tipo_auxilio: int) -> TipoAuxilio | None:
    return db.execute(
        select(TipoAuxilio).where(
            TipoAuxilio.id_tipo_auxilio == id_tipo_auxilio,
            TipoAuxilio.estado == True,
        )
    ).scalar_one_or_none()


def get_servicios_auxilio_por_taller_id(db: Session, id_taller: int) -> list[TallerAuxilio]:
    return list(
        db.execute(
            select(TallerAuxilio).where(TallerAuxilio.id_taller == id_taller)
        ).scalars()
    )


def get_taller_auxilio_by_id(db: Session, id_taller_auxilio: int) -> TallerAuxilio | None:
    return db.execute(
        select(TallerAuxilio).where(
            TallerAuxilio.id_taller_auxilio == id_taller_auxilio
        )
    ).scalar_one_or_none()


def get_taller_auxilio_by_taller_id_tipo_auxilio(
    db: Session,
    id_taller: int,
    id_tipo_auxilio: int,
) -> TallerAuxilio | None:
    return db.execute(
        select(TallerAuxilio).where(
            TallerAuxilio.id_taller == id_taller,
            TallerAuxilio.id_tipo_auxilio == id_tipo_auxilio,
        )
    ).scalar_one_or_none()


def create_taller_auxilio(
    db: Session,
    *,
    id_taller: int,
    id_tipo_auxilio: int,
    precio_referencial: float,
    disponible: bool,
) -> TallerAuxilio:
    servicio = TallerAuxilio(
        id_taller=id_taller,
        id_tipo_auxilio=id_tipo_auxilio,
        precio_referencial=precio_referencial,
        disponible=disponible,
    )
    db.add(servicio)
    db.flush()
    db.refresh(servicio)
    return servicio


def update_taller_auxilio(
    db: Session,
    taller_auxilio: TallerAuxilio,
    *,
    precio_referencial: float | None = None,
    disponible: bool | None = None,
) -> TallerAuxilio:
    if precio_referencial is not None:
        taller_auxilio.precio_referencial = precio_referencial
    if disponible is not None:
        taller_auxilio.disponible = disponible
    db.flush()
    db.refresh(taller_auxilio)
    return taller_auxilio


def set_disponibilidad_taller_auxilio(
    db: Session,
    taller_auxilio: TallerAuxilio,
    disponible: bool,
) -> TallerAuxilio:
    taller_auxilio.disponible = disponible
    db.flush()
    db.refresh(taller_auxilio)
    return taller_auxilio
