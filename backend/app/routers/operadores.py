
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Operador, Usuario
from app.schemas.operador import (
    OperadorActualizar,
    OperadorCrear,
    OperadorRespuesta,
    OperadoresPagina,
)
from app.security import get_current_user, require_admin
from app.services import operador as service


router = APIRouter(
    prefix="/operadores",
    tags=["Operadores"],
)

DatabaseSession = Annotated[Session, Depends(get_session)]

CurrentUser = Annotated[Usuario, Depends(get_current_user)]

AdminUser = Annotated[Usuario, Depends(require_admin)]

OperatorId = Annotated[
    int,
    Path(
        ge=1,
        le=9223372036854775807,
        description="Identificador único del operador.",
    ),
]


@router.post(
    "",
    response_model=OperadorRespuesta,
    status_code=201,
    summary="Registrar operador",
)
def create(
    data: OperadorCrear,
    session: DatabaseSession,
    admin: AdminUser,
) -> Operador:
    """Registra un nuevo operador. Solo administradores."""
    return service.create_operator(session, data)


@router.get(
    "",
    response_model=OperadoresPagina,
    summary="Listar operadores",
)
def list_all(
    session: DatabaseSession,
    current_user: CurrentUser,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict:
    """Consulta los operadores. Requiere autenticación."""
    return service.list_operators(session, offset, limit)


@router.get(
    "/{id}",
    response_model=OperadorRespuesta,
    summary="Consultar operador",
)
def get_one(
    id: OperatorId,
    session: DatabaseSession,
    current_user: CurrentUser,
) -> Operador:
    """Consulta un operador. Requiere autenticación."""
    return service.get_operator(session, id)


@router.patch(
    "/{id}",
    response_model=OperadorRespuesta,
    summary="Actualizar operador",
)
def update(
    id: OperatorId,
    data: OperadorActualizar,
    session: DatabaseSession,
    admin: AdminUser,
) -> Operador:
    """Actualiza un operador. Solo administradores."""
    return service.update_operator(session, id, data)


@router.delete(
    "/{id}",
    status_code=204,
    summary="Eliminar operador",
)
def delete(
    id: OperatorId,
    session: DatabaseSession,
    admin: AdminUser,
) -> Response:
    """Elimina un operador. Solo administradores."""
    service.delete_operator(session, id)
    return Response(status_code=204)
