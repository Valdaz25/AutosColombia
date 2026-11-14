
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Usuario
from app.schemas.vehiculo import (
    VehiculoActualizar,
    VehiculoCrear,
    VehiculoRespuesta,
    VehiculosPagina,
)
from app.security import get_current_user, require_admin
from app.services import vehiculo as service


router = APIRouter(
    prefix="/vehiculos",
    tags=["Vehículos"],
)

DatabaseSession = Annotated[Session, Depends(get_session)]

CurrentUser = Annotated[Usuario, Depends(get_current_user)]

AdminUser = Annotated[Usuario, Depends(require_admin)]

VehicleId = Annotated[
    int,
    Path(ge=1, le=9223372036854775807),
]


@router.post("", response_model=VehiculoRespuesta, status_code=201)
def create(
    data: VehiculoCrear,
    session: DatabaseSession,
    admin: AdminUser,
):
    """Registra un vehículo. Solo administradores."""
    return service.create_vehicle(session, data)


@router.get("", response_model=VehiculosPagina)
def list_all(
    session: DatabaseSession,
    current_user: CurrentUser,
    offset: Annotated[int, Query(ge=0, le=9223372036854775807)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """Lista los vehículos. Requiere autenticación."""
    return service.list_vehicles(session, offset, limit)


@router.get("/{id}", response_model=VehiculoRespuesta)
def get_one(
    id: VehicleId,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    """Consulta un vehículo. Requiere autenticación."""
    return service.get_vehicle(session, id)


@router.patch("/{id}", response_model=VehiculoRespuesta)
def update(
    id: VehicleId,
    data: VehiculoActualizar,
    session: DatabaseSession,
    admin: AdminUser,
):
    """Actualiza un vehículo. Solo administradores."""
    return service.update_vehicle(session, id, data)


@router.delete("/{id}", status_code=204)
def delete(
    id: VehicleId,
    session: DatabaseSession,
    admin: AdminUser,
) -> Response:
    """Elimina un vehículo. Solo administradores."""
    service.delete_vehicle(session, id)
    return Response(status_code=204)
