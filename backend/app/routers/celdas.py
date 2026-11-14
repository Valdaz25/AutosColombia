
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Usuario
from app.schemas.celda import (
    CeldaActualizar,
    CeldaCrear,
    CeldaRespuesta,
    CeldasPagina,
)
from app.security import get_current_user, require_admin
from app.services import celda as service


router = APIRouter(
    prefix="/celdas",
    tags=["Celdas"],
)

DatabaseSession = Annotated[Session, Depends(get_session)]

CurrentUser = Annotated[Usuario, Depends(get_current_user)]

AdminUser = Annotated[Usuario, Depends(require_admin)]

CellId = Annotated[
    int,
    Path(
        ge=1,
        le=9223372036854775807,
        description="Identificador único de la celda.",
    ),
]


@router.post(
    "",
    response_model=CeldaRespuesta,
    status_code=201,
    summary="Registrar celda",
)
def create(
    data: CeldaCrear,
    session: DatabaseSession,
    admin: AdminUser,
):
    """Registra una nueva celda. Solo administradores."""
    return service.create_cell(session, data)


@router.get(
    "",
    response_model=CeldasPagina,
    summary="Listar celdas",
)
def list_all(
    session: DatabaseSession,
    current_user: CurrentUser,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """Consulta las celdas. Requiere autenticación."""
    return service.list_cells(session, offset, limit)


@router.get(
    "/{id}",
    response_model=CeldaRespuesta,
    summary="Consultar celda",
)
def get_one(
    id: CellId,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    """Consulta una celda. Requiere autenticación."""
    return service.get_cell(session, id)


@router.patch(
    "/{id}",
    response_model=CeldaRespuesta,
    summary="Actualizar celda",
)
def update(
    id: CellId,
    data: CeldaActualizar,
    session: DatabaseSession,
    admin: AdminUser,
):
    """Actualiza una celda. Solo administradores."""
    return service.update_cell(session, id, data)


@router.delete(
    "/{id}",
    status_code=204,
    summary="Eliminar celda",
)
def delete(
    id: CellId,
    session: DatabaseSession,
    admin: AdminUser,
) -> Response:
    """Elimina una celda. Solo administradores."""
    service.delete_cell(session, id)
    return Response(status_code=204)
