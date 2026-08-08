import os
import sqlite3
from seed_data import seed

# Inicializar banco de dados se não existir
if not os.path.exists('inventory.db'):
    seed()
    print("Banco de dados inicializado com dados de exemplo.")
