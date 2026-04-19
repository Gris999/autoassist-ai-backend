from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.autenticacion_seguridad.models import Rol, Usuario, UsuarioRol
from app.modules.gestion_clientes.models import Cliente
from app.modules.gestion_operativa_taller_tecnico.models import Taller, TipoTaller


def get_usuario_by_email(db: Session, email: str) -> Usuario | None:
    return db.execute(
        select(Usuario).where(Usuario.email == email)
    ).scalar_one_or_none()


def get_rol_by_nombre(db: Session, nombre: str) -> Rol | None:
    return db.execute(
        select(Rol).where(Rol.nombre == nombre)
    ).scalar_one_or_none()


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