from sqlalchemy import select

from app.core.db.session import SessionLocal
from app.modules.autenticacion_seguridad.models import Rol
from app.modules.gestion_operativa_taller_tecnico.models import (
    Especialidad,
    TipoAuxilio,
    TipoTaller,
)
from app.modules.gestion_clientes.models import TipoVehiculo
from app.modules.gestion_incidentes_atencion.models import (
    EstadoServicio,
    Prioridad,
    TipoIncidente,
)


def get_or_create(session, model, defaults=None, **filters):
    instance = session.execute(
        select(model).filter_by(**filters)
    ).scalar_one_or_none()

    if instance:
        return instance, False

    params = {**filters, **(defaults or {})}
    instance = model(**params)
    session.add(instance)
    return instance, True


def seed_roles(session):
    roles = [
        {"nombre": "CLIENTE", "descripcion": "Cliente que reporta incidentes y solicita auxilio"},
        {"nombre": "TALLER", "descripcion": "Taller que ofrece servicios de auxilio"},
        {"nombre": "TECNICO", "descripcion": "Tecnico asignado para atender incidentes"},
        {"nombre": "ADMIN", "descripcion": "Administrador de la plataforma"},
        {"nombre": "SUPERADMIN", "descripcion": "Superadministrador del sistema"},
    ]

    for item in roles:
        get_or_create(session, Rol, nombre=item["nombre"], defaults=item)


def seed_tipos_taller(session):
    tipos = [
        {"nombre": "MECANICO_GENERAL", "descripcion": "Taller mecanico general"},
        {"nombre": "ELECTROMECANICO", "descripcion": "Taller especializado en sistemas electricos"},
        {"nombre": "GRUAS_Y_REMOLQUE", "descripcion": "Taller o empresa con servicio de grua y remolque"},
    ]

    for item in tipos:
        get_or_create(session, TipoTaller, nombre=item["nombre"], defaults=item)


def seed_tipos_vehiculo(session):
    tipos = [
        {"nombre": "AUTOMOVIL", "descripcion": "Vehiculo liviano particular"},
        {"nombre": "MOTOCICLETA", "descripcion": "Motocicleta de dos ruedas"},
        {"nombre": "CAMIONETA", "descripcion": "Vehiculo utilitario liviano"},
        {"nombre": "MINIBUS", "descripcion": "Vehiculo de transporte mediano"},
        {"nombre": "CAMION", "descripcion": "Vehiculo pesado de carga"},
    ]

    for item in tipos:
        get_or_create(session, TipoVehiculo, nombre=item["nombre"], defaults=item)


def seed_tipos_auxilio(session):
    tipos = [
        {
            "nombre": "REMOLQUE",
            "descripcion": "Traslado del vehiculo mediante grua",
            "requiere_unidad_movil": True,
            "requiere_remolque": True,
            "estado": True,
        },
        {
            "nombre": "AUXILIO_ELECTRICO",
            "descripcion": "Asistencia por bateria descargada o falla electrica basica",
            "requiere_unidad_movil": True,
            "requiere_remolque": False,
            "estado": True,
        },
        {
            "nombre": "CAMBIO_DE_LLANTA",
            "descripcion": "Cambio de llanta o asistencia por pinchazo",
            "requiere_unidad_movil": True,
            "requiere_remolque": False,
            "estado": True,
        },
        {
            "nombre": "SUMINISTRO_COMBUSTIBLE",
            "descripcion": "Entrega de combustible en ruta",
            "requiere_unidad_movil": True,
            "requiere_remolque": False,
            "estado": True,
        },
        {
            "nombre": "APERTURA_VEHICULO",
            "descripcion": "Apertura por llaves dentro del vehiculo",
            "requiere_unidad_movil": True,
            "requiere_remolque": False,
            "estado": True,
        },
        {
            "nombre": "AUXILIO_MECANICO_BASICO",
            "descripcion": "Asistencia mecanica basica en sitio",
            "requiere_unidad_movil": True,
            "requiere_remolque": False,
            "estado": True,
        },
    ]

    for item in tipos:
        get_or_create(session, TipoAuxilio, nombre=item["nombre"], defaults=item)


def seed_prioridades(session):
    prioridades = [
        {"nombre": "BAJA", "nivel": 1, "descripcion": "Incidente de baja urgencia"},
        {"nombre": "MEDIA", "nivel": 2, "descripcion": "Incidente de urgencia moderada"},
        {"nombre": "ALTA", "nivel": 3, "descripcion": "Incidente de alta urgencia"},
        {"nombre": "CRITICA", "nivel": 4, "descripcion": "Incidente critico o de riesgo alto"},
    ]

    for item in prioridades:
        get_or_create(session, Prioridad, nombre=item["nombre"], defaults=item)


def seed_estados_servicio(session):
    estados = [
        {"nombre": "REPORTADO", "descripcion": "Incidente reportado por el cliente", "orden_flujo": 1, "estado": True},
        {"nombre": "EN_VALIDACION", "descripcion": "Incidente en validacion inicial", "orden_flujo": 2, "estado": True},
        {"nombre": "BUSCANDO_TALLER", "descripcion": "Buscando taller candidato", "orden_flujo": 3, "estado": True},
        {"nombre": "ASIGNADO", "descripcion": "Servicio asignado a un taller/tecnico", "orden_flujo": 4, "estado": True},
        {"nombre": "EN_CAMINO", "descripcion": "Tecnico o unidad movil en camino", "orden_flujo": 5, "estado": True},
        {"nombre": "EN_ATENCION", "descripcion": "Incidente siendo atendido", "orden_flujo": 6, "estado": True},
        {"nombre": "FINALIZADO", "descripcion": "Servicio finalizado", "orden_flujo": 7, "estado": True},
        {"nombre": "CANCELADO", "descripcion": "Servicio cancelado", "orden_flujo": 8, "estado": True},
    ]

    for item in estados:
        get_or_create(session, EstadoServicio, nombre=item["nombre"], defaults=item)


def seed_tipos_incidente(session):
    tipos = [
        {"nombre": "FALLA_MECANICA", "descripcion": "Problema mecanico general", "estado": True},
        {"nombre": "BATERIA_DESCARGADA", "descripcion": "Vehiculo no enciende por bateria", "estado": True},
        {"nombre": "PINCHAZO_LLANTA", "descripcion": "Pinchazo o dano de llanta", "estado": True},
        {"nombre": "SIN_COMBUSTIBLE", "descripcion": "Vehiculo sin combustible", "estado": True},
        {"nombre": "LLAVES_DENTRO", "descripcion": "Llaves dentro del vehiculo o bloqueo", "estado": True},
        {"nombre": "ACCIDENTE_MENOR", "descripcion": "Accidente leve o colision menor", "estado": True},
        {"nombre": "SOBRECALENTAMIENTO", "descripcion": "Motor sobrecalentado", "estado": True},
    ]

    for item in tipos:
        get_or_create(session, TipoIncidente, nombre=item["nombre"], defaults=item)


def seed_especialidades(session):
    especialidades = [
        {"nombre": "MECANICA_GENERAL", "descripcion": "Diagnostico y reparacion mecanica basica"},
        {"nombre": "ELECTRICIDAD_AUTOMOTRIZ", "descripcion": "Diagnostico electrico automotriz"},
        {"nombre": "LLANTAS_Y_NEUMATICOS", "descripcion": "Cambio y soporte de llantas"},
        {"nombre": "GRUA_Y_REMOLQUE", "descripcion": "Operacion de grua y remolque"},
    ]

    for item in especialidades:
        get_or_create(session, Especialidad, nombre=item["nombre"], defaults=item)


def run_seeds():
    session = SessionLocal()
    try:
        seed_roles(session)
        seed_tipos_taller(session)
        seed_tipos_vehiculo(session)
        seed_tipos_auxilio(session)
        seed_prioridades(session)
        seed_estados_servicio(session)
        seed_tipos_incidente(session)
        seed_especialidades(session)

        session.commit()
        print("Seeds ejecutados correctamente.")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    run_seeds()