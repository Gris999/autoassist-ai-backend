from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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


class TallerAuxilioCreateRequest(BaseModel):
    id_tipo_auxilio: int
    precio_referencial: float = Field(ge=0)
    disponible: bool = Field(default=True)


class TallerAuxilioUpdateRequest(BaseModel):
    precio_referencial: float | None = Field(default=None, ge=0)
    disponible: bool | None = None


class TallerAuxilioResponse(BaseModel):
    id_taller_auxilio: int
    id_taller: int
    id_tipo_auxilio: int
    nombre_tipo_auxilio: str
    descripcion_tipo_auxilio: str | None = None
    precio_referencial: float
    disponible: bool

    model_config = ConfigDict(from_attributes=True)
