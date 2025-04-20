
from fastapi.staticfiles import StaticFiles
from routes.album_router import router as album_router
from routes.image_router import router as image_router
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI


app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes cambiar "*" por "http://localhost:3000" si es el frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los headers
)

app.include_router(image_router, prefix='/images')
app.include_router(album_router, prefix='/albums')
app.mount("/static", StaticFiles(directory="uploads"), name="static")



