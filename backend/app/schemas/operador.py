
from typing import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    field_validator
)

from app.models import required_text


Texto = Annotated[
    str,
    BeforeValidator(lambda value: required_text(value, "El campo"))
]


class OperadorCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Texto
    telefono: Texto
    documento: Texto

    @field_validator("documento", mode="before")
    @classmethod
    def normalizar_documento(cls, value):
        if not isinstance(value, str):
            return value

        value = value.strip().upper()

        if not value:
            raise ValueError("El documento es obligatorio.")

        if any(caracter.isspace() for caracter in value):
            raise ValueError("El documento no puede contener espacios internos.")

        return value


class OperadorActualizar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Texto | None = None
    telefono: Texto | None = None
    documento: Texto | None = None
    activo: bool | None = None

    @field_validator("*", mode="before")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("Los campos enviados no pueden ser nulos.")
        return value

    @field_validator("documento", mode="before")
    @classmethod
    def normalizar_documento(cls, value):
        if not isinstance(value, str):
            return value

        value = value.strip().upper()

        if not value:
            raise ValueError("El documento es obligatorio.")

        if any(caracter.isspace() for caracter in value):
            raise ValueError("El documento no puede contener espacios internos.")

        return value


class OperadorRespuesta(OperadorCrear):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    activo: bool


class OperadoresPagina(BaseModel):
    items: list[OperadorRespuesta]
    total: int
    offset: int
    limit: int
