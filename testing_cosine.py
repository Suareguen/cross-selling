# from pymongo import MongoClient
# import pandas as pd
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.preprocessing import LabelEncoder
# import numpy as np

# # Conexión a MongoDB
# client = MongoClient("mongodb://localhost:27017/")
# db = client["my_database"]
# orders_table = db["orders"]
# products_table = db["products"]

# # 1. Extraer datos de órdenes y productos
# def extract_data():
#     # Extraer órdenes
#     orders = list(orders_table.find({}, {"Customer ID": 1, "Product ID": 1, "_id": 0}))
#     orders_df = pd.DataFrame(orders)
    
#     # Extraer productos
#     products = list(products_table.find({}, {"Product ID": 1, "Category": 1, "_id": 0}))
#     products_df = pd.DataFrame(products)
    
#     # Unir productos con categorías
#     orders_with_categories = orders_df.merge(products_df, on="Product ID")
    
#     return orders_with_categories

# # 2. Crear matriz de usuario-producto
# def create_user_product_matrix(orders_with_categories):
#     # Codificar IDs de usuarios y productos
#     user_encoder = LabelEncoder()
#     product_encoder = LabelEncoder()

#     orders_with_categories["User Index"] = user_encoder.fit_transform(orders_with_categories["Customer ID"])
#     orders_with_categories["Product Index"] = product_encoder.fit_transform(orders_with_categories["Product ID"])

#     # Crear matriz dispersa usuario-producto
#     num_users = orders_with_categories["User Index"].nunique()
#     num_products = orders_with_categories["Product Index"].nunique()
#     matrix = np.zeros((num_users, num_products))

#     for _, row in orders_with_categories.iterrows():
#         matrix[row["User Index"], row["Product Index"]] += 1  # Cuenta de interacciones

#     return matrix, user_encoder, product_encoder, orders_with_categories

# # 3. Recomendar productos usando similitud de coseno
# def recommend_products(user_id, matrix, user_encoder, product_encoder, orders_with_categories, num_recommendations=5):
#     # Verificar si el usuario existe
#     if user_id not in user_encoder.classes_:
#         print(f"El usuario {user_id} no tiene datos suficientes para generar recomendaciones.")
#         return []

#     user_index = user_encoder.transform([user_id])[0]

#     # Calcular similitud entre usuarios
#     user_similarities = cosine_similarity(matrix)
#     similar_users = np.argsort(-user_similarities[user_index])  # Ordenar usuarios similares

#     # Filtrar productos comprados por categorías del usuario
#     user_categories = orders_with_categories[orders_with_categories["Customer ID"] == user_id]["Category"].unique()
#     candidate_products = orders_with_categories[orders_with_categories["Category"].isin(user_categories)]["Product Index"].unique()

#     # Recomendar productos basados en usuarios similares
#     scores = matrix[similar_users[0:num_recommendations], :].sum(axis=0)
#     scores = [(i, scores[i]) for i in candidate_products if scores[i] > 0]
#     scores = sorted(scores, key=lambda x: x[1], reverse=True)

#     # Obtener los productos recomendados
#     recommended_products = [product_encoder.inverse_transform([product[0]])[0] for product in scores[:num_recommendations]]
#     return recommended_products

# # Ejecutar el sistema de recomendación
# if __name__ == "__main__":
#     # Extraer datos y construir la matriz usuario-producto
#     orders_with_categories = extract_data()
#     matrix, user_encoder, product_encoder, orders_with_categories = create_user_product_matrix(orders_with_categories)

#     # Seleccionar un usuario y recomendar productos
#     user_id = "3899d360-38b9-42f7-bfad-210d9cd35e73"  # Cambia por un ID de usuario real
#     recommendations = recommend_products(user_id, matrix, user_encoder, product_encoder, orders_with_categories)
#     print(f"Productos recomendados para el usuario {user_id}: {recommendations}")

#####################################################################

# from pymongo import MongoClient
# import pandas as pd
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.preprocessing import LabelEncoder
# import numpy as np

# # Conexión a MongoDB
# client = MongoClient("mongodb://localhost:27017/")
# db = client["my_database"]
# orders_table = db["orders"]
# products_table = db["products"]

# # 1. Extraer datos de órdenes y productos
# def extract_data():
#     # Extraer órdenes
#     orders = list(orders_table.find({}, {"Customer ID": 1, "Product ID": 1, "_id": 0}))
#     orders_df = pd.DataFrame(orders)
    
#     # Extraer productos (incluyendo el nombre)
#     products = list(products_table.find({}, {"Product ID": 1, "Category": 1, "Name": 1, "_id": 0}))
#     products_df = pd.DataFrame(products)
    
#     # Unir productos con categorías y nombres
#     orders_with_categories = orders_df.merge(products_df, on="Product ID")

#     # Dividir en entrenamiento y prueba
#     train_df = orders_with_categories.sample(frac=0.8, random_state=42)
#     test_df = orders_with_categories.drop(train_df.index)

#     return train_df, test_df

# # 2. Crear matriz de usuario-producto
# def create_user_product_matrix(orders_with_categories):
#     # Codificar IDs de usuarios y productos
#     user_encoder = LabelEncoder()
#     product_encoder = LabelEncoder()

#     orders_with_categories["User Index"] = user_encoder.fit_transform(orders_with_categories["Customer ID"])
#     orders_with_categories["Product Index"] = product_encoder.fit_transform(orders_with_categories["Product ID"])

#     # Crear matriz dispersa usuario-producto
#     num_users = orders_with_categories["User Index"].nunique()
#     num_products = orders_with_categories["Product Index"].nunique()
#     matrix = np.zeros((num_users, num_products))

#     for _, row in orders_with_categories.iterrows():
#         matrix[row["User Index"], row["Product Index"]] += 1  # Cuenta de interacciones

#     return matrix, user_encoder, product_encoder, orders_with_categories

# # 3. Recomendar productos usando similitud de coseno
# def recommend_products(user_id, matrix, user_encoder, product_encoder, orders_with_categories, num_recommendations=5):
#     # Verificar si el usuario existe
#     if user_id not in user_encoder.classes_:
#         print(f"El usuario {user_id} no tiene datos suficientes para generar recomendaciones.")
#         return []

#     user_index = user_encoder.transform([user_id])[0]

#     # Calcular similitud entre usuarios
#     user_similarities = cosine_similarity(matrix)
#     similar_users = np.argsort(-user_similarities[user_index])  # Ordenar usuarios similares

#     # Filtrar productos comprados por categorías del usuario
#     user_categories = orders_with_categories[orders_with_categories["Customer ID"] == user_id]["Category"].unique()
#     candidate_products = orders_with_categories[orders_with_categories["Category"].isin(user_categories)]["Product Index"].unique()

#     # Recomendar productos basados en usuarios similares
#     scores = matrix[similar_users[0:num_recommendations], :].sum(axis=0)
#     scores = [(i, scores[i]) for i in candidate_products if scores[i] > 0]
#     scores = sorted(scores, key=lambda x: x[1], reverse=True)

#     # Obtener los productos recomendados (ID y nombres)
#     product_mapping = orders_with_categories[["Product Index", "Product ID", "Name"]].drop_duplicates()
#     product_mapping = product_mapping.set_index("Product Index")

#     recommended_products = [
#         (product_mapping.loc[product[0], "Product ID"], product_mapping.loc[product[0], "Name"], product[1])
#         for product in scores[:num_recommendations]
#     ]
#     return recommended_products

# # 4. Evaluar el modelo
# def evaluate_model(test_df, matrix, user_encoder, product_encoder, orders_with_categories, num_recommendations=5):
#     precision_scores = []
#     recall_scores = []
#     all_recommendations = {}

#     for user_id in test_df["Customer ID"].unique():
#         # Verificar si el usuario está en el conjunto de entrenamiento
#         if user_id not in user_encoder.classes_:
#             continue

#         # Productos comprados en el conjunto de prueba
#         relevant_products = test_df[test_df["Customer ID"] == user_id]["Product ID"].unique()

#         # Obtener recomendaciones
#         recommendations = recommend_products(user_id, matrix, user_encoder, product_encoder, orders_with_categories, num_recommendations)
#         recommended_products = [rec[0] for rec in recommendations]  # IDs de productos recomendados

#         # Guardar recomendaciones por usuario
#         all_recommendations[user_id] = recommendations

#         # Calcular métricas
#         relevant_recommended = set(recommended_products) & set(relevant_products)
#         precision = len(relevant_recommended) / num_recommendations
#         recall = len(relevant_recommended) / len(relevant_products) if len(relevant_products) > 0 else 0

#         precision_scores.append(precision)
#         recall_scores.append(recall)

#     # Promediar métricas
#     avg_precision = np.mean(precision_scores)
#     avg_recall = np.mean(recall_scores)

#     return avg_precision, avg_recall, all_recommendations

# # Ejecutar el sistema de recomendación
# if __name__ == "__main__":
#     # Extraer datos y construir la matriz usuario-producto
#     train_df, test_df = extract_data()
#     matrix, user_encoder, product_encoder, orders_with_categories = create_user_product_matrix(train_df)

#     # Evaluar el modelo
#     avg_precision, avg_recall, all_recommendations = evaluate_model(test_df, matrix, user_encoder, product_encoder, train_df, num_recommendations=5)
#     print(f"Precision@5: {avg_precision:.2f}, Recall@5: {avg_recall:.2f}")

#     # Mostrar recomendaciones para algunos usuarios
#     for user_id, recommendations in list(all_recommendations.items())[:1]:  # Mostrar para 5 usuarios
#         print(f"Recomendaciones para el usuario {user_id}: {recommendations}")






from pymongo import MongoClient
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
import numpy as np

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["my_database"]
orders_table = db["orders"]
products_table = db["products"]

# 1. Extraer datos de órdenes y productos
def extract_data():
    # Extraer órdenes
    orders = list(orders_table.find({}, {"Customer ID": 1, "Product ID": 1, "_id": 0}))
    orders_df = pd.DataFrame(orders)
    
    # Extraer productos (incluyendo categoría y nombre)
    products = list(products_table.find({}, {"Product ID": 1, "Category": 1, "Name": 1, "_id": 0}))
    products_df = pd.DataFrame(products)
    
    # Unir productos con categorías y nombres
    orders_with_categories = orders_df.merge(products_df, on="Product ID")

    # Dividir en entrenamiento y prueba
    train_df = orders_with_categories.sample(frac=0.8, random_state=42)
    test_df = orders_with_categories.drop(train_df.index)

    return train_df, test_df

# 2. Crear matriz de usuario-producto
def create_user_product_matrix(orders_with_categories):
    # Codificar IDs de usuarios y productos
    user_encoder = LabelEncoder()
    product_encoder = LabelEncoder()

    orders_with_categories["User Index"] = user_encoder.fit_transform(orders_with_categories["Customer ID"])
    orders_with_categories["Product Index"] = product_encoder.fit_transform(orders_with_categories["Product ID"])

    # Crear matriz dispersa usuario-producto
    num_users = orders_with_categories["User Index"].nunique()
    num_products = orders_with_categories["Product Index"].nunique()
    matrix = np.zeros((num_users, num_products))

    for _, row in orders_with_categories.iterrows():
        matrix[row["User Index"], row["Product Index"]] += 1  # Cuenta de interacciones

    return matrix, user_encoder, product_encoder, orders_with_categories

# 3. Recomendar productos usando similitud de coseno (con filtro de categorías)
def recommend_products(user_id, matrix, user_encoder, product_encoder, orders_with_categories, num_recommendations=5):
    # Verificar si el usuario existe
    if user_id not in user_encoder.classes_:
        print(f"El usuario {user_id} no tiene datos suficientes para generar recomendaciones.")
        return []

    user_index = user_encoder.transform([user_id])[0]

    # Calcular similitud entre usuarios
    user_similarities = cosine_similarity(matrix)
    similar_users = np.argsort(-user_similarities[user_index])  # Ordenar usuarios similares

    # Filtrar productos comprados por categorías del usuario
    user_categories = orders_with_categories[orders_with_categories["Customer ID"] == user_id]["Category"].unique()
    candidate_products = orders_with_categories[orders_with_categories["Category"].isin(user_categories)]["Product Index"].unique()

    # Recomendar productos basados en usuarios similares
    scores = matrix[similar_users[1:], :].sum(axis=0)  # Ignorar al propio usuario
    scores = [(i, scores[i]) for i in candidate_products if scores[i] > 0]
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    # Obtener los productos recomendados (ID y nombres)
    product_mapping = orders_with_categories[["Product Index", "Product ID", "Name"]].drop_duplicates()
    product_mapping = product_mapping.set_index("Product Index")

    recommended_products = [
        (product_mapping.loc[product[0], "Product ID"], product_mapping.loc[product[0], "Name"], product[1])
        for product in scores[:num_recommendations]
    ]
    return recommended_products

# 4. Evaluar el modelo
def evaluate_model(test_df, matrix, user_encoder, product_encoder, orders_with_categories, num_recommendations=5):
    precision_scores = []
    recall_scores = []
    all_recommendations = {}

    for user_id in test_df["Customer ID"].unique():
        # Verificar si el usuario está en el conjunto de entrenamiento
        if user_id not in user_encoder.classes_:
            continue

        # Productos comprados en el conjunto de prueba
        relevant_products = test_df[test_df["Customer ID"] == user_id]["Product ID"].unique()

        # Obtener recomendaciones
        recommendations = recommend_products(user_id, matrix, user_encoder, product_encoder, orders_with_categories, num_recommendations)
        recommended_products = [rec[0] for rec in recommendations]  # IDs de productos recomendados

        # Guardar recomendaciones por usuario
        all_recommendations[user_id] = recommendations

        # Calcular métricas
        relevant_recommended = set(recommended_products) & set(relevant_products)
        precision = len(relevant_recommended) / num_recommendations
        recall = len(relevant_recommended) / len(relevant_products) if len(relevant_products) > 0 else 0

        precision_scores.append(precision)
        recall_scores.append(recall)

    # Promediar métricas
    avg_precision = np.mean(precision_scores)
    avg_recall = np.mean(recall_scores)

    return avg_precision, avg_recall, all_recommendations

# Ejecutar el sistema de recomendación
if __name__ == "__main__":
    # Extraer datos y construir la matriz usuario-producto
    train_df, test_df = extract_data()
    matrix, user_encoder, product_encoder, orders_with_categories = create_user_product_matrix(train_df)

    # Evaluar el modelo
    avg_precision, avg_recall, all_recommendations = evaluate_model(test_df, matrix, user_encoder, product_encoder, train_df, num_recommendations=5)
    print(f"Precision@5: {avg_precision:.2f}, Recall@5: {avg_recall:.2f}")

    # Mostrar recomendaciones para algunos usuarios
    for user_id, recommendations in list(all_recommendations.items())[:1]:  # Mostrar para un usuario
        print(f"Recomendaciones para el usuario {user_id}: {recommendations}")
