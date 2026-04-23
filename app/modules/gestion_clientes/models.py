from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Identity,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.session import Base


class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id_usuario"),
        nullable=False,
        unique=True,
    )

    usuario = relationship("Usuario")
    vehiculos: Mapped[list["Vehiculo"]] = relationship(
        back_populates="cliente",
        cascade="all, delete-orphan",
    )


class TipoVehiculo(Base):
    __tablename__ = "tipo_vehiculo"

    id_tipo_vehiculo: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)

    vehiculos: Mapped[list["Vehiculo"]] = relationship(
        back_populates="tipo_vehiculo",
    )


class Vehiculo(Base):
    __tablename__ = "vehiculo"

    id_vehiculo: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )
    id_cliente: Mapped[int] = mapped_column(
        ForeignKey("cliente.id_cliente"),
        nullable=False,
    )
    id_tipo_vehiculo: Mapped[int] = mapped_column(
        ForeignKey("tipo_vehiculo.id_tipo_vehiculo"),
        nullable=False,
    )
    placa: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    marca: Mapped[str] = mapped_column(String(100), nullable=False)
    modelo: Mapped[str] = mapped_column(String(100), nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    descripcion_referencia: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    cliente: Mapped["Cliente"] = relationship(back_populates="vehiculos")
    tipo_vehiculo: Mapped["TipoVehiculo"] = relationship(back_populates="vehiculos")
    