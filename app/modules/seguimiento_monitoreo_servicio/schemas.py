from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class EstadoServicioDetalleResponse(BaseModel):
    id_incidente: int
    titulo: str
    fecha_reporte: datetime

    id_vehiculo: int
    id_tipo_incidente: int
    tipo_incidente: str

    id_prioridad: int
    prioridad: str

    id_estado_servicio_actual: int
    estado_servicio_actual: str

    direccion_referencia: str | None = None
    latitud: Decimal | None = None
    longitud: Decimal | None = None

    clasificacion_ia: str | None = None
    confianza_clasificacion: Decimal | None = None
    resumen_ia: str | None = None
    requiere_mas_info: bool


class ClienteIncidenteListResponse(BaseModel):
    id_incidente: int
    titulo: str
    fecha_reporte: datetime
    id_estado_servicio_actual: int
    estado_servicio_actual: str
    tiene_asignacion: bool


class TallerAsignadoResponse(BaseModel):
    id_taller: int
    nombre_taller: str
    direccion: str


class TecnicoAsignadoResponse(BaseModel):
    id_tecnico: int
    nombres: str
    apellidos: str
    telefono_contacto: str


class UnidadMovilAsignadaResponse(BaseModel):
    id_unidad_movil: int
    placa: str
    tipo_unidad: str


class AsignacionAuxilioDetalleResponse(BaseModel):
    id_incidente: int
    titulo: str
    fecha_reporte: datetime
    tipo_incidente: str
    descripcion_texto: str | None = None
    direccion_referencia: str | None = None
    latitud: Decimal | None = None
    longitud: Decimal | None = None
    id_estado_servicio_actual: int
    estado_servicio_actual: str
    estado_asignacion: str | None = None
    tiempo_estimado_min: int | None = None
    asignacion_definida: bool
    mensaje: str | None = None
    taller: TallerAsignadoResponse | None = None
    tecnico: TecnicoAsignadoResponse | None = None
    unidad_movil: UnidadMovilAsignadaResponse | None = None
    placa_vehiculo: str | None = None
    marca_vehiculo: str | None = None
    modelo_vehiculo: str | None = None
