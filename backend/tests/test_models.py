import importlib.util
from pathlib import Path

import pytest
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from app.models import Base, Celda, Operador, Vehiculo


def test_normalizes_unique_identifiers_on_creation_and_assignment():
    vehicle = Vehiculo(placa=" \tabc123\n", color="Azul", modelo=2025, marca="Marca", tipo="MOTO")
    cell = Celda(codigo=" a-01 ", tipo="Libre")
    assert vehicle.placa == "ABC123"
    assert cell.codigo == "A-01"
    vehicle.placa = " xyz789 "
    cell.codigo = " b-02 "
    assert vehicle.placa == "XYZ789"
    assert cell.codigo == "B-02"


@pytest.mark.parametrize("model,attribute", [
    (Vehiculo, "placa"), (Vehiculo, "color"), (Vehiculo, "marca"),
    (Vehiculo, "tipo"), (Celda, "codigo"), (Celda, "tipo"),
    (Operador, "nombre"), (Operador, "telefono"),
])
@pytest.mark.parametrize("value", ["", " \t\n", None])
def test_rejects_empty_text(model, attribute, value):
    with pytest.raises(ValueError):
        model(**{attribute: value})


@pytest.mark.parametrize("value", [0, 10000, True, "2025", 2025.5, None])
def test_rejects_invalid_year(value):
    with pytest.raises(ValueError):
        Vehiculo(modelo=value)


@pytest.mark.parametrize("value", ["MOTO", "AUTOMOVIL", "CAMIONETA"])
def test_vehicle_types(value):
    assert Vehiculo(tipo=value).tipo == value


def test_rejects_unknown_type_and_preserves_phone_text():
    with pytest.raises(ValueError):
        Vehiculo(tipo="CAMION")
    assert Operador(telefono="+57 00123").telefono == "+57 00123"
    assert Celda(tipo="Categoría futura").tipo == "Categoría futura"


def test_required_columns_and_identity():
    for name in ("vehiculo", "celda", "operador"):
        table = Base.metadata.tables[name]
        assert all(not column.nullable for column in table.columns)
        assert isinstance(table.c.id.type, sa.BigInteger)
        assert table.c.id.identity.always is True


def test_migration_matches_models_without_connecting(monkeypatch):
    path = Path(__file__).resolve().parents[1] / "migrations/versions/0001_modelos_iniciales.py"
    spec = importlib.util.spec_from_file_location("initial_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    metadata = sa.MetaData()

    monkeypatch.setattr(
        migration.op,
        "create_table",
        lambda name, *args: sa.Table(name, metadata, *args),
    )

    migration.upgrade()

    expected_columns = {
        "vehiculo": ["id", "placa", "color", "modelo", "marca", "tipo"],
        "celda": ["id", "codigo", "tipo"],
        "operador": ["id", "nombre", "telefono"],
    }

    assert set(metadata.tables) == set(expected_columns)

    for name, expected in expected_columns.items():
        table = metadata.tables[name]

        assert list(table.columns.keys()) == expected
        assert all(not column.nullable for column in table.columns)
        assert isinstance(table.c.id.type, sa.BigInteger)
        assert table.c.id.identity.always is True

        unique_names = {
            constraint.name
            for constraint in table.constraints
            if isinstance(constraint, sa.UniqueConstraint)
        }

        check_names = {
            constraint.name
            for constraint in table.constraints
            if isinstance(constraint, sa.CheckConstraint)
        }

        expected_unique = {
              "vehiculo": {"uq_vehiculo_placa"},
              "celda": {"uq_celda_codigo"},
              "operador": set(),
       }

        assert unique_names == expected_unique[name]
        assert check_names

        ddl = str(
            CreateTable(table).compile(
                dialect=postgresql.dialect()
            )
        )

        assert "BIGINT GENERATED ALWAYS AS IDENTITY" in ddl
