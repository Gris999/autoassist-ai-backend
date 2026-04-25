"""add taller schedule availability

Revision ID: 9d4f7f1b7b34
Revises: db4805f11a91
Create Date: 2026-04-25 09:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9d4f7f1b7b34"
down_revision: Union[str, Sequence[str], None] = "db4805f11a91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "horario_disponibilidad_taller",
        sa.Column(
            "id_horario_disponibilidad",
            sa.BigInteger(),
            sa.Identity(always=False),
            nullable=False,
        ),
        sa.Column("id_taller", sa.BigInteger(), nullable=False),
        sa.Column("dia_semana", sa.String(length=15), nullable=False),
        sa.Column("hora_inicio", sa.Time(), nullable=False),
        sa.Column("hora_fin", sa.Time(), nullable=False),
        sa.Column("estado", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["id_taller"], ["taller.id_taller"]),
        sa.PrimaryKeyConstraint("id_horario_disponibilidad"),
        sa.UniqueConstraint(
            "id_taller",
            "dia_semana",
            "hora_inicio",
            "hora_fin",
            name="uq_taller_horario_disponibilidad",
        ),
    )


def downgrade() -> None:
    op.drop_table("horario_disponibilidad_taller")
