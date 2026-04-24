from sqlalchemy.orm import Session

from app.core.security.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.modules.autenticacion_seguridad.repository import (
    assign_rol_to_usuario,
    create_bitacora_sistema,
    create_usuario,
    create_cliente,
    create_taller,
    get_rol_by_nombre,
    get_tipo_taller_by_id,
    get_usuario_by_email,
    get_roles_by_usuario_id,    
)
from app.modules.autenticacion_seguridad.schemas import (
    LoginRequest,
    RegistroClienteRequest,
    RegistroClienteResponse,
    LogoutResponse,
    RegistroTallerRequest,
    RegistroTallerResponse,
    TokenResponse,
    UsuarioResponse,
    UsuarioMeResponse,
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
