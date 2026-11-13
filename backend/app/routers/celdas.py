
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas.celda import (
    CeldaActualizar,
    CeldaCrear,
    CeldaRespuesta,
    CeldasPagina,
)
from app.services import celda as service


router = APIRouter(
    prefix="/celdas",
    tags=["Celdas"],
)

DatabaseSession = Annotated[Session, Depends(get_session)]

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
):
    """Registra una nueva celda en el sistema."""
    return service.create_cell(session, data)


@router.get(
    "",
    response_model=CeldasPagina,
    summary="Listar celdas",
)
def list_all(
    session: DatabaseSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """Consulta las celdas registradas mediante paginación."""
    return service.list_cells(session, offset, limit)


@router.get(
    "/{id}",
    response_model=CeldaRespuesta,
    summary="Consultar celda",
)
def get_one(
    id: CellId,
    session: DatabaseSession,
):
    """Consulta una celda por su identificador."""
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
):
    """Actualiza los datos o el estado de una celda."""
    return service.update_cell(session, id, data)


@router.delete(
    "/{id}",
    status_code=204,
    summary="Eliminar celda",
)
def delete(
    id: CellId,
    session: DatabaseSession,
) -> Response:
    """Elimina una celda que no tenga registros relacionados."""
    service.delete_cell(session, id)
    return Response(status_code=204)
