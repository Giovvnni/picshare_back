
import hashlib, uuid
from importlib.resources import contents
from typing import List
from bson import ObjectId
from database import images_collection, album_collection
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, Query, UploadFile


router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.get("/{album_id}")
async def get_album_images(album_id: str, access_key: str = Query(...)):
    album = album_collection.find_one({"_id": ObjectId(album_id)})

    if not album:
        raise HTTPException(status_code=404, detail="Álbum no encontrado")

    if access_key != album.get("master_key") and access_key != album.get("read_key"):
        raise HTTPException(status_code=403, detail="No tienes permiso para ver las imágenes")

    images = list(images_collection.find({"album_id": album_id}))
    if not images:
        raise HTTPException(status_code=404, detail="not found images") 
    for img in images:
        img["_id"] = str(img["_id"])  # Convertir ObjectId a string
    return {"images": images}

                                      
                                    

@router.post('/upload/{album_id}')
async def upload_images(
    album_id: str,
    files: List[UploadFile] = File(...),
    access_key: str = Query(...)
):
    album = album_collection.find_one({"_id": ObjectId(album_id)})

    if not album:
        raise HTTPException(status_code=404, detail="Álbum no encontrado")

    if access_key != album.get("master_key"):
        raise HTTPException(status_code=403, detail="No tienes permiso para subir imágenes")

    uploaded_image_ids = []

    for file in files:
        content = await file.read()
        ext = file.filename.split('.')[-1]
        encrypted_name = hashlib.sha256(content).hexdigest()[:16] + "_" + str(uuid.uuid4())[:8] + "." + ext

        file_path = UPLOAD_DIR / encrypted_name
        with file_path.open("wb") as buffer:
            buffer.write(content)

        image_data = {
            "album_id": album_id,
            "filename": encrypted_name,
            "uploaded_at": datetime.now(),
            "encrypted": False
        }

        result = images_collection.insert_one(image_data)
        uploaded_image_ids.append(str(result.inserted_id))

    return {
        "message": f"{len(uploaded_image_ids)} imágenes subidas correctamente.",
        "image_ids": uploaded_image_ids
    }



@router.delete('/delete/')
async def delete_image(image_id: str):
    image = images_collection.find_one({"_id": ObjectId(image_id)})

    if not image:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    
    file_path = UPLOAD_DIR / image["filename"]
    
    if file_path.exists():
        file_path.unlink()
    images_collection.delete_one({"_id": ObjectId(image_id)})
    return {"message": "Imagen eliminada correctamente"}




    
