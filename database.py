import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path

# Um único caminho é usado pelo dashboard, pelo seed e pelos testes. Pode ser
# substituído sem alterar o código (útil para uma instalação em outro local).
DB_PATH = Path(os.environ.get("INVENTORY_DB_PATH", Path(__file__).with_name("inventory.db")))


class DatabaseSchemaError(RuntimeError):
    """Indica um banco antigo/incompatível sem apagar os dados existentes."""


@dataclass(frozen=True)
class CategoryResult:
    """Resultado explícito de add_category, inclusive quando já existe."""

    category_id: int
    created: bool

    @property
    def duplicate(self) -> bool:
        return not self.created

    def __bool__(self) -> bool:
        return self.created


def connect_db() -> sqlite3.Connection:
    """Abre o banco com chaves estrangeiras ativadas nesta conexão."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _table_columns(conn: sqlite3.Connection, table_name: str):
    return {row[1] for row in conn.execute(f'PRAGMA table_info("{table_name}")')}


def create_tables() -> None:
    """Cria o esquema sem destruir tabelas incompatíveis.

    Bancos criados por versões antigas que não possuem as colunas essenciais
    falham de forma segura. A conversão deve ser feita após backup explícito;
    nenhuma migração destrutiva é executada automaticamente.
    """
    conn = connect_db()
    required_columns = {
        "categories": {"name"},
        "products": {"name", "category_id", "price", "stock_quantity"},
        "sales": {"product_id", "quantity", "sale_date", "total_price"},
    }
    try:
        for table_name, required in required_columns.items():
            exists = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
                (table_name,),
            ).fetchone()
            if exists:
                missing = required - _table_columns(conn, table_name)
                if missing:
                    missing_text = ", ".join(sorted(missing))
                    raise DatabaseSchemaError(
                        f"Tabela {table_name!r} incompatível; faltam: {missing_text}. "
                        "Nenhum dado foi removido. Faça backup explícito e migre o banco "
                        "manualmente antes de executar a aplicação."
                    )

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category_id INTEGER NOT NULL,
                price REAL NOT NULL CHECK (price >= 0),
                stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
                FOREIGN KEY (category_id) REFERENCES categories (id)
            );

            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_price REAL NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def add_category(name: str) -> CategoryResult:
    """Insere uma categoria ou retorna explicitamente a duplicata existente."""
    normalized_name = name.strip()
    if not normalized_name:
        raise ValueError("O nome da categoria não pode ser vazio")

    conn = connect_db()
    try:
        try:
            cursor = conn.execute(
                "INSERT INTO categories (name) VALUES (?)", (normalized_name,)
            )
            conn.commit()
            return CategoryResult(int(cursor.lastrowid), created=True)
        except sqlite3.IntegrityError:
            conn.rollback()
            existing = conn.execute(
                "SELECT id FROM categories WHERE name = ?", (normalized_name,)
            ).fetchone()
            if existing is None:
                raise
            return CategoryResult(int(existing[0]), created=False)
    finally:
        conn.close()


def add_product(name: str, category_id: int, price: float, stock: int) -> int:
    if stock < 0:
        raise ValueError("O estoque não pode ser negativo")
    conn = connect_db()
    try:
        cursor = conn.execute(
            """
            INSERT INTO products (name, category_id, price, stock_quantity)
            VALUES (?, ?, ?, ?)
            """,
            (name, category_id, price, stock),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()


def upsert_product(name: str, category_id: int, price: float, stock: int) -> int:
    """Faz upsert por nome, preservando o estoque operacional já existente."""
    if stock < 0:
        raise ValueError("O estoque não pode ser negativo")
    conn = connect_db()
    try:
        existing = conn.execute("SELECT id FROM products WHERE name = ?", (name,)).fetchone()
        if existing is not None:
            product_id = int(existing[0])
            conn.execute(
                "UPDATE products SET category_id = ?, price = ? WHERE id = ?",
                (category_id, price, product_id),
            )
            conn.commit()
            return product_id

        cursor = conn.execute(
            """
            INSERT INTO products (name, category_id, price, stock_quantity)
            VALUES (?, ?, ?, ?)
            """,
            (name, category_id, price, stock),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()


def get_product(product_id: int) -> tuple[float, int] | None:
    conn = connect_db()
    try:
        return conn.execute(
            "SELECT price, stock_quantity FROM products WHERE id = ?", (product_id,)
        ).fetchone()
    finally:
        conn.close()


def get_products():
    conn = connect_db()
    try:
        return conn.execute(
            """
            SELECT p.id, p.name, c.name, p.price, p.stock_quantity
            FROM products p
            JOIN categories c ON p.category_id = c.id
            ORDER BY p.id
            """
        ).fetchall()
    finally:
        conn.close()


def get_categories():
    conn = connect_db()
    try:
        return conn.execute("SELECT id, name FROM categories ORDER BY id").fetchall()
    finally:
        conn.close()


def record_sale(product_id: int, quantity: int, sale_date: str | None = None) -> bool:
    """Registra uma venda apenas para quantidade inteira estritamente positiva."""
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        return False

    conn = connect_db()
    try:
        conn.execute("BEGIN")
        product = conn.execute(
            "SELECT price, stock_quantity FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        if product is None or product[1] < quantity:
            conn.rollback()
            return False

        total_price = product[0] * quantity
        if sale_date is None:
            conn.execute(
                "INSERT INTO sales (product_id, quantity, total_price) VALUES (?, ?, ?)",
                (product_id, quantity, total_price),
            )
        else:
            conn.execute(
                """
                INSERT INTO sales (product_id, quantity, sale_date, total_price)
                VALUES (?, ?, ?, ?)
                """,
                (product_id, quantity, sale_date, total_price),
            )
        updated = conn.execute(
            """
            UPDATE products
            SET stock_quantity = stock_quantity - ?
            WHERE id = ? AND stock_quantity >= ?
            """,
            (quantity, product_id, quantity),
        )
        if updated.rowcount != 1:
            conn.rollback()
            return False
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def find_sale(product_id: int, quantity: int, total_price: float, sale_date: str) -> int | None:
    conn = connect_db()
    try:
        row = conn.execute(
            """
            SELECT id FROM sales
            WHERE product_id = ? AND quantity = ? AND total_price = ? AND sale_date = ?
            """,
            (product_id, quantity, total_price, sale_date),
        ).fetchone()
        return None if row is None else int(row[0])
    finally:
        conn.close()


def get_sales_report():
    conn = connect_db()
    try:
        return conn.execute(
            """
            SELECT s.id, p.name, s.quantity, s.total_price, s.sale_date
            FROM sales s
            JOIN products p ON s.product_id = p.id
            ORDER BY s.sale_date DESC, s.id DESC
            """
        ).fetchall()
    finally:
        conn.close()
