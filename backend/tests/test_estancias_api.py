
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.database import get_session


def sesion_falsa():
    """Evita conectar a PostgreSQL en pruebas que solo validan solicitudes."""
    yield None


@pytest.fixture(autouse=True)
def reemplazar_sesion():
    anteriores = app.dependency_overrides.copy()
    app.dependency_overrides[get_session] = sesion_falsa

    yield

    app.dependency_overrides.clear()
    app.dependency_overrides.update(anteriores)


def test_openapi_y_salud():
    with TestClient(app) as client:
        schema = client.get('/openapi.json').json()

        for path, method in [
            ('/estancias/entrada', 'post'),
            ('/estancias/salida', 'post'),
            ('/estancias/vehiculo/{placa}', 'get')
        ]:
            assert method in schema['paths'][path]

        assert client.get('/health').json() == {'status': 'ok'}


@pytest.mark.parametrize('payload', [
    {},
    {'placa': ' ', 'celda_id': 1, 'operador_id': 1},
    {'placa': None, 'celda_id': 1, 'operador_id': 1},
    {'placa': 'TEST', 'celda_id': 0, 'operador_id': 1},
    {'placa': 'TEST', 'celda_id': True, 'operador_id': 1},
    {'placa': 'TEST', 'celda_id': '1', 'operador_id': 1},
    {'placa': 'TEST', 'celda_id': 1, 'operador_id': None},
    {'placa': 'TEST', 'celda_id': 1, 'operador_id': 9223372036854775808},
    {'placa': 'TEST', 'celda_id': 1, 'operador_id': 1, 'entrada': '2026-01-01'},
])
def test_entrada_invalida(payload):
    with TestClient(app) as client:
        respuesta = client.post('/estancias/entrada', json=payload)
        assert respuesta.status_code == 422


def test_salida_no_admite_celda_ni_fecha():
    with TestClient(app) as client:
        for extra in (
            {'celda_id': 1},
            {'salida': '2026-01-01'},
            {'id': 1}
        ):
            respuesta = client.post(
                '/estancias/salida',
                json={'placa': 'TEST', 'operador_id': 1, **extra}
            )
            assert respuesta.status_code == 422

        assert client.get('/estancias/vehiculo/%20%20').status_code == 422
