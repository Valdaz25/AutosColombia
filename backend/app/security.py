
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.config import load_auth_settings
from app.database import get_session
from app.models import Usuario


password_hash = PasswordHash.recommended()

bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    """Genera un hash seguro de la contraseña."""
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: int) -> str:
    """Genera un token JWT con vencimiento."""
    settings = load_auth_settings()

    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_minutes
    )

    payload = {
        "sub": str(user_id),
        "exp": expires,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm="HS256",
    )


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme),
    ],
    session: Annotated[Session, Depends(get_session)],
) -> Usuario:
    """Identifica al usuario mediante su token JWT."""

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o sesión vencida.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        settings = load_auth_settings()

        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=["HS256"],
        )

        subject = payload.get("sub")

        if not isinstance(subject, str) or not subject.isdigit():
            raise credentials_error

        user_id = int(subject)

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise credentials_error from None

    user = session.get(Usuario, user_id)

    if user is None or not user.activo:
        raise credentials_error

    return user


def require_admin(
    user: Annotated[Usuario, Depends(get_current_user)],
) -> Usuario:
    """Permite continuar únicamente a usuarios administradores."""

    if user.rol != "ADMINISTRADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta operación.",
        )

    return user
