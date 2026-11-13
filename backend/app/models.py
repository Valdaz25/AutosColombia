
"""Modelos de datos de Autos Colombia."""

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    validates,
)


class Base(DeclarativeBase):
    pass


def required_text(value: str, attribute: str) -> str:
    """Valida que un campo contenga texto y elimina espacios externos."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{attribute} debe ser texto no vacío.")

    return value.strip()


def normalize_identifier(value: str, attribute: str) -> str:
    """Normaliza identificadores y rechaza espacios internos."""
    value = required_text(value, attribute).upper()

    if any(character.isspace() for character in value):
        raise ValueError(
            f"{attribute} no puede contener espacios internos."
        )

    return value


class Vehiculo(Base):
    __tablename__ = "vehiculo"

    __table_args__ = (
        UniqueConstraint("placa", name="uq_vehiculo_placa"),
        CheckConstraint(
            "placa ~ '^[^[:space:]]+$'",
            name="ck_vehiculo_placa_normalizada",
        ),
        CheckConstraint(
            "color ~ '[^[:space:]]'",
            name="ck_vehiculo_color_no_vacio",
        ),
        CheckConstraint(
            "marca ~ '[^[:space:]]'",
            name="ck_vehiculo_marca_no_vacia",
        ),
        CheckConstraint(
            "modelo BETWEEN 1 AND 9999",
            name="ck_vehiculo_modelo_anio",
        ),
        CheckConstraint(
            "tipo IN ('MOTO', 'AUTOMOVIL', 'CAMIONETA')",
            name="ck_vehiculo_tipo",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )

    placa: Mapped[str] = mapped_column(Text, nullable=False)
    color: Mapped[str] = mapped_column(Text, nullable=False)
    modelo: Mapped[int] = mapped_column(Integer, nullable=False)
    marca: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(Text, nullable=False)

    @validates("placa", "color", "marca", "tipo")
    def validate_text(self, key: str, value: str) -> str:
        if key == "placa":
            return normalize_identifier(value, key)

        value = required_text(value, key)

        if key == "tipo" and value not in {
            "MOTO",
            "AUTOMOVIL",
            "CAMIONETA",
        }:
            raise ValueError(
                "tipo debe ser MOTO, AUTOMOVIL o CAMIONETA."
            )

        return value

    @validates("modelo")
    def validate_modelo(self, key: str, value: int) -> int:
        if type(value) is not int or not 1 <= value <= 9999:
            raise ValueError(
                "modelo debe ser un año entero entre 1 y 9999."
            )

        return value


class Celda(Base):
    __tablename__ = "celda"

    __table_args__ = (
        UniqueConstraint("codigo", name="uq_celda_codigo"),
        CheckConstraint(
            "codigo ~ '^[^[:space:]]+$'",
            name="ck_celda_codigo_normalizado",
        ),
        CheckConstraint(
            "tipo ~ '[^[:space:]]'",
            name="ck_celda_tipo_no_vacio",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )

    codigo: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(Text, nullable=False)

    activo: Mapped[bool] = mapped_column(
        default=True,
        server_default=text("true"),
        nullable=False,
    )

    @validates("codigo", "tipo")
    def validate_text(self, key: str, value: str) -> str:
        if key == "codigo":
            return normalize_identifier(value, key)

        return required_text(value, key)


class Operador(Base):
    __tablename__ = "operador"

    __table_args__ = (
        UniqueConstraint("documento", name="uq_operador_documento"),
        CheckConstraint(
            "nombre ~ '[^[:space:]]'",
            name="ck_operador_nombre_no_vacio",
        ),
        CheckConstraint(
            "telefono ~ '[^[:space:]]'",
            name="ck_operador_telefono_no_vacio",
        ),
        CheckConstraint(
            "documento ~ '^[^[:space:]]+$'",
            name="ck_operador_documento_normalizado",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )

    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    telefono: Mapped[str] = mapped_column(Text, nullable=False)
    documento: Mapped[str] = mapped_column(Text, nullable=False)

    activo: Mapped[bool] = mapped_column(
        default=True,
        server_default=text("true"),
        nullable=False,
    )

    @validates("nombre", "telefono", "documento")
    def validate_text(self, key: str, value: str) -> str:
        if key == "documento":
            return normalize_identifier(value, key)

        return required_text(value, key)


class Estancia(Base):
    __tablename__ = "estancia"

    __table_args__ = (
        CheckConstraint(
            "salida >= entrada",
            name="ck_estancia_orden_fechas",
        ),
        CheckConstraint(
            "(salida IS NULL) = (operador_salida_id IS NULL)",
            name="ck_estancia_cierre_completo",
        ),
        Index(
            "uq_estancia_vehiculo_abierta",
            "vehiculo_id",
            unique=True,
            postgresql_where=text("salida IS NULL"),
        ),
        Index(
            "uq_estancia_celda_abierta",
            "celda_id",
            unique=True,
            postgresql_where=text("salida IS NULL"),
        ),
        Index(
            "ix_estancia_vehiculo_entrada",
            "vehiculo_id",
            "entrada",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )

    vehiculo_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "vehiculo.id",
            name="fk_estancia_vehiculo",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    celda_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "celda.id",
            name="fk_estancia_celda",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    entrada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    salida: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    operador_entrada_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "operador.id",
            name="fk_estancia_operador_entrada",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    operador_salida_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "operador.id",
            name="fk_estancia_operador_salida",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    vehiculo: Mapped[Vehiculo] = relationship()
    celda: Mapped[Celda] = relationship()

    operador_entrada: Mapped[Operador] = relationship(
        foreign_keys=[operador_entrada_id]
    )

    operador_salida: Mapped[Operador | None] = relationship(
        foreign_keys=[operador_salida_id]
    )

    def esta_abierta(self) -> bool:
        return self.salida is None

    def cerrar(
        self,
        fecha_salida: datetime,
        operador: Operador,
    ) -> None:
        """Valida y asigna el cierre de una estancia."""

        if not self.esta_abierta():
            raise ValueError("La estancia ya está cerrada.")

        if (
            not isinstance(fecha_salida, datetime)
            or fecha_salida.utcoffset() is None
        ):
            raise ValueError(
                "La fecha de salida debe tener zona horaria."
            )

        if (
            not isinstance(self.entrada, datetime)
            or self.entrada.utcoffset() is None
        ):
            raise ValueError(
                "La entrada debe estar cargada y tener zona horaria "
                "antes de cerrar."
            )

        if (
            fecha_salida.astimezone(timezone.utc)
            < self.entrada.astimezone(timezone.utc)
        ):
            raise ValueError(
                "La salida no puede ser anterior a la entrada."
            )

        if not isinstance(operador, Operador) or operador.id is None:
            raise ValueError(
                "El operador de salida debe tener un id asignado."
            )

        self.salida = fecha_salida
        self.operador_salida = operador
        self.operador_salida_id = operador.id
