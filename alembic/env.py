from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

from app.core.config.settings import settings
from app.core.db.session import Base

# Importar todos los modelos para que Alembic detecte las tablas
from app.modules.autenticacion_seguridad.models import (
    BitacoraSistema,
    Rol,
    Usuario,
    UsuarioRol,
)
from app.modules.gestion_clientes.models import (
    Cliente,
    TipoVehiculo,
    Vehiculo,
)
from app.modules.gestion_operativa_taller_tecnico.models import (
    Especialidad,
    Taller,
    TallerAuxilio,
    TallerTipoVehiculo,
    Tecnico,
    TecnicoEspecialidad,
    TipoAuxilio,
    TipoTaller,
    UnidadMovil,
)
from app.modules.gestion_incidentes_atencion.models import (
    AsignacionServicio,
    EstadoServicio,
    Evidencia,
    HistorialIncidente,
    Incidente,
    Prioridad,
    SolicitudTaller,
    TipoIncidente,
)
from app.modules.seguimiento_monitoreo_servicio.models import (
    CalificacionServicio,
    ComisionPlataforma,
    DetallePago,
    MetricaIncidente,
    Notificacion,
    PagoServicio,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()