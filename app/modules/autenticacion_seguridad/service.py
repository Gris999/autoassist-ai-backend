from datetime import datetime

from sqlalchemy.orm import Session

from app.core.security.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.modules.autenticacion_seguridad.repository import (
    assign_rol_to_usuario,
    delete_usuario_roles_by_usuario_id,
    get_bitacora_sistema,
    get_bitacora_sistema_by_id,
    create_bitacora_sistema,
    create_usuario,
    create_cliente,
    create_taller,
    get_rol_by_nombre,
    get_roles,
    get_roles_by_nombres,
    get_usuario_by_id,
    get_usuario_with_roles_by_id,
    get_usuarios_with_roles,
    get_tipo_taller_by_id,
    get_usuario_by_email,
    get_roles_by_usuario_id,    
)
from app.modules.autenticacion_seguridad.schemas import (
    LoginRequest,
    BitacoraSistemaDetailResponse,
    BitacoraSistemaResponse,
    RegistroClienteRequest,
    RegistroClienteResponse,
    LogoutResponse,
    RolResponse,
    RegistroTallerRequest,
    RegistroTallerResponse,
    TokenResponse,
    UsuarioRolesListResponse,
    UsuarioRolesUpdateRequest,
    UsuarioRolesUpdateResponse,
    UsuarioResponse,
    UsuarioMeResponse,
    BitacoraUsuarioResponse,
)


def register_cliente_service(
    db: Session,
    payload: RegistroClienteRequest,
) -> RegistroClienteResponse:
    existing_user = get_usuario_by_email(db, payload.email)
    if existing_user:
        raise ValueError("Ya existe un usuario registrado con ese email.")

    rol_cliente = get_rol_by_nombre(db, "CLIENTE")
    if not rol_cliente:
        raise ValueError("No existe el rol CLIENTE en la base de datos.")

    try:
        usuario = create_usuario(
            db,
            nombres=payload.nombres,
            apellidos=payload.apellidos,
            celular=payload.celular,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )

        assign_rol_to_usuario(
            db,
            id_usuario=usuario.id_usuario,
            id_rol=rol_cliente.id_rol,
        )

        create_cliente(
            db,
            id_usuario=usuario.id_usuario,
        )

        db.commit()
        db.refresh(usuario)

        return RegistroClienteResponse(
            usuario=UsuarioResponse.model_validate(usuario),
            rol="CLIENTE",
        )
    except Exception:
        db.rollback()
        raise


def register_taller_service(
    db: Session,
    payload: RegistroTallerRequest,
) -> RegistroTallerResponse:
    existing_user = get_usuario_by_email(db, payload.email)
    if existing_user:
        raise ValueError("Ya existe un usuario registrado con ese email.")

    rol_taller = get_rol_by_nombre(db, "TALLER")
    if not rol_taller:
        raise ValueError("No existe el rol TALLER en la base de datos.")

    tipo_taller = get_tipo_taller_by_id(db, payload.id_tipo_taller)
    if not tipo_taller:
        raise ValueError("El tipo de taller seleccionado no existe.")

    try:
        usuario = create_usuario(
            db,
            nombres=payload.nombres,
            apellidos=payload.apellidos,
            celular=payload.celular,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )

        assign_rol_to_usuario(
            db,
            id_usuario=usuario.id_usuario,
            id_rol=rol_taller.id_rol,
        )

        create_taller(
            db,
            id_usuario=usuario.id_usuario,
            id_tipo_taller=payload.id_tipo_taller,
            nombre_taller=payload.nombre_taller,
            nit=payload.nit,
            direccion=payload.direccion,
            latitud=payload.latitud,
            longitud=payload.longitud,
            radio_cobertura_km=payload.radio_cobertura_km,
        )

        db.commit()
        db.refresh(usuario)

        return RegistroTallerResponse(
            usuario=UsuarioResponse.model_validate(usuario),
            rol="TALLER",
            nombre_taller=payload.nombre_taller,
        )
    except Exception:
        db.rollback()
        raise


def login_service(
    db: Session,
    payload: LoginRequest,
) -> TokenResponse:
    usuario = get_usuario_by_email(db, payload.email)

    if not usuario:
        raise ValueError("Credenciales inválidas.")

    if not usuario.estado:
        raise ValueError("El usuario se encuentra inactivo.")

    if not verify_password(payload.password, usuario.password_hash):
        raise ValueError("Credenciales inválidas.")

    token = create_access_token(subject=str(usuario.id_usuario))

    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )

def get_me_service(
    db: Session,
    current_user,
) -> UsuarioMeResponse:
    roles = get_roles_by_usuario_id(db, current_user.id_usuario)

    return UsuarioMeResponse(
        id_usuario=current_user.id_usuario,
        nombres=current_user.nombres,
        apellidos=current_user.apellidos,
        celular=current_user.celular,
        email=current_user.email,
        estado=current_user.estado,
        fecha_registro=current_user.fecha_registro,
        roles=roles,
    )


def logout_service(
    db: Session,
    current_user,
    *,
    ip_origen: str | None = None,
) -> LogoutResponse:
    try:
        create_bitacora_sistema(
            db,
            id_usuario=current_user.id_usuario,
            accion="LOGOUT",
            modulo="AUTENTICACION_SEGURIDAD",
            descripcion="Cierre de sesion del usuario.",
            ip_origen=ip_origen,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    return LogoutResponse(
        message=(
            "Sesion cerrada correctamente."
        ),
        invalidacion_servidor=False,
    )


def _to_bitacora_usuario_response(usuario) -> BitacoraUsuarioResponse | None:
    if not usuario:
        return None
    return BitacoraUsuarioResponse(
        id_usuario=usuario.id_usuario,
        nombres=usuario.nombres,
        apellidos=usuario.apellidos,
        email=usuario.email,
    )


def _to_bitacora_sistema_response(bitacora) -> BitacoraSistemaResponse:
    return BitacoraSistemaResponse(
        id_bitacora=bitacora.id_bitacora,
        fecha_hora=bitacora.fecha_hora,
        usuario=_to_bitacora_usuario_response(bitacora.usuario),
        accion=bitacora.accion,
        modulo=bitacora.modulo,
        descripcion=bitacora.descripcion,
        ip_origen=bitacora.ip_origen,
    )


def _to_bitacora_sistema_detail_response(bitacora) -> BitacoraSistemaDetailResponse:
    return BitacoraSistemaDetailResponse(
        id_bitacora=bitacora.id_bitacora,
        id_usuario=bitacora.id_usuario,
        fecha_hora=bitacora.fecha_hora,
        usuario=_to_bitacora_usuario_response(bitacora.usuario),
        accion=bitacora.accion,
        modulo=bitacora.modulo,
        descripcion=bitacora.descripcion,
        ip_origen=bitacora.ip_origen,
    )


def listar_bitacora_sistema_service(
    db: Session,
    *,
    fecha_inicio: datetime | None = None,
    fecha_fin: datetime | None = None,
    id_usuario: int | None = None,
    modulo: str | None = None,
    accion: str | None = None,
) -> list[BitacoraSistemaResponse]:
    if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
        raise ValueError("El rango de fechas es inconsistente.")

    bitacoras = get_bitacora_sistema(
        db,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        id_usuario=id_usuario,
        modulo=modulo,
        accion=accion,
    )
    return [_to_bitacora_sistema_response(bitacora) for bitacora in bitacoras]


def obtener_bitacora_sistema_service(
    db: Session,
    id_bitacora: int,
) -> BitacoraSistemaDetailResponse:
    bitacora = get_bitacora_sistema_by_id(db, id_bitacora)
    if not bitacora:
        raise ValueError("El registro de bitacora no existe.")
    return _to_bitacora_sistema_detail_response(bitacora)


def _to_usuario_roles_list_response(usuario: Usuario) -> UsuarioRolesListResponse:
    return UsuarioRolesListResponse(
        id_usuario=usuario.id_usuario,
        nombres=usuario.nombres,
        apellidos=usuario.apellidos,
        celular=usuario.celular,
        email=usuario.email,
        estado=usuario.estado,
        fecha_registro=usuario.fecha_registro,
        roles=sorted(usuario_rol.rol.nombre for usuario_rol in usuario.usuario_roles),
    )


def listar_roles_service(db: Session) -> list[RolResponse]:
    roles = get_roles(db)
    return [RolResponse.model_validate(rol) for rol in roles]


def listar_usuarios_roles_service(db: Session) -> list[UsuarioRolesListResponse]:
    usuarios = get_usuarios_with_roles(db)
    return [_to_usuario_roles_list_response(usuario) for usuario in usuarios]


def actualizar_roles_usuario_service(
    db: Session,
    current_user,
    id_usuario: int,
    payload: UsuarioRolesUpdateRequest,
    *,
    ip_origen: str | None = None,
) -> UsuarioRolesUpdateResponse:
    nombres_roles = [rol.strip().upper() for rol in payload.roles if rol.strip()]
    if not nombres_roles:
        raise ValueError("Debe enviar al menos un rol valido.")
    if len(set(nombres_roles)) != len(nombres_roles):
        raise ValueError("La lista de roles contiene valores duplicados.")

    usuario_objetivo = get_usuario_by_id(db, id_usuario)
    if not usuario_objetivo:
        raise ValueError("El usuario objetivo no existe.")

    roles = get_roles_by_nombres(db, nombres_roles)
    if len(roles) != len(nombres_roles):
        roles_encontrados = {rol.nombre for rol in roles}
        roles_faltantes = sorted(set(nombres_roles) - roles_encontrados)
        raise ValueError(
            f"Los siguientes roles no existen: {', '.join(roles_faltantes)}."
        )

    try:
        delete_usuario_roles_by_usuario_id(db, id_usuario)
        for rol in roles:
            assign_rol_to_usuario(
                db,
                id_usuario=id_usuario,
                id_rol=rol.id_rol,
            )

        create_bitacora_sistema(
            db,
            id_usuario=current_user.id_usuario,
            accion="ACTUALIZAR_ROLES_USUARIO",
            modulo="AUTENTICACION_SEGURIDAD",
            descripcion=(
                f"Actualizacion de roles del usuario {id_usuario}: "
                f"{', '.join(sorted(nombres_roles))}."
            ),
            ip_origen=ip_origen,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    usuario_actualizado = get_usuario_with_roles_by_id(db, id_usuario)
    return UsuarioRolesUpdateResponse(
        id_usuario=usuario_actualizado.id_usuario,
        roles=sorted(
            usuario_rol.rol.nombre for usuario_rol in usuario_actualizado.usuario_roles
        ),
        mensaje="Roles actualizados correctamente.",
    )
