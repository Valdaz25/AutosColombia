
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas.usuario import (
    UsuarioActualizar,
    UsuarioCrear,
    UsuarioEstado,
    UsuarioRespuesta,
    UsuariosPagina,
)
from app.security import require_admin
from app.services.usuario import (
    UsuarioError,
    change_user_status,
    create_user,
    get_user,
    list_users,
    update_user,
)


router = APIRouter(
    prefix="/usuarios",
    tags=["Gestión de usuarios"],
    dependencies=[Depends(require_admin)],
)


@router.post("", response_model=UsuarioRespuesta, status_code=201)
def crear_usuario(
    data: UsuarioCrear,
    session: Annotated[Session, Depends(get_session)],
):
    try:
        return create_user(session, data)
    except UsuarioError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from None


@router.get("", response_model=UsuariosPagina)
def consultar_usuarios(
    session: Annotated[Session, Depends(get_session)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    try:
        return list_users(session, offset, limit)
    except UsuarioError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from None


@router.get("/{user_id}", response_model=UsuarioRespuesta)
def consultar_usuario(
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
):
    try:
        return get_user(session, user_id)
    except UsuarioError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from None


@router.put("/{user_id}", response_model=UsuarioRespuesta)
def editar_usuario(
    user_id: int,
    data: UsuarioActualizar,
    session: Annotated[Session, Depends(get_session)],
):
    try:
        return update_user(session, user_id, data)
    except UsuarioError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from None


@router.patch("/{user_id}/estado", response_model=UsuarioRespuesta)
def cambiar_estado_usuario(
    user_id: int,
    data: UsuarioEstado,
    session: Annotated[Session, Depends(get_session)],
):
    try:
        return change_user_status(session, user_id, data.activo)
    except UsuarioError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from None
