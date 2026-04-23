from sqlalchemy.orm import Session

from app.modules.gestion_operativa_taller_tecnico.repository import (
    get_taller_by_id,
    get_taller_by_usuario_id,
    get_talleres_disponibles,
    update_disponibilidad_taller,
)
from app.modules.gestion_operativa_taller_tecnico.schemas import (
    ActualizarDisponibilidadTallerRequest,
    DisponibilidadTallerResponse,
    TallerInfoResponse,
)


def obtener_disponibilidad_taller_service(
    db: Session,
    current_user,
) -> DisponibilidadTallerResponse:
    taller = get_taller_by_usuario_id(db, current_user.id_usuario)
    if not taller:
        raise ValueError("El usuario autenticado no tiene perfil de taller.")

    return DisponibilidadTallerResponse.model_validate(taller)


def actualizar_disponibilidad_taller_service(
    db: Session,
    current_user,
    payload: ActualizarDisponibilidadTallerRequest,
) -> DisponibilidadTallerResponse:
    taller = get_taller_by_usuario_id(db, current_user.id_usuario)
    if not taller:
        raise ValueError("El usuario autenticado no tiene perfil de taller.")

    try:
        taller_actualizado = update_disponibilidad_taller(
            db,
            id_taller=taller.id_taller,
            disponible=payload.disponible,
        )

        db.commit()
        db.refresh(taller_actualizado)

        return DisponibilidadTallerResponse.model_validate(taller_actualizado)
    except Exception:
        db.rollback()
        raise


def obtener_talleres_disponibles_service(
    db: Session,
) -> list[TallerInfoResponse]:
    talleres = get_talleres_disponibles(db)
    return [TallerInfoResponse.model_validate(t) for t in talleres]


def obtener_informacion_taller_service(
    db: Session,
    current_user,
) -> TallerInfoResponse:
    taller = get_taller_by_usuario_id(db, current_user.id_usuario)
    if not taller:
        raise ValueError("El usuario autenticado no tiene perfil de taller.")

    return TallerInfoResponse.model_validate(taller)
