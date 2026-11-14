from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas.usuario import LoginRequest, TokenRespuesta, UsuarioRespuesta
from app.security import get_current_user
from app.services.auth import AuthError, authenticate_user
from app.models import Usuario


router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenRespuesta)
def login(
    data: LoginRequest,
    session: Annotated[Session, Depends(get_session)],
):
    try:
        return authenticate_user(
            session,
            data.nombre_usuario,
            data.password,
        )
    except AuthError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from None


@router.get("/me", response_model=UsuarioRespuesta)
def read_current_user(
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    return current_user 