import sqlite3

import pytest

import database
from seed_data import seed


@pytest.fixture
def isolated_database(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "inventory.db")
    database.create_tables()
    return database.DB_PATH


def _product_id():
    category = database.add_category("Eletrônicos")
    return database.add_product("Produto teste", category.category_id, 10.0, 3)


def test_foreign_keys_are_enabled_for_every_connection(isolated_database):
    with database.connect_db() as conn:
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_product_with_unknown_category_fails(isolated_database):
    with pytest.raises(sqlite3.IntegrityError):
        database.add_product("Sem categoria", 999, 10.0, 1)


def test_negative_sale_is_rejected_without_increasing_stock(isolated_database):
    product_id = _product_id()

    assert database.record_sale(product_id, -1) is False
    assert database.get_product(product_id) == (10.0, 3)
    with database.connect_db() as conn:
        assert conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 0


def test_sale_decreases_stock_and_insufficient_stock_is_atomic(isolated_database):
    product_id = _product_id()

    assert database.record_sale(product_id, 2) is True
    assert database.get_product(product_id) == (10.0, 1)
    assert database.record_sale(product_id, 2) is False
    assert database.get_product(product_id) == (10.0, 1)


def test_duplicate_category_is_reported_with_existing_id(isolated_database):
    first = database.add_category("Escritório")
    duplicate = database.add_category("Escritório")

    assert first.created is True
    assert duplicate.duplicate is True
    assert duplicate.category_id == first.category_id
    assert len(database.get_categories()) == 1


def test_seed_is_deterministic_and_idempotent(isolated_database):
    first = seed()
    with database.connect_db() as conn:
        first_snapshot = conn.execute(
            "SELECT name, category_id, price, stock_quantity FROM products ORDER BY id"
        ).fetchall()
        first_sales = conn.execute(
            "SELECT product_id, quantity, sale_date, total_price FROM sales ORDER BY id"
        ).fetchall()

    second = seed()
    with database.connect_db() as conn:
        second_snapshot = conn.execute(
            "SELECT name, category_id, price, stock_quantity FROM products ORDER BY id"
        ).fetchall()
        second_sales = conn.execute(
            "SELECT product_id, quantity, sale_date, total_price FROM sales ORDER BY id"
        ).fetchall()

    assert first == second
    assert first_snapshot == second_snapshot
    assert first_sales == second_sales
    assert len(first["categories"]) == 4
    assert len(first["products"]) == 6
    assert len(first["sales"]) == 10


def test_incompatible_schema_fails_without_dropping_data(tmp_path, monkeypatch):
    db_path = tmp_path / "legacy.db"
    monkeypatch.setattr(database, "DB_PATH", db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
        conn.execute("INSERT INTO products (name) VALUES ('legado')")
        conn.commit()

    with pytest.raises(database.DatabaseSchemaError):
        database.create_tables()

    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT name FROM products").fetchone()[0] == "legado"
        assert conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'products'"
        ).fetchone()[0] == "products"
