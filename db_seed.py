import pymongo
import random
from faker import Faker
import datetime
import numpy as np

# Configuración de MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["ecommerce_cross"]

# Crear instancias de las colecciones
users_collection = db["users"]
products_collection = db["products"]
interactions_collection = db["interactions"]

# Limpiar la base de datos existente
users_collection.delete_many({})
products_collection.delete_many({})
interactions_collection.delete_many({})

# Instancia de Faker
fake = Faker()

# Generar usuarios
def generate_users(n_users=1000):
    users = []
    for i in range(n_users):
        user = {
            "_id": str(i + 1),
            "name": fake.name(),
            "email": fake.email(),
            "created_at": fake.date_time_this_decade()
        }
        users.append(user)
    users_collection.insert_many(users)

# Generar productos
def generate_products(n_products=500):
    categories = ["Electronics", "Books", "Clothing", "Home", "Toys", "Sports", "Beauty"]
    products = []
    for i in range(n_products):
        product = {
            "_id": str(i + 1),
            "name": fake.catch_phrase(),
            "category": random.choice(categories),
            "price": round(random.uniform(5.0, 500.0), 2),
            "created_at": fake.date_time_this_decade()
        }
        products.append(product)
    products_collection.insert_many(products)

# Generar interacciones
def generate_interactions(n_interactions=100000):
    user_ids = [user["_id"] for user in users_collection.find()]
    product_ids = [product["_id"] for product in products_collection.find()]
    interactions = []

    for _ in range(n_interactions):
        interaction = {
            "user_id": random.choice(user_ids),
            "product_id": random.choice(product_ids),
            "interaction": random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0],  # 1: Viewed, 2: Added to Cart, 3: Purchased
            "timestamp": fake.date_time_this_year()
        }
        interactions.append(interaction)
    
    # Inserción en lotes para mayor rendimiento
    batch_size = 1000
    for i in range(0, len(interactions), batch_size):
        interactions_collection.insert_many(interactions[i:i + batch_size])

# Llamadas para generar los datos
print("Generando usuarios...")
generate_users(n_users=1000)

print("Generando productos...")
generate_products(n_products=500)

print("Generando interacciones...")
generate_interactions(n_interactions=100000)

print("¡Base de datos generada exitosamente!")
