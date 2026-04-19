from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class IncidenteCreateRequest(BaseModel):
    id_vehiculo: int
    id_tipo_incidente: int
    titulo: str = Field(min_length=5, max_length=150)
    descripcion_texto: str | None = Field(default=None, max_length=2000)
    direccion_referencia: str | None = Field(default=None, max_length=255)
    latitud: Decimal | None = None
    longitud: Decimal | None = None


class IncidenteResponse(BaseModel):
    id_incidente: int
    id_cliente: int
    id_vehiculo: int
    id_tipo_incidente: int
    id_prioridad: int
    id_estado_servicio_actual: int
    titulo: str
    descripcion_texto: str | None = None
    direccion_referencia: str | None = None
    latitud: Decimal | None = None
    longitud: Decimal | None = None
    fecha_reporte: datetime
    clasificacion_ia: str | None = None
    confianza_clasificacion: Decimal | None = None
    resumen_ia: str | None = None
    requiere_mas_info: bool

    model_config = ConfigDict(from_attributes=True)


class IncidenteDetalleResponse(BaseModel):
    id_incidente: int
    titulo: str
    descripcion_texto: str | None = None
    direccion_referencia: str | None = None
    latitud: Decimal | None = None
    longitud: Decimal | None = None
    fecha_reporte: datetime

    id_vehiculo: int
    id_tipo_incidente: int
    tipo_incidente: str
    id_prioridad: int
    prioridad: str
    id_estado_servicio_actual: int
    estado_servicio_actual: str

    clasificacion_ia: str | None = None
    confianza_clasificacion: Decimal | None = None
    resumen_ia: str | None = None
    requiere_mas_info: bool