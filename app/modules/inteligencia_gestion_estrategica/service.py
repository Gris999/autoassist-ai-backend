import unicodedata
from decimal import Decimal

from sqlalchemy.orm import Session

from app.modules.inteligencia_gestion_estrategica.repository import (
    get_evidencia_textos_by_incidente_id,
    get_incidente_by_id,
    update_incidente_analysis_result,
)
from app.modules.inteligencia_gestion_estrategica.schemas import (
    AnalisisIncidenteManualRequest,
    AnalisisIncidenteResponse,
)


KEYWORDS_BY_CATEGORY: dict[str, tuple[str, ...]] = {
    "bateria": (
        "no enciende",
        "no arranca",
        "bateria",
        "descargada",
        "corriente",
        "tablero",
        "luces",
        "chispa",
    ),
    "llanta": (
        "llanta",
        "pinchazo",
        "pinchada",
        "rueda",
        "neumatico",
        "desinflada",
        "revento",
    ),
    "choque": (
        "choque",
        "colision",
        "accidente",
        "golpe",
        "impacto",
        "abollado",
        "parachoques",
    ),
    "motor": (
        "motor",
        "humo",
        "sobrecalentamiento",
        "calento",
        "temperatura",
        "aceite",
        "ruido extrano",
        "falla mecanica",
    ),
    "combustible": (
        "gasolina",
        "combustible",
        "sin gasolina",
        "sin combustible",
        "tanque vacio",
    ),
    "llave": (
        "llave",
        "perdi la llave",
        "llave dentro",
        "no puedo abrir",
        "cerradura",
    ),
}

PRIORITY_BY_CATEGORY: dict[str, str] = {
    "choque": "alta",
    "motor": "alta",
    "bateria": "media",
    "llanta": "media",
    "combustible": "media",
    "llave": "baja",
    "incierto": "baja",
}

QUESTIONS_BY_CATEGORY: dict[str, list[str]] = {
    "incierto": [
        "\u00bfEl vehiculo enciende?",
        "\u00bfTiene alguna llanta danada?",
        "\u00bfHay humo, fuga o golpe visible?",
        "\u00bfPuede enviar una foto del problema?",
    ],
    "bateria": [
        "\u00bfEl vehiculo intenta arrancar o no hace ningun sonido?",
        "\u00bfSe encienden las luces del tablero?",
        "\u00bfHace cuanto tiempo se cambio la bateria?",
    ],
    "llanta": [
        "\u00bfLa llanta esta desinflada o reventada?",
        "\u00bfTiene llanta de auxilio?",
        "\u00bfEsta en carretera o dentro de la ciudad?",
    ],
    "choque": [
        "\u00bfHay personas heridas?",
        "\u00bfEl vehiculo puede moverse?",
        "\u00bfEl dano es frontal, lateral o trasero?",
    ],
    "motor": [
        "\u00bfSale humo del motor?",
        "\u00bfLa temperatura esta elevada?",
        "\u00bfEscucha algun ruido extrano?",
    ],
    "combustible": [
        "\u00bfEl indicador marca reserva o vacio?",
        "\u00bfEl vehiculo se detuvo por falta de combustible?",
        "\u00bfSe encuentra en una zona segura para recibir auxilio?",
    ],
    "llave": [
        "\u00bfLa llave quedo dentro del vehiculo o se perdio?",
        "\u00bfCuenta con llave de repuesto?",
        "\u00bfLa cerradura responde o esta bloqueada?",
    ],
}


class IncidentNotFoundError(LookupError):
    pass


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _clean_texts(texts: list[str | None]) -> list[str]:
    return [text.strip() for text in texts if text and text.strip()]


def _build_text_corpus(
    descripcion_texto: str | None,
    texto_evidencias: list[str],
) -> tuple[list[str], str]:
    text_parts = _clean_texts([descripcion_texto, *texto_evidencias])
    return text_parts, _normalize_text(" ".join(text_parts))


def _match_keywords(text: str) -> dict[str, list[str]]:
    return {
        category: [keyword for keyword in keywords if _normalize_text(keyword) in text]
        for category, keywords in KEYWORDS_BY_CATEGORY.items()
    }


def _classify_incident(
    descripcion_texto: str | None,
    texto_evidencias: list[str],
) -> tuple[str, float, dict[str, list[str]], list[str]]:
    text_parts, normalized_text = _build_text_corpus(descripcion_texto, texto_evidencias)
    if not normalized_text:
        raise ValueError("No hay informacion suficiente para analizar el incidente.")

    matches_by_category = _match_keywords(normalized_text)
    scores = {
        category: len(matches)
        for category, matches in matches_by_category.items()
    }

    max_score = max(scores.values(), default=0)
    if max_score == 0:
        return "incierto", 0.0, matches_by_category, text_parts

    top_categories = [
        category
        for category, score in scores.items()
        if score == max_score
    ]
    if len(top_categories) > 1:
        return "incierto", 0.25, matches_by_category, text_parts

    category = top_categories[0]
    total_hits = sum(scores.values())
    dominance = max_score / total_hits if total_hits else 0.0

    confidence = 0.25 + (0.12 * max_score) + (0.18 * dominance)
    if descripcion_texto and descripcion_texto.strip():
        confidence += 0.05
    if texto_evidencias:
        confidence += 0.05

    confidence = round(min(confidence, 0.95), 2)
    return category, confidence, matches_by_category, text_parts


def _estimate_priority(category: str) -> str:
    return PRIORITY_BY_CATEGORY.get(category, "baja")


def _requires_more_information(
    *,
    category: str,
    confidence: float,
    text_parts: list[str],
) -> bool:
    if category == "incierto":
        return True
    if confidence < 0.55:
        return True
    return sum(len(part.split()) for part in text_parts) < 4


def _build_summary(
    *,
    category: str,
    priority: str,
    confidence: float,
    requires_more_info: bool,
    matches_by_category: dict[str, list[str]],
    evidence_count: int,
    has_location: bool,
) -> str:
    matched_keywords = matches_by_category.get(category, [])
    summary_parts = [
        f"Analisis automatico sugiere un incidente de tipo {category} con prioridad {priority}.",
        f"Confianza estimada: {confidence:.2f}.",
    ]

    if matched_keywords:
        summary_parts.append(
            "Indicadores detectados: " + ", ".join(matched_keywords[:4]) + "."
        )

    if evidence_count:
        summary_parts.append(
            f"Se consideraron {evidence_count} texto(s) extraidos de evidencias."
        )

    if has_location:
        summary_parts.append("La ubicacion del incidente se encuentra disponible.")

    if requires_more_info:
        summary_parts.append(
            "Se requiere mas informacion para confirmar la clasificacion preliminar."
        )

    return " ".join(summary_parts)


def _suggest_questions(category: str, requires_more_info: bool) -> list[str]:
    if not requires_more_info:
        return []
    return QUESTIONS_BY_CATEGORY.get(category, QUESTIONS_BY_CATEGORY["incierto"])


def _run_incident_analysis(
    *,
    id_incidente: int | None,
    descripcion_texto: str | None,
    texto_evidencias: list[str],
    latitud: Decimal | None,
    longitud: Decimal | None,
) -> AnalisisIncidenteResponse:
    category, confidence, matches_by_category, text_parts = _classify_incident(
        descripcion_texto,
        texto_evidencias,
    )
    priority = _estimate_priority(category)
    requires_more_info = _requires_more_information(
        category=category,
        confidence=confidence,
        text_parts=text_parts,
    )

    summary = _build_summary(
        category=category,
        priority=priority,
        confidence=confidence,
        requires_more_info=requires_more_info,
        matches_by_category=matches_by_category,
        evidence_count=len(texto_evidencias),
        has_location=latitud is not None and longitud is not None,
    )
    suggested_questions = _suggest_questions(category, requires_more_info)

    return AnalisisIncidenteResponse(
        id_incidente=id_incidente,
        clasificacion_ia=category,
        confianza_clasificacion=confidence,
        prioridad=priority,
        resumen_ia=summary,
        requiere_mas_info=requires_more_info,
        preguntas_sugeridas=suggested_questions,
    )


def analizar_incidente_manual_service(
    payload: AnalisisIncidenteManualRequest,
) -> AnalisisIncidenteResponse:
    return _run_incident_analysis(
        id_incidente=None,
        descripcion_texto=payload.descripcion_texto,
        texto_evidencias=_clean_texts(payload.texto_evidencias),
        latitud=payload.latitud,
        longitud=payload.longitud,
    )


def analizar_incidente_por_id_service(
    db: Session,
    id_incidente: int,
) -> AnalisisIncidenteResponse:
    incidente = get_incidente_by_id(db, id_incidente)
    if not incidente:
        raise IncidentNotFoundError("El incidente especificado no existe.")

    evidencia_textos = get_evidencia_textos_by_incidente_id(db, id_incidente)
    if not _clean_texts([incidente.descripcion_texto, *evidencia_textos]):
        raise ValueError(
            "El incidente no cuenta con descripcion_texto ni texto_extraido suficiente para analizar."
        )

    try:
        analysis = _run_incident_analysis(
            id_incidente=incidente.id_incidente,
            descripcion_texto=incidente.descripcion_texto,
            texto_evidencias=evidencia_textos,
            latitud=incidente.latitud,
            longitud=incidente.longitud,
        )
        update_incidente_analysis_result(
            db,
            incidente,
            clasificacion_ia=analysis.clasificacion_ia,
            confianza_clasificacion=analysis.confianza_clasificacion,
            resumen_ia=analysis.resumen_ia,
            requiere_mas_info=analysis.requiere_mas_info,
        )
        db.commit()
        return analysis
    except Exception:
        db.rollback()
        raise
