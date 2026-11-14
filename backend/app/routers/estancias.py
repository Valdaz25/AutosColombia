
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Usuario
from app.schemas.estancia import (
    EntradaCrear,
    SalidaCrear,
    EstanciaRespuesta,
    EstadoVehiculoRespuesta,
)
from app.schemas.vehiculo import Placa
from app.security import get_current_user
from app.services.estancia import ServicioEstancia


router = APIRouter(
    prefix="/estancias",
    tags=["Estancias"],
)

DatabaseSession = Annotated[Session, Depends(get_session)]

CurrentUser = Annotated[Usuario, Depends(get_current_user)]


def obtener_operador_id(
    current_user: Usuario,
    operador_id: int,
) -> int:
    """Determina el operador que puede registrar el movimiento."""

    if current_user.rol == "ADMINISTRADOR":
        return operador_id

    if current_user.rol == "OPERADOR":
        if current_user.operador_id is None:
            raise HTTPException(
                status_code=403,
                detail="La cuenta no tiene un operador asociado.",
            )

        return current_user.operador_id

    raise HTTPException(
        status_code=403,
        detail="No tienes permisos para realizar esta operación.",
    )


@router.post(
    "/entrada",
    response_model=EstanciaRespuesta,
    status_code=201,
)
def entrada(
    data: EntradaCrear,
    session: DatabaseSession,
    current_user: CurrentUser,
) -> EstanciaRespuesta:

    operador_id = obtener_operador_id(
        current_user,
        data.operador_id,
    )

    data = data.model_copy(
        update={"operador_id": operador_id}
    )

    return ServicioEstancia(session).entrada(data)


@router.post(
    "/salida",
    response_model=EstanciaRespuesta,
)
def salida(
    data: SalidaCrear,
    session: DatabaseSession,
    current_user: CurrentUser,
) -> EstanciaRespuesta:

    operador_id = obtener_operador_id(
        current_user,
        data.operador_id,
    )

    data = data.model_copy(
        update={"operador_id": operador_id}
    )

    return ServicioEstancia(session).salida(data)


@router.get(
    "/vehiculo/{placa}",
    response_model=EstadoVehiculoRespuesta,
)
def consultar(
    placa: Placa,
    session: DatabaseSession,
    current_user: CurrentUser,
) -> EstadoVehiculoRespuesta:

    return ServicioEstancia(session).consultar(placa)
