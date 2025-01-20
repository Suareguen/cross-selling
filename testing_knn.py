from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import matplotlib.pyplot as plt

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["my_database"]
orders_table = db["orders"]
products_table = db["products"]

# 1. Crear una matriz de interacción usuario-producto
def create_interaction_matrix():
    """
    Combina los datos de MongoDB para crear una matriz de interacción usuario-producto.

    Returns:
        pd.DataFrame: Matriz de interacción usuario-producto.
        pd.DataFrame: Datos combinados de órdenes con productos y categorías.
    """
    # Extraer órdenes
    orders = list(orders_table.find({}, {"Customer ID": 1, "Product ID": 1, "_id": 0}))
    orders_df = pd.DataFrame(orders)

    # Extraer productos (incluyendo categoría y nombre)
    products = list(products_table.find({}, {"Product ID": 1, "Category": 1, "Name": 1, "_id": 0}))
    products_df = pd.DataFrame(products)

    # Unir órdenes con productos y categorías
    interactions = orders_df.merge(products_df, on="Product ID", how="left")

    # Crear matriz de interacción usuario-producto
    interaction_matrix = interactions.pivot_table(
        index="Customer ID",  # Usuarios
        columns="Product ID",  # Productos
        values="Category",     # Interacciones (conteo)
        aggfunc="count",
        fill_value=0
    )

    return interaction_matrix, interactions

# 2. Entrenar modelo KNN
def train_knn_model(interaction_matrix):
    """
    Entrena un modelo KNN usando la matriz de interacción usuario-producto.

    Args:
        interaction_matrix (pd.DataFrame): Matriz de interacción usuario-producto.

    Returns:
        NearestNeighbors: Modelo KNN entrenado.
        csr_matrix: Matriz de interacción en formato disperso.
    """
    # Convertir la matriz a formato disperso
    sparse_matrix = csr_matrix(interaction_matrix)

    # Entrenar modelo KNN
    knn_model = NearestNeighbors(metric="cosine", algorithm="brute")
    knn_model.fit(sparse_matrix)
    print("Modelo KNN entrenado correctamente.")

    return knn_model, sparse_matrix

# 3. Recomendar productos basados en categorías del usuario
def recommend_products_filtered(user_id, interaction_matrix, interactions, knn_model, num_recommendations=5):
    """
    Recomienda productos para un usuario específico, filtrando por categorías de interés.

    Args:
        user_id (str): ID del usuario.
        interaction_matrix (pd.DataFrame): Matriz de interacción usuario-producto.
        interactions (pd.DataFrame): Datos combinados de órdenes con productos y categorías.
        knn_model: Modelo KNN entrenado.
        num_recommendations (int): Número de recomendaciones.

    Returns:
        pd.DataFrame: Productos recomendados con relevancia.
    """
    # Verificar si el usuario está en la matriz
    if user_id not in interaction_matrix.index:
        print(f"El usuario {user_id} no tiene datos suficientes para generar recomendaciones.")
        return pd.DataFrame()

    # Obtener las categorías de productos comprados por el usuario
    user_categories = interactions[interactions["Customer ID"] == user_id]["Category"].unique()

    # Obtener índice del usuario
    user_index = interaction_matrix.index.get_loc(user_id)

    # Obtener los vecinos más cercanos
    distances, indices = knn_model.kneighbors(
        interaction_matrix.iloc[user_index, :].values.reshape(1, -1), n_neighbors=6
    )

    # Excluir al propio usuario
    similar_users = indices.flatten()[1:]

    # Filtrar productos de las categorías de interés
    candidate_products = interactions[
        interactions["Category"].isin(user_categories)
    ]["Product ID"].unique()

    # Recomendar productos basados en vecinos
    recommended_products = interaction_matrix.iloc[similar_users].sum(axis=0).sort_values(ascending=False)
    recommended_products = recommended_products.loc[candidate_products]  # Filtrar solo productos relevantes

    # Crear un DataFrame con los productos recomendados
    recommended_products_df = recommended_products.head(num_recommendations).reset_index()
    recommended_products_df.columns = ["Producto", "Relevancia"]

    # Combinar con nombres de productos
    product_names = interactions[["Product ID", "Name"]].drop_duplicates().set_index("Product ID")
    recommended_products_df["Nombre"] = recommended_products_df["Producto"].map(product_names["Name"])

    return recommended_products_df

# 4. Visualizar recomendaciones
def plot_recommendations(recommendations, user_id):
    """
    Grafica las recomendaciones para un usuario.

    Args:
        recommendations (pd.DataFrame): DataFrame con productos recomendados y relevancia.
        user_id (str): ID del usuario.
    """
    recommendations.plot(
        x="Nombre", y="Relevancia", kind="bar", figsize=(10, 6), legend=False
    )
    plt.title(f"Top productos recomendados para el usuario {user_id}")
    plt.xlabel("Producto")
    plt.ylabel("Relevancia")
    plt.xticks(rotation=45)
    plt.show()

# 5. Ejecución principal
if __name__ == "__main__":
    # Crear la matriz de interacción y extraer datos combinados
    interaction_matrix, interactions = create_interaction_matrix()

    # Entrenar modelo KNN
    knn_model, sparse_matrix = train_knn_model(interaction_matrix)

    # Probar recomendaciones para un usuario
    user_id = "4bbdbd43-2420-4c6a-924b-cace33d9bf92"  # Cambiar por un ID válido
    recommendations = recommend_products_filtered(user_id, interaction_matrix, interactions, knn_model, num_recommendations=5)

    if not recommendations.empty:
        print(f"Productos recomendados para el usuario {user_id}:\n{recommendations}")
        plot_recommendations(recommendations, user_id)
    else:
        print(f"No se pudieron generar recomendaciones para el usuario {user_id}.")
