from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Usuario
from app.security import create_access_token, verify_password


class AuthError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


def authenticate_user(
    session: Session,
    nombre_usuario: str,
    password: str,
) -> dict:
    """Valida las credenciales y genera un token de acceso."""

    user = session.scalar(
        select(Usuario).where(
            Usuario.nombre_usuario == nombre_usuario.strip().lower()
        )
    )

    if user is None or not user.activo:
        raise AuthError(
            401,
            "Nombre de usuario o contraseña incorrectos.",
        )

    if not verify_password(password, user.password_hash):
        raise AuthError(
            401,
            "Nombre de usuario o contraseña incorrectos.",
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }