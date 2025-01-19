from pymongo import MongoClient
from faker import Faker
import random
from datetime import datetime, timedelta

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["my_database"]  # Cambia el nombre de la base de datos
customers_table = db["customers"]  # Cambia el nombre de la colección de clientes
products_table = db["products"]  # Cambia el nombre de la colección de productos
categories_table = db["categories"]  # Cambia el nombre de la colección de categorías
orders_table = db["orders"]  # Cambia el nombre de la colección de órdenes

# Instancia de Faker
fake = Faker()

# Generar datos ficticios para clientes
def generate_customers(n):
    customers = []
    for _ in range(n):
        title_id = random.choice([1, 2, 0])  # Mr = 1, Ms = 2, else 0
        first_name = fake.first_name_male() if title_id == 1 else fake.first_name_female()
        last_name = fake.last_name()
        email = fake.email()
        password = fake.password()
        birthday = fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%Y-%m-%d")
        newsletter = random.choice([0, 1])
        opt_in = random.choice([0, 1])
        registration_date = fake.date_between(start_date="-10y", end_date="today").strftime("%Y-%m-%d")
        groups = random.choice(["Customer", "Customer, Carribean", "VIP"])
        default_group_id = random.randint(1, 5)

        customer = {
            "Customer ID": fake.uuid4(),
            "Active": 1,
            "Title ID": title_id,
            "Email": email,
            "Password": password,
            "Birthday": birthday,
            "Last Name": last_name,
            "First Name": first_name,
            "Newsletter": newsletter,
            "Opt-in": opt_in,
            "Registration Date": registration_date,
            "Groups": groups,
            "Default Group ID": default_group_id,
        }
        customers.append(customer)
    return customers

# Generar datos ficticios para productos
def generate_products(n, categories):
    products = []
    for _ in range(n):
        name = fake.word().capitalize()
        category = random.choice(categories)
        price = round(random.uniform(10, 1000), 2)
        tax_rules_id = random.randint(1, 5)
        wholesale_price = round(price * random.uniform(0.5, 0.8), 2)
        on_sale = random.choice([0, 1])
        discount_amount = round(price * random.uniform(0.05, 0.3), 2) if on_sale else 0
        discount_percent = round((discount_amount / price) * 100, 2) if on_sale else 0
        quantity = random.randint(1, 1000)
        description = fake.text(max_nb_chars=200)

        product = {
            "Product ID": fake.uuid4(),
            "Active": 1,
            "Name": name,
            "Category": category,
            "Price (tax excluded)": price,
            "Tax rules ID": tax_rules_id,
            "Wholesale price": wholesale_price,
            "On sale": on_sale,
            "Discount amount": discount_amount,
            "Discount percent": discount_percent,
            "Quantity": quantity,
            "Description": description,
        }
        products.append(product)
    return products

# Insertar categorías en la base de datos
def insert_categories(categories_data):
    categories = []
    for _, row in categories_data.iterrows():
        category = {
            "Category ID": row["Category ID"],
            "Active": row["Active (0/1)"],
            "Name": row["Name *"],
            "Parent Category": row["Parent category"],
            "Root Category": row["Root category (0/1)"],
            "Description": row["Description"],
            "Meta Title": row["Meta title"],
            "Meta Keywords": row["Meta keywords"],
            "Meta Description": row["Meta description"],
            "URL Rewritten": row["URL rewritten"],
            "Image URL": row["Image URL"],
        }
        categories.append(category)
    categories_table.insert_many(categories)
    return [cat["Name"] for cat in categories]  # Retorna los nombres de las categorías

# Generar datos ficticios para órdenes
def generate_orders(n, customer_ids, product_ids):
    orders = []
    for _ in range(n):
        order = {
            "Order ID": fake.uuid4(),
            "Customer ID": random.choice(customer_ids),
            "Product ID": random.choice(product_ids),
            "ID Carrier": random.randint(1, 10),
            "ID Lang": random.randint(1, 5),
            "ID Currency": random.randint(1, 3),
            "Total Paid": round(random.uniform(20, 500), 2),
            "Total Products": random.randint(1, 5),
            "Total Shipping": round(random.uniform(5, 50), 2),
            "Payment Method": random.choice(["Credit Card", "PayPal", "Bank Transfer"]),
            "Order Date": fake.date_between(start_date="-5y", end_date="today").strftime("%Y-%m-%d"),
        }
        orders.append(order)
    return orders

# Cargar datos del archivo CSV de categorías
import pandas as pd
categories_file_path = "categories_import.csv"
categories_df = pd.read_csv(categories_file_path, sep=';')

# Insertar datos ficticios en la base de datos
num_customers = 100  # Cambia la cantidad de clientes que deseas generar
num_products = 50  # Cambia la cantidad de productos que deseas generar
num_orders = 200  # Cambia la cantidad de órdenes que deseas generar

# Insertar categorías y obtener sus nombres
category_names = insert_categories(categories_df)

# Generar clientes y productos
fake_customers = generate_customers(num_customers)
fake_products = generate_products(num_products, category_names)

# Insertar clientes y productos
customers_table.insert_many(fake_customers)
products_table.insert_many(fake_products)

# Generar e insertar órdenes
customer_ids = [customer["Customer ID"] for customer in fake_customers]
product_ids = [product["Product ID"] for product in fake_products]
fake_orders = generate_orders(num_orders, customer_ids, product_ids)

orders_table.insert_many(fake_orders)

print(f"Se han insertado {num_customers} clientes ficticios en la colección 'customers'.")
print(f"Se han insertado {num_products} productos ficticios en la colección 'products'.")
print(f"Se han insertado {num_orders} órdenes ficticias en la colección 'orders'.")
print("Se han insertado las categorías en la colección 'categories'.")
