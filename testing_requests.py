import requests

url = "http://127.0.0.1:8000/recommendations/"
data = {
    "user_id": 1,  # Asegúrate de que este ID existe en la base de datos
    "num_recommendations": 5
}

try:
    response = requests.post(url, json=data)
    response.raise_for_status()  # Lanza una excepción si hay un error HTTP

    recommendations = response.json().get('recommendations', [])
    print("Recomendaciones:", recommendations)

except requests.exceptions.RequestException as e:
    print("Error al hacer la solicitud:", e)
