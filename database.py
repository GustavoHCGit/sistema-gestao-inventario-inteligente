import sqlite3

def connect_db():
    return sqlite3.connect('inventory.db')

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Tabela de Categorias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Tabela de Produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # Tabela de Vendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_price REAL NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_category(name):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def add_product(name, category_id, price, stock):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, category_id, price, stock_quantity) VALUES (?, ?, ?, ?)", 
                   (name, category_id, price, stock))
    conn.commit()
    conn.close()

def get_products():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, p.name, c.name, p.price, p.stock_quantity 
        FROM products p 
        JOIN categories c ON p.category_id = c.id
    ''')
    products = cursor.fetchall()
    conn.close()
    return products

def get_categories():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()
    conn.close()
    return categories

def record_sale(product_id, quantity):
    conn = connect_db()
    cursor = conn.cursor()
    
    # Buscar preço do produto
    cursor.execute("SELECT price, stock_quantity FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    
    if product and product[1] >= quantity:
        total_price = product[0] * quantity
        cursor.execute("INSERT INTO sales (product_id, quantity, total_price) VALUES (?, ?, ?)", 
                       (product_id, quantity, total_price))
        cursor.execute("UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?", 
                       (quantity, product_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def get_sales_report():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.id, p.name, s.quantity, s.total_price, s.sale_date 
        FROM sales s 
        JOIN products p ON s.product_id = p.id
        ORDER BY s.sale_date DESC
    ''')
    sales = cursor.fetchall()
    conn.close()
    return sales
