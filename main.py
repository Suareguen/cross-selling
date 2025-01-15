from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]

# Inicializar FastAPI
app = FastAPI()

# Cargar datos desde MongoDB
def load_data():
    interactions = pd.DataFrame(list(db.interactions.find()))
    if interactions.empty:
        raise RuntimeError("No se encontraron interacciones en la base de datos.")
    return interactions

# Crear matriz de interacción
def create_interaction_matrix(interactions):
    matrix = interactions.pivot_table(
        index="user_id", columns="product_id", values="interaction", fill_value=0
    )
    sparse_matrix = csr_matrix(matrix)
    return sparse_matrix, matrix

# Entrenar modelo KNN
def train_knn(sparse_matrix):
    knn_model = NearestNeighbors(metric="cosine", algorithm="brute")
    knn_model.fit(sparse_matrix)
    return knn_model

# Cargar modelo KNN (entrenar si es necesario)
try:
    interactions = load_data()
    sparse_matrix, interaction_matrix = create_interaction_matrix(interactions)
    knn_model = train_knn(sparse_matrix)
    print("Modelo KNN entrenado con éxito.")
except Exception as e:
    print(f"Error durante la carga o entrenamiento del modelo: {e}")

# Endpoints
@app.post("/register_user")
async def register_user(name: str, email: str):
    user = {"name": name, "email": email}
    result = db.users.insert_one(user)
    return {"message": "Usuario registrado correctamente", "user_id": str(result.inserted_id)}

@app.post("/register_product")
async def register_product(name: str, category: str, price: float):
    product = {"name": name, "category": category, "price": price}
    result = db.products.insert_one(product)
    return {"message": "Producto registrado correctamente", "product_id": str(result.inserted_id)}

@app.post("/register_interaction")
async def register_interaction(user_id: str, product_id: str, interaction: int):
    interaction_data = {"user_id": user_id, "product_id": product_id, "interaction": interaction}
    result = db.interactions.insert_one(interaction_data)
    return {"message": "Interacción registrada correctamente", "interaction_id": str(result.inserted_id)}

@app.get("/recommend/{user_id}")
async def recommend(user_id: str, top_n: int = Query(5, ge=1, le=20, description="Número de recomendaciones")):
    # Verificar si el usuario existe en la base de datos
    if user_id not in interaction_matrix.index:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {user_id} no encontrado")

    # Obtener las recomendaciones
    user_index = interaction_matrix.index.get_loc(user_id)
    distances, indices = knn_model.kneighbors(interaction_matrix.iloc[user_index, :].values.reshape(1, -1), n_neighbors=top_n + 1)

    # Excluir el propio usuario de los resultados
    similar_users = indices.flatten()[1:]
    recommended_products = interaction_matrix.iloc[similar_users].sum(axis=0).sort_values(ascending=False)
    recommended_products = recommended_products[interaction_matrix.loc[user_id] == 0].head(top_n)

    return {"user_id": user_id, "recommendations": recommended_products.index.tolist()}
