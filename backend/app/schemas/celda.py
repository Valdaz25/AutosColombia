
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    field_validator,
)

from app.models import required_text


Texto = Annotated[
    str,
    BeforeValidator(
        lambda value: required_text(value, "El campo")
    ),
]


def normalizar_codigo(value: str) -> str:
    value = value.upper()

    if any(caracter.isspace() for caracter in value):
        raise ValueError(
            "El código de la celda no puede contener espacios internos."
        )

    return value


Codigo = Annotated[
    Texto,
    AfterValidator(normalizar_codigo),
]


class CeldaCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    codigo: Codigo
    tipo: Texto
    activo: bool = True


class CeldaActualizar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    codigo: Codigo | None = None
    tipo: Texto | None = None
    activo: bool | None = None

    @field_validator("*", mode="before")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError(
                "Los campos enviados no pueden ser nulos."
            )

        return value


class CeldaRespuesta(CeldaCrear):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    id: int


class CeldasPagina(BaseModel):
    items: list[CeldaRespuesta]
    total: int
    offset: int
    limit: int
