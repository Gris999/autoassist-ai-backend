from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RolResponse(BaseModel):
    id_rol: int
    nombre: str
    descripcion: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UsuarioResponse(BaseModel):
    id_usuario: int
    nombres: str
    apellidos: str
    celular: str
    email: EmailStr
    estado: bool
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)


class RegistroClienteRequest(BaseModel):
    nombres: str = Field(min_length=2, max_length=100)
    apellidos: str = Field(min_length=2, max_length=100)
    celular: str = Field(min_length=7, max_length=20)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RegistroTallerRequest(BaseModel):
    nombres: str = Field(min_length=2, max_length=100)
    apellidos: str = Field(min_length=2, max_length=100)
    celular: str = Field(min_length=7, max_length=20)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    id_tipo_taller: int
    nombre_taller: str = Field(min_length=2, max_length=150)
    nit: str = Field(min_length=5, max_length=30)
    direccion: str = Field(min_length=5, max_length=255)
    latitud: Decimal | None = None
    longitud: Decimal | None = None
    radio_cobertura_km: Decimal | None = None


class MensajeResponse(BaseModel):
    message: str


class RegistroClienteResponse(BaseModel):
    usuario: UsuarioResponse
    rol: str


class RegistroTallerResponse(BaseModel):
    usuario: UsuarioResponse
    rol: str
    nombre_taller: str


class UsuarioMeResponse(BaseModel):
    id_usuario: int
    nombres: str
    apellidos: str
    celular: str
    email: EmailStr
    estado: bool
    fecha_registro: datetime
    roles: list[str]