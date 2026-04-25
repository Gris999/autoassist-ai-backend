from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AnalisisIncidenteManualRequest(BaseModel):
    descripcion_texto: str | None = Field(default=None, max_length=2000)
    texto_evidencias: list[str] = Field(default_factory=list)
    latitud: Decimal | None = None
    longitud: Decimal | None = None

    model_config = ConfigDict(extra="forbid")


class PreguntasSugeridasResponse(BaseModel):
    preguntas_sugeridas: list[str] = Field(default_factory=list)


class AnalisisIncidenteResponse(PreguntasSugeridasResponse):
    id_incidente: int | None = None
    clasificacion_ia: str
    confianza_clasificacion: float = Field(ge=0.0, le=1.0)
    prioridad: str
    resumen_ia: str
    requiere_mas_info: bool


class SolicitudMasInformacionResponse(PreguntasSugeridasResponse):
    id_incidente: int
    id_usuario_destino: int
    solicitud_emitida: bool
    mensaje: str
    id_notificacion: int | None = None


class RegistrarEvidenciaProcesadaRequest(BaseModel):
    tipo_evidencia: str
    archivo_url: str | None = None
    texto_extraido: str
    descripcion: str | None = None

    model_config = ConfigDict(extra="forbid")


class EvidenciaProcesadaResponse(BaseModel):
    id_evidencia: int
    id_incidente: int
    tipo_evidencia: str
    archivo_url: str | None = None
    texto_extraido: str | None = None
    descripcion: str | None = None
    mensaje: str | None = None


class TallerCandidatoResponse(BaseModel):
    id_taller: int
    nombre_taller: str
    distancia_km: float
    puntaje_asignacion: float
    compatible_servicio: bool
    compatible_tipo_vehiculo: bool
    taller_disponible: bool
    tecnico_disponible: bool
    unidad_movil_disponible: bool
    estado_solicitud: str


class TallerRecomendadoResponse(BaseModel):
    id_taller: int
    nombre_taller: str
    distancia_km: float
    puntaje_asignacion: float


class AsignacionInteligenteResponse(BaseModel):
    id_incidente: int
    clasificacion_ia: str
    taller_recomendado: TallerRecomendadoResponse
    candidatos: list[TallerCandidatoResponse]
    total_candidatos: int
    mensaje: str
