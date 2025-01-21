from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Inicializar la app de FastAPI
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las solicitudes (cambiar esto en producción)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los headers
)

# Cargar el modelo entrenado
MODEL_PATH = "recommendation_model.pkl"

try:
    with open(MODEL_PATH, "rb") as file:
        model_data = pickle.load(file)
    
    matrix = model_data["matrix"]
    user_encoder = model_data["user_encoder"]
    product_encoder = model_data["product_encoder"]
    orders_with_categories = model_data["orders_with_categories"]
except Exception as e:
    raise RuntimeError(f"Error al cargar el modelo: {e}")

# Modelo para solicitudes
class RecommendationRequest(BaseModel):
    user_id: int
    num_recommendations: int = 5

class ProductInfoRequest(BaseModel):
    product_ids: list[int]  # Lista de IDs de productos

# Función para generar recomendaciones
def recommend_products(user_id, matrix, user_encoder, product_encoder, orders_with_categories, num_recommendations=5):
    if user_id not in user_encoder.classes_:
        return [], []

    user_index = int(user_encoder.transform([user_id])[0])  # Convertir a int
    user_similarities = cosine_similarity(matrix)
    similar_users = np.argsort(-user_similarities[user_index])

    user_categories = orders_with_categories[orders_with_categories["Customer ID"] == user_id]["Category"].unique()
    candidate_products = orders_with_categories[orders_with_categories["Category"].isin(user_categories)]["Product Index"].unique()

    # Excluir productos ya comprados por el usuario
    purchased_products = orders_with_categories[orders_with_categories["Customer ID"] == user_id]["Product Index"].unique()
    candidate_products = [int(product) for product in candidate_products if product not in purchased_products]

    # Recomendar productos basados en usuarios similares
    scores = matrix[similar_users[1:], :].sum(axis=0)
    max_score = scores.max() if scores.max() > 0 else 1
    normalized_scores = [(int(i), scores[i] / max_score) for i in candidate_products if scores[i] > 0]
    normalized_scores = sorted(normalized_scores, key=lambda x: x[1], reverse=True)

    product_mapping = orders_with_categories[["Product Index", "Product ID", "Name"]].drop_duplicates()
    product_mapping = product_mapping.set_index("Product Index")

    recommended_products = [
        (
            int(product_mapping.loc[product[0], "Product ID"]),  # Convertir a int
            product_mapping.loc[product[0], "Name"],
            round(float(product[1]), 2),  # Convertir a float
        )
        for product in normalized_scores[:num_recommendations]
    ]

    user_purchases = orders_with_categories[orders_with_categories["Customer ID"] == user_id][["Product ID", "Name", "Category"]].drop_duplicates()

    return recommended_products, user_purchases

@app.post("/recommendations/")
def get_recommendations(request: RecommendationRequest):
    user_id = request.user_id
    num_recommendations = request.num_recommendations

    # Validar que los datos estén cargados
    if orders_with_categories is None or matrix is None:
        raise HTTPException(status_code=500, detail="El modelo no está completamente cargado.")

    # Obtener recomendaciones
    recommendations, user_purchases = recommend_products(
        user_id, matrix, user_encoder, product_encoder, orders_with_categories, num_recommendations
    )

    if not recommendations:
        raise HTTPException(status_code=404, detail=f"No se encontraron recomendaciones para el usuario {user_id}.")

    # Convertir user_purchases a un formato serializable
    user_purchases_serializable = user_purchases.astype(str).to_dict(orient="records") if not user_purchases.empty else []

    return {
        "user_id": int(user_id),
        "recommendations": recommendations,
        "user_purchases": user_purchases_serializable
    }

@app.post("/products/")
def get_product_info(request: ProductInfoRequest):
    product_ids = request.product_ids

    # Validar que los datos estén cargados
    if orders_with_categories is None:
        raise HTTPException(status_code=500, detail="Los datos de productos no están disponibles.")

    # Filtrar los productos solicitados
    product_info = orders_with_categories[orders_with_categories["Product ID"].isin(product_ids)][["Product ID", "Name", "Category"]].drop_duplicates()

    if product_info.empty:
        raise HTTPException(status_code=404, detail="No se encontró información para los productos solicitados.")

    return product_info.to_dict(orient="records")

# Endpoint de prueba
@app.get("/")
def root():
    return {"message": "API de recomendaciones funcionando correctamente"}
