from pydantic import BaseModel, ConfigDict, Field


class VehiculoCreateRequest(BaseModel):
    id_tipo_vehiculo: int
    placa: str = Field(min_length=5, max_length=20)
    marca: str = Field(min_length=2, max_length=100)
    modelo: str = Field(min_length=1, max_length=100)
    anio: int = Field(ge=1900, le=2100)
    color: str | None = Field(default=None, max_length=50)
    descripcion_referencia: str | None = Field(default=None, max_length=255)


class VehiculoResponse(BaseModel):
    id_vehiculo: int
    id_cliente: int
    id_tipo_vehiculo: int
    placa: str
    marca: str
    modelo: str
    anio: int
    color: str | None = None
    descripcion_referencia: str | None = None
    estado: bool

    model_config = ConfigDict(from_attributes=True)