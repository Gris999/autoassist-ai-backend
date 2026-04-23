from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.modules.autenticacion_seguridad.models import Usuario
from app.modules.gestion_incidentes_atencion.models import (
    AsignacionServicio,
    EstadoServicio,
    Incidente,
)
from app.modules.gestion_operativa_taller_tecnico.models import (
    Taller,
    TallerAuxilio,
    Tecnico,
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


def get_tecnico_by_usuario_id(db: Session, id_usuario: int) -> Tecnico | None:
    return db.execute(
        select(Tecnico).where(Tecnico.id_usuario == id_usuario)
    ).scalar_one_or_none()


def get_tecnico_by_id(db: Session, id_tecnico: int) -> Tecnico | None:
    return db.execute(
        select(Tecnico).where(Tecnico.id_tecnico == id_tecnico)
    ).scalar_one_or_none()


def get_tecnicos_by_taller_id(db: Session, id_taller: int) -> list[Tecnico]:
    return list(
        db.execute(
            select(Tecnico)
            .options(joinedload(Tecnico.usuario))
            .where(Tecnico.id_taller == id_taller)
            .order_by(Tecnico.id_tecnico.desc())
        ).scalars()
    )


def get_tecnico_with_usuario_by_id(db: Session, id_tecnico: int) -> Tecnico | None:
    return db.execute(
        select(Tecnico)
        .options(joinedload(Tecnico.usuario))
        .where(Tecnico.id_tecnico == id_tecnico)
    ).scalar_one_or_none()


def update_disponibilidad_tecnico(
    db: Session,
    *,
    id_tecnico: int,
    disponible: bool,
) -> Tecnico:
    tecnico = get_tecnico_by_id(db, id_tecnico)
    if tecnico:
        tecnico.disponible = disponible
        db.flush()
        db.refresh(tecnico)
    return tecnico


def get_tecnicos_disponibles(db: Session) -> list[Tecnico]:
    return list(
        db.execute(
            select(Tecnico).where(Tecnico.disponible == True, Tecnico.estado == True)
        ).scalars()
    )


def create_tecnico(
    db: Session,
    *,
    id_usuario: int,
    id_taller: int,
    telefono_contacto: str,
    disponible: bool,
    estado: bool,
) -> Tecnico:
    tecnico = Tecnico(
        id_usuario=id_usuario,
        id_taller=id_taller,
        telefono_contacto=telefono_contacto,
        disponible=disponible,
        estado=estado,
    )
    db.add(tecnico)
    db.flush()
    db.refresh(tecnico)
    return tecnico


def update_usuario_tecnico(
    db: Session,
    usuario: Usuario,
    *,
    nombres: str | None = None,
    apellidos: str | None = None,
    celular: str | None = None,
    email: str | None = None,
    estado: bool | None = None,
) -> Usuario:
    if nombres is not None:
        usuario.nombres = nombres
    if apellidos is not None:
        usuario.apellidos = apellidos
    if celular is not None:
        usuario.celular = celular
    if email is not None:
        usuario.email = email
    if estado is not None:
        usuario.estado = estado
    db.flush()
    db.refresh(usuario)
    return usuario


def update_tecnico(
    db: Session,
    tecnico: Tecnico,
    *,
    telefono_contacto: str | None = None,
    disponible: bool | None = None,
) -> Tecnico:
    if telefono_contacto is not None:
        tecnico.telefono_contacto = telefono_contacto
    if disponible is not None:
        tecnico.disponible = disponible
    db.flush()
    db.refresh(tecnico)
    return tecnico


def update_estado_tecnico(
    db: Session,
    tecnico: Tecnico,
    *,
    estado: bool,
) -> Tecnico:
    tecnico.estado = estado
    if not estado:
        tecnico.disponible = False
    db.flush()
    db.refresh(tecnico)
    return tecnico


def get_asignacion_activa_by_tecnico_id(
    db: Session,
    id_tecnico: int,
) -> AsignacionServicio | None:
    return (
        db.execute(
            select(AsignacionServicio)
            .join(Incidente, AsignacionServicio.id_incidente == Incidente.id_incidente)
            .join(
                EstadoServicio,
                Incidente.id_estado_servicio_actual == EstadoServicio.id_estado_servicio,
            )
            .where(
                AsignacionServicio.id_tecnico == id_tecnico,
                EstadoServicio.nombre.notin_(["FINALIZADO", "CANCELADO"]),
            )
            .order_by(AsignacionServicio.fecha_asignacion.desc())
        )
        .scalars()
        .first()
    )
