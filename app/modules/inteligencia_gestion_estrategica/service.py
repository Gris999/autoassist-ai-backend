import unicodedata
from decimal import Decimal
from math import asin, cos, radians, sin, sqrt

from sqlalchemy.orm import Session

from app.modules.inteligencia_gestion_estrategica.repository import (
    create_solicitud_taller,
    create_processed_evidence,
    create_notification,
    get_cliente_by_id,
    get_evidencia_textos_by_incidente_id,
    get_incidente_by_id,
    get_incidente_with_assignment_context,
    get_pending_notification_by_incidente_usuario_tipo,
    get_solicitud_taller_by_incidente_and_taller,
    get_usuario_by_id,
    list_available_talleres_with_resources,
    list_evidences_by_incidente_id,
    update_solicitud_taller_candidate_data,
    update_incidente_analysis_result,
)
from app.modules.inteligencia_gestion_estrategica.schemas import (
    AnalisisIncidenteManualRequest,
    AnalisisIncidenteResponse,
    AsignacionInteligenteResponse,
    EvidenciaProcesadaResponse,
    RegistrarEvidenciaProcesadaRequest,
    SolicitudMasInformacionResponse,
    TallerCandidatoResponse,
    TallerRecomendadoResponse,
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

ALLOWED_EVIDENCE_TYPES = {
    "TEXTO",
    "AUDIO_TRANSCRITO",
    "IMAGEN_ANALIZADA",
}

CLASSIFICATION_SERVICE_KEYWORDS = {
    "bateria": ("bateria", "electrico", "corriente"),
    "llanta": ("llanta", "rueda", "neumatico", "pinchazo"),
    "choque": ("remolque", "grua", "choque", "accidente"),
    "motor": ("mecanica", "motor", "remolque", "grua"),
    "combustible": ("combustible", "gasolina"),
    "llave": ("llave", "cerrajeria", "apertura"),
}

ESTADOS_SOLICITUD_EXCLUIDOS = {"RECHAZADA"}
ESTADOS_INCIDENTE_NO_APTOS_PARA_ASIGNACION = {"FINALIZADO", "CANCELADO"}
ESTADO_SOLICITUD_INTELIGENTE = "PENDIENTE"


class IncidentNotFoundError(LookupError):
    pass


class IncidentDoesNotRequireMoreInformationError(ValueError):
    pass


class IncidentClientNotFoundError(LookupError):
    pass


class IncidentUserNotFoundError(LookupError):
    pass


class IncidentNotAnalyzedError(ValueError):
    pass


class IncidentClassificationInsufficientError(ValueError):
    pass


class IncidentLocationInvalidError(ValueError):
    pass


class IncidentVehicleNotFoundError(ValueError):
    pass


class NoCandidateTallerFoundError(LookupError):
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


def _get_questions_for_incident_classification(clasificacion_ia: str | None) -> list[str]:
    normalized_category = (clasificacion_ia or "").strip().lower()
    if not normalized_category or normalized_category not in QUESTIONS_BY_CATEGORY:
        normalized_category = "incierto"
    return QUESTIONS_BY_CATEGORY[normalized_category]


def _serialize_archivo_url(archivo_url: str | None) -> str | None:
    if not archivo_url:
        return None
    return archivo_url


def _to_evidencia_procesada_response(
    evidencia,
    *,
    mensaje: str | None = None,
) -> EvidenciaProcesadaResponse:
    return EvidenciaProcesadaResponse(
        id_evidencia=evidencia.id_evidencia,
        id_incidente=evidencia.id_incidente,
        tipo_evidencia=evidencia.tipo_evidencia,
        archivo_url=_serialize_archivo_url(evidencia.archivo_url),
        texto_extraido=evidencia.texto_extraido,
        descripcion=evidencia.descripcion,
        mensaje=mensaje,
    )


def _normalize_evidence_type(tipo_evidencia: str) -> str:
    normalized_type = tipo_evidencia.strip().upper()
    if normalized_type not in ALLOWED_EVIDENCE_TYPES:
        raise ValueError(
            "tipo_evidencia no permitido. Use TEXTO, AUDIO_TRANSCRITO o IMAGEN_ANALIZADA."
        )
    return normalized_type


def _normalize_service_name(value: str | None) -> str:
    if not value:
        return ""
    return _normalize_text(value)


def _get_service_keywords_for_classification(clasificacion_ia: str) -> tuple[str, ...]:
    normalized_category = clasificacion_ia.strip().lower()
    if normalized_category not in CLASSIFICATION_SERVICE_KEYWORDS:
        raise IncidentClassificationInsufficientError(
            "La clasificacion del incidente no es suficiente para asignar taller."
        )
    return CLASSIFICATION_SERVICE_KEYWORDS[normalized_category]


def _haversine_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    radius_km = 6371.0
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    a = (
        sin(delta_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(delta_lon / 2) ** 2
    )
    c = 2 * asin(sqrt(a))
    return radius_km * c


def _calculate_distance_score(distance_km: float, coverage_km: float) -> float:
    if distance_km <= 2:
        return 10.0
    if distance_km <= 5:
        return 8.0
    if distance_km <= 10:
        return 5.0
    if distance_km <= coverage_km:
        return 3.0
    return 0.0


def _has_available_tecnico(taller) -> bool:
    return any(tecnico.estado and tecnico.disponible for tecnico in taller.tecnicos)


def _has_available_unidad_movil(taller) -> bool:
    return any(
        unidad_movil.estado and unidad_movil.disponible
        for unidad_movil in taller.unidades_moviles
    )


def _is_vehicle_type_compatible(taller, id_tipo_vehiculo: int) -> bool:
    return any(
        taller_tipo_vehiculo.id_tipo_vehiculo == id_tipo_vehiculo
        for taller_tipo_vehiculo in taller.talleres_tipo_vehiculo
    )


def _get_feasible_auxilio_for_classification(
    taller,
    *,
    clasificacion_ia: str,
    unidad_movil_disponible: bool,
):
    keywords = _get_service_keywords_for_classification(clasificacion_ia)
    compatible_services = []
    for taller_auxilio in taller.talleres_auxilio:
        tipo_auxilio = taller_auxilio.tipo_auxilio
        if not tipo_auxilio or not tipo_auxilio.estado or not taller_auxilio.disponible:
            continue

        service_name = _normalize_service_name(tipo_auxilio.nombre)
        if any(keyword in service_name for keyword in keywords):
            compatible_services.append(taller_auxilio)

    if not compatible_services:
        return None

    feasible_services = [
        service
        for service in compatible_services
        if not service.tipo_auxilio.requiere_unidad_movil or unidad_movil_disponible
    ]
    if not feasible_services:
        return None

    return feasible_services[0]


def _validate_incidente_for_intelligent_assignment(incidente) -> None:
    if not incidente:
        raise IncidentNotFoundError("Incidente no encontrado.")
    if incidente.clasificacion_ia is None:
        raise IncidentNotAnalyzedError(
            "El incidente debe ser analizado primero por CU25."
        )
    if incidente.requiere_mas_info:
        raise IncidentDoesNotRequireMoreInformationError(
            "El incidente aun requiere mas informacion para asignar taller."
        )
    if incidente.clasificacion_ia.strip().lower() == "incierto":
        raise IncidentClassificationInsufficientError(
            "La clasificacion del incidente no es suficiente para asignar taller."
        )
    if incidente.latitud is None or incidente.longitud is None:
        raise IncidentLocationInvalidError(
            "El incidente no tiene ubicacion valida para asignar taller."
        )
    if incidente.vehiculo is None or incidente.vehiculo.id_tipo_vehiculo is None:
        raise IncidentVehicleNotFoundError(
            "El incidente no tiene un vehiculo asociado valido."
        )
    if (
        incidente.estado_servicio_actual
        and incidente.estado_servicio_actual.nombre in ESTADOS_INCIDENTE_NO_APTOS_PARA_ASIGNACION
    ):
        raise ValueError("El incidente no se encuentra en un estado apto para asignacion.")
    if incidente.asignacion_servicio is not None:
        raise ValueError("El incidente ya tiene una asignacion operativa registrada.")


def _build_taller_candidate_response(
    *,
    taller,
    distancia_km: float,
    puntaje_asignacion: float,
    taller_disponible: bool,
    tecnico_disponible: bool,
    unidad_movil_disponible: bool,
    estado_solicitud: str,
) -> TallerCandidatoResponse:
    return TallerCandidatoResponse(
        id_taller=taller.id_taller,
        nombre_taller=taller.nombre_taller,
        distancia_km=round(distancia_km, 2),
        puntaje_asignacion=round(puntaje_asignacion, 2),
        compatible_servicio=True,
        compatible_tipo_vehiculo=True,
        taller_disponible=taller_disponible,
        tecnico_disponible=tecnico_disponible,
        unidad_movil_disponible=unidad_movil_disponible,
        estado_solicitud=estado_solicitud,
    )


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


def solicitar_mas_informacion_incidente_service(
    db: Session,
    id_incidente: int,
) -> SolicitudMasInformacionResponse:
    incidente = get_incidente_by_id(db, id_incidente)
    if not incidente:
        raise IncidentNotFoundError("Incidente no encontrado.")

    if not incidente.requiere_mas_info:
        raise IncidentDoesNotRequireMoreInformationError(
            "El incidente ya cuenta con informacion suficiente."
        )

    cliente = get_cliente_by_id(db, incidente.id_cliente)
    if not cliente:
        raise IncidentClientNotFoundError(
            "No existe cliente asociado al incidente."
        )

    usuario = get_usuario_by_id(db, cliente.id_usuario)
    if not usuario:
        raise IncidentUserNotFoundError(
            "No existe usuario asociado al incidente."
        )

    preguntas_sugeridas = _get_questions_for_incident_classification(
        incidente.clasificacion_ia
    )
    mensaje_base = (
        "Se requiere informacion adicional para analizar correctamente el incidente."
    )
    mensaje_notificacion = (
        mensaje_base
        + " Preguntas sugeridas: "
        + " ".join(preguntas_sugeridas)
    )

    existing_notification = get_pending_notification_by_incidente_usuario_tipo(
        db,
        id_incidente=incidente.id_incidente,
        id_usuario=usuario.id_usuario,
        tipo_notificacion="SOLICITUD_MAS_INFORMACION",
    )
    if existing_notification:
        return SolicitudMasInformacionResponse(
            id_incidente=incidente.id_incidente,
            id_usuario_destino=usuario.id_usuario,
            solicitud_emitida=False,
            mensaje=(
                "Ya existe una solicitud pendiente de mas informacion para este incidente."
            ),
            preguntas_sugeridas=preguntas_sugeridas,
            id_notificacion=existing_notification.id_notificacion,
        )

    try:
        notification = create_notification(
            db,
            id_usuario=usuario.id_usuario,
            id_incidente=incidente.id_incidente,
            titulo="Solicitud de mas informacion del incidente",
            mensaje=mensaje_notificacion,
            tipo_notificacion="SOLICITUD_MAS_INFORMACION",
        )
        db.commit()
        return SolicitudMasInformacionResponse(
            id_incidente=incidente.id_incidente,
            id_usuario_destino=usuario.id_usuario,
            solicitud_emitida=True,
            mensaje=mensaje_base,
            preguntas_sugeridas=preguntas_sugeridas,
            id_notificacion=notification.id_notificacion,
        )
    except Exception:
        db.rollback()
        raise


def registrar_evidencia_procesada_service(
    db: Session,
    id_incidente: int,
    payload: RegistrarEvidenciaProcesadaRequest,
) -> EvidenciaProcesadaResponse:
    incidente = get_incidente_by_id(db, id_incidente)
    if not incidente:
        raise IncidentNotFoundError("Incidente no encontrado.")

    texto_extraido = payload.texto_extraido.strip()
    if not texto_extraido:
        raise ValueError("texto_extraido no puede estar vacio.")

    tipo_evidencia = _normalize_evidence_type(payload.tipo_evidencia)
    archivo_url = (payload.archivo_url or "").strip()
    descripcion = payload.descripcion.strip() if payload.descripcion else None

    try:
        evidencia = create_processed_evidence(
            db,
            id_incidente=incidente.id_incidente,
            tipo_evidencia=tipo_evidencia,
            archivo_url=archivo_url,
            texto_extraido=texto_extraido,
            descripcion=descripcion,
        )
        db.commit()
        return _to_evidencia_procesada_response(
            evidencia,
            mensaje=(
                "Evidencia procesada registrada correctamente. "
                "Se recomienda volver a ejecutar CU25 para reanalizar el incidente."
            ),
        )
    except Exception:
        db.rollback()
        raise


def listar_evidencias_procesadas_incidente_service(
    db: Session,
    id_incidente: int,
) -> list[EvidenciaProcesadaResponse]:
    incidente = get_incidente_by_id(db, id_incidente)
    if not incidente:
        raise IncidentNotFoundError("Incidente no encontrado.")

    evidencias = list_evidences_by_incidente_id(db, id_incidente)
    return [
        _to_evidencia_procesada_response(evidencia)
        for evidencia in evidencias
    ]


def asignar_taller_inteligentemente_service(
    db: Session,
    id_incidente: int,
) -> AsignacionInteligenteResponse:
    incidente = get_incidente_with_assignment_context(db, id_incidente)
    _validate_incidente_for_intelligent_assignment(incidente)

    incident_lat = float(incidente.latitud)
    incident_lon = float(incidente.longitud)
    vehicle_type_id = incidente.vehiculo.id_tipo_vehiculo

    talleres = list_available_talleres_with_resources(db)
    candidatos_registrados: list[TallerCandidatoResponse] = []

    for taller in talleres:
        if taller.latitud is None or taller.longitud is None or taller.radio_cobertura_km is None:
            continue

        taller_disponible = bool(taller.disponible)
        tecnico_disponible = _has_available_tecnico(taller)
        unidad_movil_disponible = _has_available_unidad_movil(taller)
        compatible_tipo_vehiculo = _is_vehicle_type_compatible(taller, vehicle_type_id)

        if not taller_disponible or not tecnico_disponible or not compatible_tipo_vehiculo:
            continue

        auxilio_compatible = _get_feasible_auxilio_for_classification(
            taller,
            clasificacion_ia=incidente.clasificacion_ia,
            unidad_movil_disponible=unidad_movil_disponible,
        )
        if auxilio_compatible is None:
            continue

        distance_km = _haversine_distance_km(
            incident_lat,
            incident_lon,
            float(taller.latitud),
            float(taller.longitud),
        )
        coverage_km = float(taller.radio_cobertura_km)
        if distance_km > coverage_km:
            continue

        distance_score = _calculate_distance_score(distance_km, coverage_km)
        unit_score = 10.0 if (
            unidad_movil_disponible or not auxilio_compatible.tipo_auxilio.requiere_unidad_movil
        ) else 0.0
        total_score = 35.0 + 20.0 + 15.0 + 10.0 + unit_score + distance_score

        existing_solicitud = get_solicitud_taller_by_incidente_and_taller(
            db,
            id_incidente=incidente.id_incidente,
            id_taller=taller.id_taller,
        )
        if existing_solicitud and existing_solicitud.estado_solicitud in ESTADOS_SOLICITUD_EXCLUIDOS:
            continue

        if existing_solicitud:
            solicitud = update_solicitud_taller_candidate_data(
                db,
                existing_solicitud,
                distancia_km=distance_km,
                puntaje_asignacion=total_score,
            )
        else:
            solicitud = create_solicitud_taller(
                db,
                id_incidente=incidente.id_incidente,
                id_taller=taller.id_taller,
                distancia_km=distance_km,
                puntaje_asignacion=total_score,
                estado_solicitud=ESTADO_SOLICITUD_INTELIGENTE,
            )

        candidatos_registrados.append(
            _build_taller_candidate_response(
                taller=taller,
                distancia_km=distance_km,
                puntaje_asignacion=total_score,
                taller_disponible=taller_disponible,
                tecnico_disponible=tecnico_disponible,
                unidad_movil_disponible=unidad_movil_disponible,
                estado_solicitud=solicitud.estado_solicitud,
            )
        )

    if not candidatos_registrados:
        db.rollback()
        raise NoCandidateTallerFoundError(
            "No existen talleres disponibles y compatibles para atender el incidente."
        )

    candidatos_registrados.sort(
        key=lambda candidato: (
            -candidato.puntaje_asignacion,
            candidato.distancia_km,
        ),
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    taller_recomendado = candidatos_registrados[0]
    return AsignacionInteligenteResponse(
        id_incidente=incidente.id_incidente,
        clasificacion_ia=incidente.clasificacion_ia,
        taller_recomendado=TallerRecomendadoResponse(
            id_taller=taller_recomendado.id_taller,
            nombre_taller=taller_recomendado.nombre_taller,
            distancia_km=taller_recomendado.distancia_km,
            puntaje_asignacion=taller_recomendado.puntaje_asignacion,
        ),
        candidatos=candidatos_registrados,
        total_candidatos=len(candidatos_registrados),
        mensaje="Taller recomendado correctamente.",
    )
