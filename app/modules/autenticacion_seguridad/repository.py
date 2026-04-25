from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.modules.autenticacion_seguridad.models import (
    BitacoraSistema,
    Rol,
    Usuario,
    UsuarioRol,
)
from app.modules.gestion_clientes.models import Cliente
from app.modules.gestion_operativa_taller_tecnico.models import Taller, TipoTaller


def get_usuario_by_email(db: Session, email: str) -> Usuario | None:
    return db.execute(
        select(Usuario).where(Usuario.email == email)
    ).scalar_one_or_none()


def get_usuario_by_id(db: Session, id_usuario: int) -> Usuario | None:
    return db.execute(
        select(Usuario).where(Usuario.id_usuario == id_usuario)
    ).scalar_one_or_none()


def get_usuario_with_roles_by_id(db: Session, id_usuario: int) -> Usuario | None:
    return db.execute(
        select(Usuario)
        .options(joinedload(Usuario.usuario_roles).joinedload(UsuarioRol.rol))
        .where(Usuario.id_usuario == id_usuario)
    ).unique().scalar_one_or_none()


def get_usuarios_with_roles(db: Session) -> list[Usuario]:
    return list(
        db.execute(
            select(Usuario)
            .options(joinedload(Usuario.usuario_roles).joinedload(UsuarioRol.rol))
            .order_by(Usuario.id_usuario.asc())
        ).unique().scalars()
    )


def get_rol_by_nombre(db: Session, nombre: str) -> Rol | None:
    return db.execute(
        select(Rol).where(Rol.nombre == nombre)
    ).scalar_one_or_none()


def get_roles(db: Session) -> list[Rol]:
    return list(
        db.execute(
            select(Rol).order_by(Rol.nombre.asc())
        ).scalars()
    )


def get_tipos_taller(db: Session) -> list[TipoTaller]:
    return list(
        db.execute(
            select(TipoTaller).order_by(TipoTaller.nombre.asc())
        ).scalars()
    )


def get_roles_by_nombres(db: Session, nombres: list[str]) -> list[Rol]:
    if not nombres:
        return []
    return list(
        db.execute(
            select(Rol).where(Rol.nombre.in_(nombres))
        ).scalars()
    )


def get_tipo_taller_by_id(db: Session, id_tipo_taller: int) -> TipoTaller | None:
    return db.execute(
        select(TipoTaller).where(TipoTaller.id_tipo_taller == id_tipo_taller)
    ).scalar_one_or_none()


def create_usuario(
    db: Session,
    *,
    nombres: str,
    apellidos: str,
    celular: str,
    email: str,
    password_hash: str,
) -> Usuario:
    usuario = Usuario(
        nombres=nombres,
        apellidos=apellidos,
        celular=celular,
        email=email,
        password_hash=password_hash,
        estado=True,
    )
    db.add(usuario)
    db.flush()
    db.refresh(usuario)
    return usuario


def assign_rol_to_usuario(
    db: Session,
    *,
    id_usuario: int,
    id_rol: int,
) -> UsuarioRol:
    usuario_rol = UsuarioRol(
        id_usuario=id_usuario,
        id_rol=id_rol,
    )
    db.add(usuario_rol)
    db.flush()
    db.refresh(usuario_rol)
    return usuario_rol


def create_cliente(
    db: Session,
    *,
    id_usuario: int,
) -> Cliente:
    cliente = Cliente(
        id_usuario=id_usuario,
    )
    db.add(cliente)
    db.flush()
    db.refresh(cliente)
    return cliente


def create_taller(
    db: Session,
    *,
    id_usuario: int,
    id_tipo_taller: int,
    nombre_taller: str,
    nit: str,
    direccion: str,
    latitud,
    longitud,
    radio_cobertura_km,
) -> Taller:
    taller = Taller(
        id_usuario=id_usuario,
        id_tipo_taller=id_tipo_taller,
        nombre_taller=nombre_taller,
        nit=nit,
        direccion=direccion,
        latitud=latitud,
        longitud=longitud,
        radio_cobertura_km=radio_cobertura_km,
        disponible=True,
    )
    db.add(taller)
    db.flush()
    db.refresh(taller)
    return taller

def get_roles_by_usuario_id(db: Session, id_usuario: int) -> list[str]:
    return db.execute(
        select(Rol.nombre)
        .join(UsuarioRol, UsuarioRol.id_rol == Rol.id_rol)
        .where(UsuarioRol.id_usuario == id_usuario)
    ).scalars().all()


def delete_usuario_roles_by_usuario_id(db: Session, id_usuario: int) -> None:
    usuario_roles = db.execute(
        select(UsuarioRol).where(UsuarioRol.id_usuario == id_usuario)
    ).scalars().all()

    for usuario_rol in usuario_roles:
        db.delete(usuario_rol)

    db.flush()


def create_bitacora_sistema(
    db: Session,
    *,
    id_usuario: int,
    accion: str,
    modulo: str,
    descripcion: str | None = None,
    ip_origen: str | None = None,
) -> BitacoraSistema:
    bitacora = BitacoraSistema(
        id_usuario=id_usuario,
        accion=accion,
        modulo=modulo,
        descripcion=descripcion,
        ip_origen=ip_origen,
    )
    db.add(bitacora)
    db.flush()
    db.refresh(bitacora)
    return bitacora


def get_bitacora_sistema(
    db: Session,
    *,
    fecha_inicio: datetime | None = None,
    fecha_fin: datetime | None = None,
    id_usuario: int | None = None,
    modulo: str | None = None,
    accion: str | None = None,
) -> list[BitacoraSistema]:
    query = (
        select(BitacoraSistema)
        .options(joinedload(BitacoraSistema.usuario))
        .order_by(BitacoraSistema.fecha_hora.desc(), BitacoraSistema.id_bitacora.desc())
    )

    if fecha_inicio is not None:
        query = query.where(BitacoraSistema.fecha_hora >= fecha_inicio)
    if fecha_fin is not None:
        query = query.where(BitacoraSistema.fecha_hora <= fecha_fin)
    if id_usuario is not None:
        query = query.where(BitacoraSistema.id_usuario == id_usuario)
    if modulo:
        query = query.where(BitacoraSistema.modulo.ilike(f"%{modulo}%"))
    if accion:
        query = query.where(BitacoraSistema.accion.ilike(f"%{accion}%"))

    return list(db.execute(query).scalars())


def get_bitacora_sistema_by_id(
    db: Session,
    id_bitacora: int,
) -> BitacoraSistema | None:
    return db.execute(
        select(BitacoraSistema)
        .options(joinedload(BitacoraSistema.usuario))
        .where(BitacoraSistema.id_bitacora == id_bitacora)
    ).scalar_one_or_none()
