from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.gestion_incidentes_atencion.models import Evidencia, Incidente


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
