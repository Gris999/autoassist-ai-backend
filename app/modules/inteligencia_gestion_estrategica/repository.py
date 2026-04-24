from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.autenticacion_seguridad.models import Usuario
from app.modules.gestion_clientes.models import Cliente
from app.modules.gestion_incidentes_atencion.models import Evidencia, Incidente
from app.modules.seguimiento_monitoreo_servicio.models import Notificacion


def get_incidente_by_id(db: Session, id_incidente: int) -> Incidente | None:
    return db.execute(
        select(Incidente).where(Incidente.id_incidente == id_incidente)
    ).scalar_one_or_none()


def get_evidencia_textos_by_incidente_id(db: Session, id_incidente: int) -> list[str]:
    return [
        texto
        for texto in db.execute(
            select(Evidencia.texto_extraido).where(
                Evidencia.id_incidente == id_incidente,
                Evidencia.texto_extraido.is_not(None),
            )
        ).scalars()
        if texto and texto.strip()
    ]


def update_incidente_analysis_result(
    db: Session,
    incidente: Incidente,
    *,
    clasificacion_ia: str,
    confianza_clasificacion: float,
    resumen_ia: str,
    requiere_mas_info: bool,
) -> Incidente:
    incidente.clasificacion_ia = clasificacion_ia
    incidente.confianza_clasificacion = round(confianza_clasificacion, 2)
    incidente.resumen_ia = resumen_ia
    incidente.requiere_mas_info = requiere_mas_info
    db.flush()
    db.refresh(incidente)
    return incidente


def get_cliente_by_id(db: Session, id_cliente: int) -> Cliente | None:
    return db.execute(
        select(Cliente).where(Cliente.id_cliente == id_cliente)
    ).scalar_one_or_none()


def get_usuario_by_id(db: Session, id_usuario: int) -> Usuario | None:
    return db.execute(
        select(Usuario).where(Usuario.id_usuario == id_usuario)
    ).scalar_one_or_none()


def get_pending_notification_by_incidente_usuario_tipo(
    db: Session,
    *,
    id_incidente: int,
    id_usuario: int,
    tipo_notificacion: str,
) -> Notificacion | None:
    return db.execute(
        select(Notificacion).where(
            Notificacion.id_incidente == id_incidente,
            Notificacion.id_usuario == id_usuario,
            Notificacion.tipo_notificacion == tipo_notificacion,
            Notificacion.leido == False,
        )
    ).scalar_one_or_none()


def create_notification(
    db: Session,
    *,
    id_usuario: int,
    id_incidente: int,
    titulo: str,
    mensaje: str,
    tipo_notificacion: str,
) -> Notificacion:
    notification = Notificacion(
        id_usuario=id_usuario,
        id_incidente=id_incidente,
        titulo=titulo,
        mensaje=mensaje,
        tipo_notificacion=tipo_notificacion,
        leido=False,
    )
    db.add(notification)
    db.flush()
    db.refresh(notification)
    return notification
