import random
from datetime import datetime, timedelta

import database

SEED = 42
CATEGORIES = ["Eletrônicos", "Escritório", "Alimentos", "Limpeza"]
PRODUCTS = [
    ("Notebook", "Eletrônicos", 3500.00, 10),
    ("Mouse Wireless", "Eletrônicos", 89.90, 50),
    ("Cadeira Ergonômica", "Escritório", 1200.00, 5),
    ("Café 500g", "Alimentos", 18.50, 100),
    ("Monitor 24'", "Eletrônicos", 850.00, 15),
    ("Papel A4 (Resma)", "Escritório", 25.00, 200),
]


def seed():
    """Carrega dados de demonstração sem duplicar registros existentes."""
    database.create_tables()

    category_ids = {}
    for category_name in CATEGORIES:
        result = database.add_category(category_name)
        category_ids[category_name] = result.category_id

    product_ids = {}
    product_prices = {}
    for name, category_name, price, stock in PRODUCTS:
        product_ids[name] = database.upsert_product(
            name, category_ids[category_name], price, stock
        )
        product_prices[name] = price

    # Randomness is local and fixed, so the fixture is reproducible in every run.
    rng = random.Random(SEED)
    product_names = [product[0] for product in PRODUCTS]
    sale_ids = []
    base_date = datetime(2024, 1, 1)
    for index in range(10):
        product_name = rng.choice(product_names)
        quantity = rng.randint(1, 3)
        product_id = product_ids[product_name]
        sale_date = (base_date + timedelta(days=index)).isoformat(sep=" ")
        total_price = product_prices[product_name] * quantity

        sale_id = database.find_sale(product_id, quantity, total_price, sale_date)
        if sale_id is None and database.record_sale(product_id, quantity, sale_date):
            sale_id = database.find_sale(product_id, quantity, total_price, sale_date)
        if sale_id is not None:
            sale_ids.append(sale_id)

    return {"categories": category_ids, "products": product_ids, "sales": sale_ids}


if __name__ == "__main__":
    seed()
    print("Banco de dados populado com sucesso!")
