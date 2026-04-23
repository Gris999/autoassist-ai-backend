from sqlalchemy.orm import Session

from app.core.security.security import hash_password
from app.modules.autenticacion_seguridad.repository import (
    assign_rol_to_usuario,
    create_usuario,
    get_rol_by_nombre,
    get_usuario_by_email,
)
from app.modules.gestion_operativa_taller_tecnico.repository import (
    create_tecnico,
    create_taller_auxilio,
    get_asignacion_activa_by_tecnico_id,
    get_taller_auxilio_by_id,
    get_taller_auxilio_by_taller_id_tipo_auxilio,
    get_taller_by_usuario_id,
    get_servicios_auxilio_por_taller_id,
    get_tecnico_with_usuario_by_id,
    get_tecnicos_by_taller_id,
    get_tecnico_by_usuario_id,
    get_talleres_disponibles,
    get_tipo_auxilio_by_id,
    set_disponibilidad_taller_auxilio,
    update_estado_tecnico,
    update_disponibilidad_tecnico,
    update_disponibilidad_taller,
    update_taller_auxilio,
    update_tecnico,
    update_usuario_tecnico,
)
from app.modules.gestion_operativa_taller_tecnico.schemas import (
    ActualizarDisponibilidadTecnicoRequest,
    ActualizarDisponibilidadTallerRequest,
    DisponibilidadTecnicoResponse,
    TecnicoCreateRequest,
    TecnicoDetailResponse,
    TecnicoEstadoResponse,
    TecnicoListResponse,
    TecnicoUpdateRequest,
    TallerAuxilioCreateRequest,
    TallerAuxilioResponse,
    TallerAuxilioUpdateRequest,
    DisponibilidadTallerResponse,
    TallerInfoResponse,
)


def _get_taller_gestor_service(db: Session, current_user):
    taller = get_taller_by_usuario_id(db, current_user.id_usuario)
    if not taller:
        raise ValueError("El usuario autenticado no tiene perfil de taller.")
    return taller


def _validar_tecnico_del_taller(db: Session, id_tecnico: int, id_taller: int):
    tecnico = get_tecnico_with_usuario_by_id(db, id_tecnico)
    if not tecnico:
        raise ValueError("El tecnico especificado no existe.")
    if tecnico.id_taller != id_taller:
        raise ValueError("El tecnico no pertenece al taller autenticado.")
    return tecnico


def _to_tecnico_list_response(tecnico) -> TecnicoListResponse:
    return TecnicoListResponse(
        id_tecnico=tecnico.id_tecnico,
        id_usuario=tecnico.id_usuario,
        nombres=tecnico.usuario.nombres,
        apellidos=tecnico.usuario.apellidos,
        email=tecnico.usuario.email,
        celular=tecnico.usuario.celular,
        telefono_contacto=tecnico.telefono_contacto,
        disponible=tecnico.disponible,
        estado=tecnico.estado,
    )


def _to_tecnico_detail_response(tecnico) -> TecnicoDetailResponse:
    return TecnicoDetailResponse(
        id_tecnico=tecnico.id_tecnico,
        id_usuario=tecnico.id_usuario,
        id_taller=tecnico.id_taller,
        nombres=tecnico.usuario.nombres,
        apellidos=tecnico.usuario.apellidos,
        email=tecnico.usuario.email,
        celular=tecnico.usuario.celular,
        telefono_contacto=tecnico.telefono_contacto,
        disponible=tecnico.disponible,
        estado=tecnico.estado,
        latitud_actual=float(tecnico.latitud_actual) if tecnico.latitud_actual is not None else None,
        longitud_actual=float(tecnico.longitud_actual) if tecnico.longitud_actual is not None else None,
    )


def _to_tecnico_estado_response(tecnico) -> TecnicoEstadoResponse:
    return TecnicoEstadoResponse(
        id_tecnico=tecnico.id_tecnico,
        id_usuario=tecnico.id_usuario,
        estado=tecnico.estado,
        disponible=tecnico.disponible,
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


def listar_tecnicos_service(
    db: Session,
    current_user,
) -> list[TecnicoListResponse]:
    taller = _get_taller_gestor_service(db, current_user)
    tecnicos = get_tecnicos_by_taller_id(db, taller.id_taller)
    return [_to_tecnico_list_response(tecnico) for tecnico in tecnicos]


def obtener_tecnico_service(
    db: Session,
    current_user,
    id_tecnico: int,
) -> TecnicoDetailResponse:
    taller = _get_taller_gestor_service(db, current_user)
    tecnico = _validar_tecnico_del_taller(db, id_tecnico, taller.id_taller)
    return _to_tecnico_detail_response(tecnico)


def registrar_tecnico_service(
    db: Session,
    current_user,
    payload: TecnicoCreateRequest,
) -> TecnicoDetailResponse:
    taller = _get_taller_gestor_service(db, current_user)

    existing_user = get_usuario_by_email(db, payload.email)
    if existing_user:
        raise ValueError("Ya existe un usuario registrado con ese email.")

    rol_tecnico = get_rol_by_nombre(db, "TECNICO")
    if not rol_tecnico:
        raise ValueError("No existe el rol TECNICO en la base de datos.")

    try:
        usuario = create_usuario(
            db,
            nombres=payload.nombres,
            apellidos=payload.apellidos,
            celular=payload.celular,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )

        if not payload.estado:
            update_usuario_tecnico(
                db,
                usuario,
                estado=False,
            )

        assign_rol_to_usuario(
            db,
            id_usuario=usuario.id_usuario,
            id_rol=rol_tecnico.id_rol,
        )

        tecnico = create_tecnico(
            db,
            id_usuario=usuario.id_usuario,
            id_taller=taller.id_taller,
            telefono_contacto=payload.telefono_contacto,
            disponible=payload.disponible if payload.estado else False,
            estado=payload.estado,
        )

        db.commit()
        tecnico = get_tecnico_with_usuario_by_id(db, tecnico.id_tecnico)
        return _to_tecnico_detail_response(tecnico)
    except Exception:
        db.rollback()
        raise


def actualizar_tecnico_service(
    db: Session,
    current_user,
    id_tecnico: int,
    payload: TecnicoUpdateRequest,
) -> TecnicoDetailResponse:
    taller = _get_taller_gestor_service(db, current_user)
    tecnico = _validar_tecnico_del_taller(db, id_tecnico, taller.id_taller)

    if (
        payload.nombres is None
        and payload.apellidos is None
        and payload.celular is None
        and payload.email is None
        and payload.telefono_contacto is None
        and payload.disponible is None
    ):
        raise ValueError("Debe indicar al menos un campo para actualizar.")

    if payload.email is not None:
        existing_user = get_usuario_by_email(db, payload.email)
        if existing_user and existing_user.id_usuario != tecnico.id_usuario:
            raise ValueError("Ya existe un usuario registrado con ese email.")

    if payload.disponible is True and not tecnico.estado:
        raise ValueError("No se puede marcar como disponible un tecnico deshabilitado.")

    try:
        update_usuario_tecnico(
            db,
            tecnico.usuario,
            nombres=payload.nombres,
            apellidos=payload.apellidos,
            celular=payload.celular,
            email=payload.email,
        )

        update_tecnico(
            db,
            tecnico,
            telefono_contacto=payload.telefono_contacto,
            disponible=payload.disponible,
        )

        db.commit()
        tecnico_actualizado = get_tecnico_with_usuario_by_id(db, tecnico.id_tecnico)
        return _to_tecnico_detail_response(tecnico_actualizado)
    except Exception:
        db.rollback()
        raise


def habilitar_tecnico_service(
    db: Session,
    current_user,
    id_tecnico: int,
) -> TecnicoEstadoResponse:
    taller = _get_taller_gestor_service(db, current_user)
    tecnico = _validar_tecnico_del_taller(db, id_tecnico, taller.id_taller)

    try:
        update_usuario_tecnico(
            db,
            tecnico.usuario,
            estado=True,
        )
        tecnico_actualizado = update_estado_tecnico(
            db,
            tecnico,
            estado=True,
        )
        db.commit()
        db.refresh(tecnico_actualizado)
        return _to_tecnico_estado_response(tecnico_actualizado)
    except Exception:
        db.rollback()
        raise


def deshabilitar_tecnico_service(
    db: Session,
    current_user,
    id_tecnico: int,
) -> TecnicoEstadoResponse:
    taller = _get_taller_gestor_service(db, current_user)
    tecnico = _validar_tecnico_del_taller(db, id_tecnico, taller.id_taller)

    try:
        update_usuario_tecnico(
            db,
            tecnico.usuario,
            estado=False,
        )
        tecnico_actualizado = update_estado_tecnico(
            db,
            tecnico,
            estado=False,
        )
        db.commit()
        db.refresh(tecnico_actualizado)
        return _to_tecnico_estado_response(tecnico_actualizado)
    except Exception:
        db.rollback()
        raise


def obtener_disponibilidad_tecnico_service(
    db: Session,
    current_user,
) -> DisponibilidadTecnicoResponse:
    tecnico = get_tecnico_by_usuario_id(db, current_user.id_usuario)
    if not tecnico:
        raise ValueError("El usuario autenticado no tiene perfil de tecnico.")
    if not tecnico.estado:
        raise ValueError("El tecnico no se encuentra habilitado en el sistema.")

    return DisponibilidadTecnicoResponse.model_validate(tecnico)


def actualizar_disponibilidad_tecnico_service(
    db: Session,
    current_user,
    payload: ActualizarDisponibilidadTecnicoRequest,
) -> DisponibilidadTecnicoResponse:
    tecnico = get_tecnico_by_usuario_id(db, current_user.id_usuario)
    if not tecnico:
        raise ValueError("El usuario autenticado no tiene perfil de tecnico.")
    if not tecnico.estado:
        raise ValueError("El tecnico no se encuentra habilitado en el sistema.")

    asignacion_activa = get_asignacion_activa_by_tecnico_id(db, tecnico.id_tecnico)
    if payload.disponible and asignacion_activa:
        raise ValueError(
            "El tecnico tiene una asignacion activa y no puede marcarse como disponible."
        )

    try:
        tecnico_actualizado = update_disponibilidad_tecnico(
            db,
            id_tecnico=tecnico.id_tecnico,
            disponible=payload.disponible,
        )

        db.commit()
        db.refresh(tecnico_actualizado)

        return DisponibilidadTecnicoResponse.model_validate(tecnico_actualizado)
    except Exception:
        db.rollback()
        raise


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
