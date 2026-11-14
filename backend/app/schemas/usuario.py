
from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)


NombreUsuario = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        to_lower=True,
        min_length=3,
        max_length=50,
        pattern=r"^[a-z0-9._-]+$",
    ),
]


class UsuarioCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre_usuario: NombreUsuario
    password: str = Field(min_length=12, max_length=128)
    rol: Literal["ADMINISTRADOR", "OPERADOR"]
    operador_id: int | None = Field(default=None, ge=1)

    @field_validator("rol", mode="before")
    @classmethod
    def normalizar_rol(cls, value):
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @model_validator(mode="after")
    def validar_operador(self):
        if self.rol == "OPERADOR" and self.operador_id is None:
            raise ValueError(
                "Una cuenta de operador debe estar asociada a un operador."
            )

        if self.rol == "ADMINISTRADOR" and self.operador_id is not None:
            raise ValueError(
                "Una cuenta administradora no debe asociarse a un operador."
            )

        return self


class UsuarioActualizar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre_usuario: NombreUsuario
    password: str | None = Field(default=None, min_length=12, max_length=128)
    rol: Literal["ADMINISTRADOR", "OPERADOR"]
    operador_id: int | None = Field(default=None, ge=1)

    @field_validator("rol", mode="before")
    @classmethod
    def normalizar_rol(cls, value):
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @model_validator(mode="after")
    def validar_operador(self):
        if self.rol == "OPERADOR" and self.operador_id is None:
            raise ValueError(
                "Una cuenta de operador debe estar asociada a un operador."
            )

        if self.rol == "ADMINISTRADOR" and self.operador_id is not None:
            raise ValueError(
                "Una cuenta administradora no debe asociarse a un operador."
            )

        return self


class UsuarioEstado(BaseModel):
    model_config = ConfigDict(extra="forbid")

    activo: bool


class UsuarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    nombre_usuario: str
    rol: str
    operador_id: int | None
    activo: bool
    creado_en: datetime


class UsuariosPagina(BaseModel):
    items: list[UsuarioRespuesta]
    total: int
    offset: int
    limit: int


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre_usuario: NombreUsuario
    password: str


class TokenRespuesta(BaseModel):
    access_token: str
    token_type: str = "bearer"
