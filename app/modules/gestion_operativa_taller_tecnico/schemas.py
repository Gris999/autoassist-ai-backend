from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class ActualizarDisponibilidadTallerRequest(BaseModel):
    disponible: bool = Field(description="Indicar si el taller está disponible")


class DisponibilidadTallerResponse(BaseModel):
    id_taller: int
    nombre_taller: str
    disponible: bool
    latitud: float | None = None
    longitud: float | None = None
    radio_cobertura_km: float | None = None
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)


class TallerInfoResponse(BaseModel):
    id_taller: int
    nombre_taller: str
    nit: str
    direccion: str
    disponible: bool
    latitud: float | None = None
    longitud: float | None = None
    radio_cobertura_km: float | None = None
    id_tipo_taller: int
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)
