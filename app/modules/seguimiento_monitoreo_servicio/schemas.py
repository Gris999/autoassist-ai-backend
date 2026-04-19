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