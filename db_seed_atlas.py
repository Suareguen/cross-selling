from pymongo import MongoClient
from faker import Faker
import random
import pandas as pd

# URI de conexión a MongoDB Atlas
uri = "mongodb+srv://Suarenguen:Lampara.1@suarenguen.ay1mt6g.mongodb.net/"
client = MongoClient(uri)

# Seleccionar la base de datos
db = client["my_database"]  # Cambia el nombre de la base de datos si es necesario
customers_table = db["customers"]  # Colección de clientes
products_table = db["products"]  # Colección de productos
categories_table = db["categories"]  # Colección de categorías
orders_table = db["orders"]  # Colección de órdenes

# Instancia de Faker
fake = Faker()

# Contadores globales para IDs
category_id_counter = 1
product_id_counter = 1
customer_id_counter = 1
order_id_counter = 1

def get_next_id(counter):
    global category_id_counter, product_id_counter, customer_id_counter, order_id_counter
    if counter == "category":
        category_id_counter += 1
        return category_id_counter - 1
    elif counter == "product":
        product_id_counter += 1
        return product_id_counter - 1
    elif counter == "customer":
        customer_id_counter += 1
        return customer_id_counter - 1
    elif counter == "order":
        order_id_counter += 1
        return order_id_counter - 1

# Crear categorías generales
def create_general_categories():
    general_categories = [
        {"Category ID": get_next_id("category"), "Name": "Electronics", "Description": "Electronic gadgets and devices"},
        {"Category ID": get_next_id("category"), "Name": "Fashion", "Description": "Clothing, footwear, and accessories"},
        {"Category ID": get_next_id("category"), "Name": "Home & Furniture", "Description": "Furniture and home essentials"},
        {"Category ID": get_next_id("category"), "Name": "Sports & Outdoors", "Description": "Sporting goods and outdoor gear"},
        {"Category ID": get_next_id("category"), "Name": "Books & Media", "Description": "Books, movies, music, and games"},
        {"Category ID": get_next_id("category"), "Name": "Health & Beauty", "Description": "Health and beauty products"},
    ]
    categories_table.insert_many(general_categories)
    return {category["Name"]: category["Category ID"] for category in general_categories}

# Procesar dataset externo de productos y asignar categorías generales
def process_external_products_with_categories(file_path, general_categories_map):
    data = pd.read_csv(file_path)

    # Función para asignar una categoría general
    def assign_general_category(category_name):
        for general_category, specific_categories in {
            "Electronics": ["Mobiles", "Laptops", "Tablets", "Cameras", "Headphones"],
            "Fashion": ["Clothing", "Footwear", "Watches", "Jewelry"],
            "Home & Furniture": ["Furniture", "Home Decor", "Kitchen", "Bedding"],
            "Sports & Outdoors": ["Fitness Equipment", "Outdoor Gear", "Bicycles"],
            "Books & Media": ["Books", "Movies", "Music", "Video Games"],
            "Health & Beauty": ["Skincare", "Haircare", "Makeup", "Health Devices"],
        }.items():
            if any(specific in category_name for specific in specific_categories):
                return general_categories_map[general_category]
        return general_categories_map.get("Others", "Unknown")

    # Transformar y mapear columnas
    data["Product ID"] = [get_next_id("product") for _ in range(len(data))]
    data["Active"] = 1
    data["Name"] = data["product_name"]

    # Manejo seguro de la categoría
    def extract_category(category_tree):
        if pd.notna(category_tree) and ">>" in category_tree:
            categories = category_tree.split(">>")
            return categories[1].strip() if len(categories) > 1 else categories[0].strip()
        return "Unknown"

    data["Category"] = data["product_category_tree"].apply(extract_category)
    data["General Category ID"] = data["Category"].apply(assign_general_category)
    data["Price (tax excluded)"] = data["retail_price"]
    data["Tax rules ID"] = [random.randint(1, 5) for _ in range(len(data))]
    data["Wholesale price"] = data["retail_price"] * random.uniform(0.5, 0.8)
    data["On sale"] = data.apply(
        lambda row: 1 if row["retail_price"] > row["discounted_price"] else 0, axis=1
    )
    data["Discount amount"] = data["retail_price"] - data["discounted_price"]
    data["Discount percent"] = (data["Discount amount"] / data["retail_price"]) * 100
    data["Quantity"] = [random.randint(1, 100) for _ in range(len(data))]
    data["Description"] = data["description"]

    # Seleccionar columnas necesarias
    mapped_products = data[[
        "Product ID", "Active", "Name", "Category", "General Category ID", 
        "Price (tax excluded)", "Tax rules ID", "Wholesale price", 
        "On sale", "Discount amount", "Discount percent", "Quantity", "Description"
    ]]
    return mapped_products.to_dict(orient="records")

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
            "Customer ID": get_next_id("customer"),
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

# Generar órdenes realistas
def generate_orders_realistic(n, customer_ids, product_ids, product_categories, product_prices):
    orders = []
    customer_profiles = {
        customer_id: {
            "preferred_categories": random.sample(
                list(set(product_categories.values())), k=random.randint(1, 3)
            ),
            "price_range": (random.uniform(10, 100), random.uniform(200, 500)),
        }
        for customer_id in customer_ids
    }

    for _ in range(n):
        customer_id = random.choice(customer_ids)
        profile = customer_profiles[customer_id]
        
        preferred_products = [
            prod_id for prod_id in product_ids
            if product_categories[prod_id] in profile["preferred_categories"]
            and profile["price_range"][0] <= product_prices[prod_id] <= profile["price_range"][1]
        ]
        
        if not preferred_products:
            preferred_products = product_ids
        
        num_products_in_order = random.randint(1, min(5, len(preferred_products)))
        selected_products = random.sample(preferred_products, k=num_products_in_order)

        for product_id in selected_products:
            order = {
                "Order ID": get_next_id("order"),
                "Customer ID": customer_id,
                "Product ID": product_id,
                "Quantity": random.randint(1, 10),
            }
            orders.append(order)
    return orders


# Archivo externo de productos
products_file_path = "flipkart_com-ecommerce_sample.csv"
print("Creando Base de Datos...")
# Crear categorías generales e insertar en la base de datos
general_categories_map = create_general_categories()

# Procesar y cargar productos con categorías generales
processed_products = process_external_products_with_categories(products_file_path, general_categories_map)
products_table.insert_many(processed_products)

# Generar clientes ficticios
num_customers = 1000
fake_customers = generate_customers(num_customers)
customers_table.insert_many(fake_customers)

# Generar y almacenar órdenes realistas
customer_ids = [customer["Customer ID"] for customer in fake_customers]
product_ids = [product["Product ID"] for product in processed_products]
product_data = pd.DataFrame(processed_products)
product_categories = dict(zip(product_data["Product ID"], product_data["General Category ID"]))
product_prices = dict(zip(product_data["Product ID"], product_data["Price (tax excluded)"]))
num_orders = 50000
fake_orders = generate_orders_realistic(num_orders, customer_ids, product_ids, product_categories, product_prices)
orders_table.insert_many(fake_orders)

print(f"Se han insertado {num_customers} clientes ficticios en la colección 'customers'.")
print(f"Se han insertado {len(processed_products)} productos con categorías generales en la colección 'products'.")
print(f"Se han insertado {num_orders} órdenes realistas en la colección 'orders'.")
print(f"Se han creado 6 categorías generales en la colección 'categories'.")
