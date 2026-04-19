from sqlalchemy.orm import Session

from app.modules.gestion_clientes.repository import (
    create_vehiculo,
    get_cliente_by_usuario_id,
    get_tipo_vehiculo_by_id,
    get_vehiculo_by_placa,
    get_vehiculos_by_cliente_id,
)
from app.modules.gestion_clientes.schemas import (
    VehiculoCreateRequest,
    VehiculoResponse,
)


def register_vehiculo_service(
    db: Session,
    current_user,
    payload: VehiculoCreateRequest,
) -> VehiculoResponse:
    cliente = get_cliente_by_usuario_id(db, current_user.id_usuario)
    if not cliente:
        raise ValueError("El usuario autenticado no tiene perfil de cliente.")

    tipo_vehiculo = get_tipo_vehiculo_by_id(db, payload.id_tipo_vehiculo)
    if not tipo_vehiculo:
        raise ValueError("El tipo de vehículo seleccionado no existe.")

    existing_vehiculo = get_vehiculo_by_placa(db, payload.placa)
    if existing_vehiculo:
        raise ValueError("Ya existe un vehículo registrado con esa placa.")

    try:
        vehiculo = create_vehiculo(
            db,
            id_cliente=cliente.id_cliente,
            id_tipo_vehiculo=payload.id_tipo_vehiculo,
            placa=payload.placa,
            marca=payload.marca,
            modelo=payload.modelo,
            anio=payload.anio,
            color=payload.color,
            descripcion_referencia=payload.descripcion_referencia,
        )

        db.commit()
        db.refresh(vehiculo)

        return VehiculoResponse.model_validate(vehiculo)
    except Exception:
        db.rollback()
        raise


def get_mis_vehiculos_service(
    db: Session,
    current_user,
) -> list[VehiculoResponse]:
    cliente = get_cliente_by_usuario_id(db, current_user.id_usuario)
    if not cliente:
        raise ValueError("El usuario autenticado no tiene perfil de cliente.")

    vehiculos = get_vehiculos_by_cliente_id(db, cliente.id_cliente)
    return [VehiculoResponse.model_validate(v) for v in vehiculos]