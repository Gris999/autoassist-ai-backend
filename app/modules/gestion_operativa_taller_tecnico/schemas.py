from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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


class ActualizarDisponibilidadTecnicoRequest(BaseModel):
    disponible: bool = Field(description="Indicar si el técnico está disponible")


class DisponibilidadTecnicoResponse(BaseModel):
    id_tecnico: int
    id_usuario: int
    disponible: bool
    estado: bool
    latitud_actual: float | None = None
    longitud_actual: float | None = None

    model_config = ConfigDict(from_attributes=True)


class TecnicoInfoResponse(BaseModel):
    id_tecnico: int
    id_usuario: int
    id_taller: int
    telefono_contacto: str
    disponible: bool
    estado: bool
    latitud_actual: float | None = None
    longitud_actual: float | None = None

    model_config = ConfigDict(from_attributes=True)


class TecnicoCreateRequest(BaseModel):
    nombres: str = Field(min_length=2, max_length=100)
    apellidos: str = Field(min_length=2, max_length=100)
    celular: str = Field(min_length=7, max_length=20)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    telefono_contacto: str = Field(min_length=7, max_length=20)
    disponible: bool = True
    estado: bool = True


class TecnicoUpdateRequest(BaseModel):
    nombres: str | None = Field(default=None, min_length=2, max_length=100)
    apellidos: str | None = Field(default=None, min_length=2, max_length=100)
    celular: str | None = Field(default=None, min_length=7, max_length=20)
    email: EmailStr | None = None
    telefono_contacto: str | None = Field(default=None, min_length=7, max_length=20)
    disponible: bool | None = None


class TecnicoListResponse(BaseModel):
    id_tecnico: int
    id_usuario: int
    nombres: str
    apellidos: str
    email: EmailStr
    celular: str
    telefono_contacto: str
    disponible: bool
    estado: bool

    model_config = ConfigDict(from_attributes=True)


class TecnicoDetailResponse(BaseModel):
    id_tecnico: int
    id_usuario: int
    id_taller: int
    nombres: str
    apellidos: str
    email: EmailStr
    celular: str
    telefono_contacto: str
    disponible: bool
    estado: bool
    latitud_actual: float | None = None
    longitud_actual: float | None = None

    model_config = ConfigDict(from_attributes=True)


class TecnicoEstadoResponse(BaseModel):
    id_tecnico: int
    id_usuario: int
    estado: bool
    disponible: bool

    model_config = ConfigDict(from_attributes=True)


class EspecialidadResponse(BaseModel):
    id_especialidad: int
    nombre: str
    descripcion: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TecnicoEspecialidadesResponse(BaseModel):
    id_tecnico: int
    especialidades: list[EspecialidadResponse]


class TecnicoEspecialidadesAssignRequest(BaseModel):
    ids_especialidad: list[int] = Field(min_length=1)


class TecnicoEspecialidadesUpdateRequest(BaseModel):
    ids_especialidad: list[int] = Field(default_factory=list)


class TipoVehiculoResponse(BaseModel):
    id_tipo_vehiculo: int
    nombre: str
    descripcion: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TallerTiposVehiculoConfigResponse(BaseModel):
    id_taller: int
    tipos_vehiculo: list[TipoVehiculoResponse]


class TallerTiposVehiculoConfigRequest(BaseModel):
    ids_tipo_vehiculo: list[int] = Field(min_length=1)


class UnidadMovilCreateRequest(BaseModel):
    placa: str = Field(min_length=5, max_length=20)
    tipo_unidad: str = Field(min_length=2, max_length=100)
    disponible: bool = True
    estado: bool = True
    latitud_actual: float | None = None
    longitud_actual: float | None = None


class UnidadMovilUpdateRequest(BaseModel):
    placa: str | None = Field(default=None, min_length=5, max_length=20)
    tipo_unidad: str | None = Field(default=None, min_length=2, max_length=100)
    disponible: bool | None = None
    estado: bool | None = None
    latitud_actual: float | None = None
    longitud_actual: float | None = None


class UnidadMovilEstadoDisponibilidadRequest(BaseModel):
    disponible: bool | None = None
    estado: bool | None = None


class UnidadMovilListResponse(BaseModel):
    id_unidad_movil: int
    id_taller: int
    placa: str
    tipo_unidad: str
    disponible: bool
    estado: bool

    model_config = ConfigDict(from_attributes=True)


class UnidadMovilDetailResponse(BaseModel):
    id_unidad_movil: int
    id_taller: int
    placa: str
    tipo_unidad: str
    disponible: bool
    estado: bool
    latitud_actual: float | None = None
    longitud_actual: float | None = None

    model_config = ConfigDict(from_attributes=True)
