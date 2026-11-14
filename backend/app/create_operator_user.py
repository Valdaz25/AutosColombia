from getpass import getpass

from sqlalchemy import select

from app.database import get_session
from app.models import Operador, Usuario
from app.schemas.usuario import UsuarioCrear
from app.services.usuario import create_user


def main():
    generator = get_session()
    session = next(generator)

    try:
        operador_id = 17

        operador = session.get(Operador, operador_id)

        if operador is None:
            print("No se encontró el operador.")
            return

        existing = session.scalar(
            select(Usuario).where(
                Usuario.operador_id == operador_id
            )
        )

        if existing:
            print("Este operador ya tiene una cuenta.")
            return

        print(f"Operador: {operador.nombre}")
        nombre_usuario = input("Nombre de usuario: ").strip()
        password = getpass("Contraseña (mínimo 12 caracteres): ")
        confirmation = getpass("Confirma la contraseña: ")

        if password != confirmation:
            print("Las contraseñas no coinciden.")
            return

        data = UsuarioCrear(
            nombre_usuario=nombre_usuario,
            password=password,
            rol="OPERADOR",
            operador_id=operador_id,
        )

        user = create_user(session, data)

        print("Cuenta de operador creada correctamente.")
        print(f"Usuario: {user.nombre_usuario}")
        print(f"Operador asociado: {user.operador_id}")

    finally:
        session.close()
        generator.close()


if __name__ == "__main__":
    main()