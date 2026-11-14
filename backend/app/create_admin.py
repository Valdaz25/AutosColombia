
from getpass import getpass

from pydantic import TypeAdapter, ValidationError
from sqlalchemy import func, select

from app.database import get_session
from app.models import Usuario
from app.schemas.usuario import NombreUsuario
from app.security import hash_password


def main() -> None:
    session_generator = get_session()
    session = next(session_generator)

    try:
        admin_count = session.scalar(
            select(func.count())
            .select_from(Usuario)
            .where(Usuario.rol == "ADMINISTRADOR")
        )

        if admin_count:
            print("Ya existe un administrador. No se creó otra cuenta.")
            return

        nombre_usuario = input("Nombre de usuario: ").strip().lower()

        try:
            nombre_usuario = TypeAdapter(
                NombreUsuario
            ).validate_python(nombre_usuario)
        except ValidationError:
            print(
                "Nombre inválido. Usa entre 3 y 50 caracteres: "
                "letras minúsculas, números, puntos, guiones o guiones bajos."
            )
            return

        password = getpass("Contraseña (mínimo 12 caracteres): ")
        confirmation = getpass("Confirma la contraseña: ")

        if not 12 <= len(password) <= 128:
            print("La contraseña debe tener entre 12 y 128 caracteres.")
            return

        if password != confirmation:
            print("Las contraseñas no coinciden.")
            return

        user = Usuario(
            nombre_usuario=nombre_usuario,
            password_hash=hash_password(password),
            rol="ADMINISTRADOR",
            operador_id=None,
            activo=True,
        )

        session.add(user)
        session.commit()

        print("Administrador creado correctamente.")
        print(f"Nombre de usuario: {user.nombre_usuario}")

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
        session_generator.close()


if __name__ == "__main__":
    main()
