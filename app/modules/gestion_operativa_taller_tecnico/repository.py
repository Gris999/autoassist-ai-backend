from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.gestion_operativa_taller_tecnico.models import Taller


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
