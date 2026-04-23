from sqlalchemy.orm import Session

from app.modules.gestion_operativa_taller_tecnico.repository import (
    create_taller_auxilio,
    get_taller_auxilio_by_id,
    get_taller_auxilio_by_taller_id_tipo_auxilio,
    get_taller_by_usuario_id,
    get_servicios_auxilio_por_taller_id,
    get_talleres_disponibles,
    get_tipo_auxilio_by_id,
    set_disponibilidad_taller_auxilio,
    update_disponibilidad_taller,
    update_taller_auxilio,
)
from app.modules.gestion_operativa_taller_tecnico.schemas import (
    ActualizarDisponibilidadTallerRequest,
    TallerAuxilioCreateRequest,
    TallerAuxilioResponse,
    TallerAuxilioUpdateRequest,
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


def listar_servicios_auxilio_service(
    db: Session,
    current_user,
) -> list[TallerAuxilioResponse]:
    taller = get_taller_by_usuario_id(db, current_user.id_usuario)
    if not taller:
        raise ValueError("El usuario autenticado no tiene perfil de taller.")

    servicios = get_servicios_auxilio_por_taller_id(db, taller.id_taller)
    return [
        TallerAuxilioResponse(
            id_taller_auxilio=s.id_taller_auxilio,
            id_taller=s.id_taller,
            id_tipo_auxilio=s.id_tipo_auxilio,
            nombre_tipo_auxilio=s.tipo_auxilio.nombre,
            descripcion_tipo_auxilio=s.tipo_auxilio.descripcion,
            precio_referencial=float(s.precio_referencial),
            disponible=s.disponible,
        )
        for s in servicios
    ]


def registrar_servicio_auxilio_service(
    db: Session,
    current_user,
    payload: TallerAuxilioCreateRequest,
) -> TallerAuxilioResponse:
    taller = get_taller_by_usuario_id(db, current_user.id_usuario)
    if not taller:
        raise ValueError("El usuario autenticado no tiene perfil de taller.")

    tipo_auxilio = get_tipo_auxilio_by_id(db, payload.id_tipo_auxilio)
    if not tipo_auxilio:
        raise ValueError("El tipo de auxilio especificado no existe.")

    existing = get_taller_auxilio_by_taller_id_tipo_auxilio(
        db,
        id_taller=taller.id_taller,
        id_tipo_auxilio=payload.id_tipo_auxilio,
    )
    if existing:
        raise ValueError("El taller ya ofrece ese tipo de auxilio.")

    try:
        servicio = create_taller_auxilio(
            db,
            id_taller=taller.id_taller,
            id_tipo_auxilio=payload.id_tipo_auxilio,
            precio_referencial=payload.precio_referencial,
            disponible=payload.disponible,
        )
        db.commit()
        db.refresh(servicio)
        return TallerAuxilioResponse(
            id_taller_auxilio=servicio.id_taller_auxilio,
            id_taller=servicio.id_taller,
            id_tipo_auxilio=servicio.id_tipo_auxilio,
            nombre_tipo_auxilio=servicio.tipo_auxilio.nombre,
            descripcion_tipo_auxilio=servicio.tipo_auxilio.descripcion,
            precio_referencial=float(servicio.precio_referencial),
            disponible=servicio.disponible,
        )
    except Exception:
        db.rollback()
        raise


def actualizar_servicio_auxilio_service(
    db: Session,
    current_user,
    id_taller_auxilio: int,
    payload: TallerAuxilioUpdateRequest,
) -> TallerAuxilioResponse:
    taller = get_taller_by_usuario_id(db, current_user.id_usuario)
    if not taller:
        raise ValueError("El usuario autenticado no tiene perfil de taller.")

    servicio = get_taller_auxilio_by_id(db, id_taller_auxilio)
    if not servicio:
        raise ValueError("El servicio de auxilio especificado no existe.")
    if servicio.id_taller != taller.id_taller:
        raise ValueError("El servicio no pertenece al taller autenticado.")

    try:
        servicio_actualizado = update_taller_auxilio(
            db,
            servicio,
            precio_referencial=payload.precio_referencial,
            disponible=payload.disponible,
        )
        db.commit()
        db.refresh(servicio_actualizado)
        return TallerAuxilioResponse(
            id_taller_auxilio=servicio_actualizado.id_taller_auxilio,
            id_taller=servicio_actualizado.id_taller,
            id_tipo_auxilio=servicio_actualizado.id_tipo_auxilio,
            nombre_tipo_auxilio=servicio_actualizado.tipo_auxilio.nombre,
            descripcion_tipo_auxilio=servicio_actualizado.tipo_auxilio.descripcion,
            precio_referencial=float(servicio_actualizado.precio_referencial),
            disponible=servicio_actualizado.disponible,
        )
    except Exception:
        db.rollback()
        raise


def deshabilitar_servicio_auxilio_service(
    db: Session,
    current_user,
    id_taller_auxilio: int,
) -> TallerAuxilioResponse:
    taller = get_taller_by_usuario_id(db, current_user.id_usuario)
    if not taller:
        raise ValueError("El usuario autenticado no tiene perfil de taller.")

    servicio = get_taller_auxilio_by_id(db, id_taller_auxilio)
    if not servicio:
        raise ValueError("El servicio de auxilio especificado no existe.")
    if servicio.id_taller != taller.id_taller:
        raise ValueError("El servicio no pertenece al taller autenticado.")

    try:
        servicio_actualizado = set_disponibilidad_taller_auxilio(
            db,
            servicio,
            disponible=False,
        )
        db.commit()
        db.refresh(servicio_actualizado)
        return TallerAuxilioResponse(
            id_taller_auxilio=servicio_actualizado.id_taller_auxilio,
            id_taller=servicio_actualizado.id_taller,
            id_tipo_auxilio=servicio_actualizado.id_tipo_auxilio,
            nombre_tipo_auxilio=servicio_actualizado.tipo_auxilio.nombre,
            descripcion_tipo_auxilio=servicio_actualizado.tipo_auxilio.descripcion,
            precio_referencial=float(servicio_actualizado.precio_referencial),
            disponible=servicio_actualizado.disponible,
        )
    except Exception:
        db.rollback()
        raise
