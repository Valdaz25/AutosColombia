"""Actualiza operadores y celdas según los modelos actuales.

Revision ID: 0003
Revises: 0002
"""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar campos de estado.
    op.add_column(
        "celda",
        sa.Column(
            "activo",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )

    op.add_column(
        "operador",
        sa.Column(
            "activo",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )

    # La tabla operador está vacía, por lo que documento puede ser obligatorio.
    op.add_column(
        "operador",
        sa.Column("documento", sa.Text(), nullable=False),
    )

    # Restricciones para el documento del operador.
    op.create_unique_constraint(
        "uq_operador_documento",
        "operador",
        ["documento"],
    )
    op.create_check_constraint(
        "ck_operador_documento_normalizado",
        "operador",
        "documento ~ '^[^[:space:]]+$'",
    )

    # Actualizar la validación de la placa del vehículo.
    op.drop_constraint(
        "ck_vehiculo_placa_no_vacia",
        "vehiculo",
        type_="check",
    )
    op.drop_constraint(
        "ck_vehiculo_placa_normalizada",
        "vehiculo",
        type_="check",
    )
    op.create_check_constraint(
        "ck_vehiculo_placa_normalizada",
        "vehiculo",
        "placa ~ '^[^[:space:]]+$'",
    )

    # Actualizar la validación del código de la celda.
    op.drop_constraint(
        "ck_celda_codigo_no_vacio",
        "celda",
        type_="check",
    )
    op.drop_constraint(
        "ck_celda_codigo_normalizado",
        "celda",
        type_="check",
    )
    op.create_check_constraint(
        "ck_celda_codigo_normalizado",
        "celda",
        "codigo ~ '^[^[:space:]]+$'",
    )


def downgrade() -> None:
    # Revertir las restricciones de celda.
    op.drop_constraint(
        "ck_celda_codigo_normalizado",
        "celda",
        type_="check",
    )
    op.create_check_constraint(
        "ck_celda_codigo_no_vacio",
        "celda",
        "codigo ~ '[^[:space:]]'",
    )
    op.create_check_constraint(
        "ck_celda_codigo_normalizado",
        "celda",
        "codigo = upper(regexp_replace(codigo, "
        "'^[[:space:]]+|[[:space:]]+$', '', 'g'))",
    )

    # Revertir las restricciones de vehículo.
    op.drop_constraint(
        "ck_vehiculo_placa_normalizada",
        "vehiculo",
        type_="check",
    )
    op.create_check_constraint(
        "ck_vehiculo_placa_no_vacia",
        "vehiculo",
        "placa ~ '[^[:space:]]'",
    )
    op.create_check_constraint(
        "ck_vehiculo_placa_normalizada",
        "vehiculo",
        "placa = upper(regexp_replace(placa, "
        "'^[[:space:]]+|[[:space:]]+$', '', 'g'))",
    )

    # Revertir los campos de operador.
    op.drop_constraint(
        "ck_operador_documento_normalizado",
        "operador",
        type_="check",
    )
    op.drop_constraint(
        "uq_operador_documento",
        "operador",
        type_="unique",
    )
    op.drop_column("operador", "documento")
    op.drop_column("operador", "activo")

    # Revertir el campo de celda.
    op.drop_column("celda", "activo")
