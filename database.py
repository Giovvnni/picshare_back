from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()  # Cargar las variables de entorno desde .env

# Obtener la URI de MongoDB desde las variables de entorno
MONGO_URI = os.getenv("MONGO_URI")  # Si no está definida, usa la URI por defecto

# Conexión a la base de datos
client = MongoClient(MONGO_URI)
db = client["test"]
images_collection = db["images"]
album_collection = db["albums"]
