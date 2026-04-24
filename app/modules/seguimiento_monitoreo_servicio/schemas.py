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


class NotificacionCreateRequest(BaseModel):
    id_usuario: int
    id_incidente: int | None = None
    titulo: str
    mensaje: str
    tipo_notificacion: str


class NotificacionListResponse(BaseModel):
    id_notificacion: int
    id_incidente: int | None = None
    titulo: str
    mensaje: str
    tipo_notificacion: str
    leido: bool
    fecha_envio: datetime


class NotificacionDetailResponse(BaseModel):
    id_notificacion: int
    id_usuario: int
    id_incidente: int | None = None
    titulo: str
    mensaje: str
    tipo_notificacion: str
    leido: bool
    fecha_envio: datetime


class NotificacionLeidaResponse(BaseModel):
    id_notificacion: int
    leido: bool
    mensaje: str


class IncidenteHistorialListResponse(BaseModel):
    id_incidente: int
    titulo: str
    fecha_reporte: datetime
    tipo_incidente: str
    id_estado_servicio_actual: int
    estado_servicio_actual: str


class HistorialIncidenteEventoResponse(BaseModel):
    fecha_hora: datetime
    tipo_evento: str
    actor: str | None = None
    detalle: str | None = None
    estado_anterior: str | None = None
    estado_nuevo: str | None = None
    estado_solicitud: str | None = None
    id_taller: int | None = None
    nombre_taller: str | None = None
    id_tecnico: int | None = None
    nombre_tecnico: str | None = None
    id_unidad_movil: int | None = None
    placa_unidad_movil: str | None = None


class IncidenteHistorialDetailResponse(BaseModel):
    id_incidente: int
    titulo: str
    fecha_reporte: datetime
    tipo_incidente: str
    prioridad: str
    id_estado_servicio_actual: int
    estado_servicio_actual: str
    descripcion_texto: str | None = None
    direccion_referencia: str | None = None
    latitud: Decimal | None = None
    longitud: Decimal | None = None
    historial: list[HistorialIncidenteEventoResponse]
    mensaje: str | None = None
