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
