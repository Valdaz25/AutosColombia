
from functools import wraps

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Operador, Usuario
from app.schemas.usuario import UsuarioActualizar, UsuarioCrear
from app.security import hash_password


class UsuarioError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


def database_operation(operation):
    """Controla errores de base de datos y revierte transacciones fallidas."""

    @wraps(operation)
    def wrapped(session: Session, *args, **kwargs):
        try:
            return operation(session, *args, **kwargs)

        except IntegrityError as error:
            session.rollback()

            code = getattr(error.orig, "sqlstate", None)
            constraint = getattr(
                getattr(error.orig, "diag", None),
                "constraint_name",
                None,
            )

            if code == "23505" and constraint == "uq_usuario_nombre_usuario":
                raise UsuarioError(
                    409,
                    "Ya existe una cuenta con ese nombre de usuario.",
                ) from None

            if code == "23505" and constraint == "uq_usuario_operador":
                raise UsuarioError(
                    409,
                    "El operador ya tiene una cuenta asociada.",
                ) from None

            if code == "23503":
                raise UsuarioError(
                    409,
                    "El operador asociado no existe o tiene registros relacionados.",
                ) from None

            if code in {"23502", "23514"}:
                raise UsuarioError(
                    422,
                    "Los datos incumplen las restricciones del usuario.",
                ) from None

            raise UsuarioError(
                409,
                "La operación entra en conflicto con los datos existentes.",
            ) from None

        except SQLAlchemyError:
            session.rollback()
            raise UsuarioError(
                503,
                "No se pudo completar la operación con la base de datos.",
            ) from None

    return wrapped


def validar_operador(session: Session, operador_id: int) -> Operador:
    """Comprueba que el operador exista y esté activo."""

    operator = session.get(Operador, operador_id)

    if operator is None:
        raise UsuarioError(404, "El operador asociado no existe.")

    if not operator.activo:
        raise UsuarioError(
            409,
            "No se puede asociar una cuenta a un operador inactivo.",
        )

    return operator


@database_operation
def create_user(session: Session, data: UsuarioCrear) -> Usuario:
    """Crea una cuenta y almacena únicamente el hash de su contraseña."""

    user_data = data.model_dump(exclude={"password"})

    if data.rol == "OPERADOR":
        validar_operador(session, data.operador_id)

    user = Usuario(
        **user_data,
        password_hash=hash_password(data.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@database_operation
def update_user(
    session: Session,
    user_id: int,
    data: UsuarioActualizar,
) -> Usuario:
    """Actualiza los datos de una cuenta."""

    user = session.get(Usuario, user_id)

    if user is None:
        raise UsuarioError(404, "Usuario no encontrado.")

    if data.rol == "OPERADOR":
        validar_operador(session, data.operador_id)

    user.nombre_usuario = data.nombre_usuario
    user.rol = data.rol
    user.operador_id = data.operador_id

    if data.password:
        user.password_hash = hash_password(data.password)

    session.commit()
    session.refresh(user)

    return user


@database_operation
def change_user_status(
    session: Session,
    user_id: int,
    activo: bool,
) -> Usuario:
    """Activa o desactiva una cuenta."""

    user = session.get(Usuario, user_id)

    if user is None:
        raise UsuarioError(404, "Usuario no encontrado.")

    user.activo = activo

    session.commit()
    session.refresh(user)

    return user


@database_operation
def list_users(session: Session, offset: int, limit: int) -> dict:
    """Lista las cuentas sin exponer hashes de contraseñas."""

    total = session.scalar(
        select(func.count()).select_from(Usuario)
    )

    items = list(
        session.scalars(
            select(Usuario)
            .order_by(Usuario.id)
            .offset(offset)
            .limit(limit)
        )
    )

    return {
        "items": items,
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@database_operation
def get_user(session: Session, user_id: int) -> Usuario:
    """Busca una cuenta por su identificador."""

    user = session.get(Usuario, user_id)

    if user is None:
        raise UsuarioError(404, "Usuario no encontrado.")

    return user
