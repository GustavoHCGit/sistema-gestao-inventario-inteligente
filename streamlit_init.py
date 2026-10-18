import database
from seed_data import seed

database.create_tables()
if not database.get_categories():
    seed()
    print("Banco de dados inicializado com dados de exemplo.")
