from database import create_tables, add_category, add_product, record_sale
import random

def seed():
    create_tables()
    
    # Adicionar Categorias
    categories = ["Eletrônicos", "Escritório", "Alimentos", "Limpeza"]
    for cat in categories:
        add_category(cat)
    
    # Adicionar Produtos
    products = [
        ("Notebook", 1, 3500.00, 10),
        ("Mouse Wireless", 1, 89.90, 50),
        ("Cadeira Ergonômica", 2, 1200.00, 5),
        ("Café 500g", 3, 18.50, 100),
        ("Monitor 24'", 1, 850.00, 15),
        ("Papel A4 (Resma)", 2, 25.00, 200)
    ]
    
    for name, cat_id, price, stock in products:
        add_product(name, cat_id, price, stock)
    
    # Simular algumas vendas
    for _ in range(10):
        prod_id = random.randint(1, 6)
        qty = random.randint(1, 3)
        record_sale(prod_id, qty)

if __name__ == "__main__":
    seed()
    print("Banco de dados populado com sucesso!")
