from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Body, HTTPException, Query
from utils.utils import generate_wallet_key, generate_read_only_key
from database import album_collection
from models.image_model import Album



router = APIRouter()

@router.post('/create/')
async def create_album(album: Album):
    master_key = generate_wallet_key()
    album_data={
        **album.dict(),
        "created_at" : datetime.now(),
        "album_name" : album.album_name,
        "master_key" : master_key,
        "read_only_keys" : [],
    }
    
    result = album_collection.insert_one(album_data)
    album_id = str(result.inserted_id)

    return {
        "message": "Albúm Creado", 
        "album":{

            "_id": album_id,
            "master_key": master_key,
            "album_name" : album.album_name,
            
        }
    }
@router.post('/change_name/')
async def change_name (album_id: str=Body(...), album_name: str = Body (...), master_key: str = Body(...)):
    album =album_collection.find_one({"_id": ObjectId(album_id)})
    if not album:
        raise HTTPException(status_code = 404, detail= "album not found")
    
    if album["master_key"] != master_key:
        raise HTTPException(status_code=403, detail= "Wrong master key")
    album_collection.update_one (

        {"_id": ObjectId(album_id)},
        {"$set":{"album_name": album_name }}
    )
    return {"message": "Album name changed to: ", "album_name": album_name}

@router.post('/add_read_key/')
async def add_read_only_key (album_id: str = Body(...), master_key: str = Body(...)):
    album = album_collection.find_one({"_id": ObjectId(album_id)})

    if not album:
        raise HTTPException(status_code = 404, detail= "album not found")
    
    if album["master_key"] != master_key:
        raise HTTPException(status_code=403, detail= "Wrong master key")
    
    new_key= generate_read_only_key
    album_collection.update_one(
        {"_id": ObjectId(album_id)},
        {"$push": {"read_only_keys": new_key}}
    )
    return{"message": "read only key generated", "read_only_key": new_key}

@router.post('/revoke_read_key/')
async def revoke_read_only_key (album_id: str = Body(...), master_key: str = Body(...), key_to_remove: str = Body (...)):
    album = album_collection.find_one({"_id": ObjectId(album_id)})

    if not album:
        raise HTTPException(status_code = 404, detail= "album not found")
    
    if album["master_key"] != master_key:
        raise HTTPException(status_code=403, detail= "Wrong master key")
    
    album_collection.update_one(
        {"_id": ObjectId(album_id)},
        {"$pull": {"read_only_keys": key_to_remove}}
    )
    return{"message": "read only key revoked", "read_only_key": key_to_remove}

@router.delete('/delete/')
async def delete_album (album_id:str):
    album = album_collection.find_one({"_id": ObjectId(album_id)})

    if not album:
        raise HTTPException(status_code=404, detail="Albúm no encontrado")
    
  
    album_collection.delete_one({"_id" : ObjectId(album_id)})

    return{"message": "Albúm eliminado correctamente"}

@router.get('/get/')
async def get_albums():
    albums = list(album_collection.find())  # Encuentra todos los álbumes

    if not albums:
        raise HTTPException(status_code=404, detail="No existen álbumes")
    
    for album in albums:
        album["_id"] = str(album["_id"])  # Convierte _id a string
    
    return {"albums": albums}  # Devuelve la lista de álbumes

@router.get("/verify_key")
async def verify_key(key: str = Query(...)):
    album = album_collection.find_one({
        "$or": [
            {"master_key": key},
            {"read_only_key": key}
        ]
    })

    if not album:
        raise HTTPException(status_code=404, detail="Clave inválida")

    access_type = "master" if album["master_key"] == key else "readonly"

    return {
        "access_type": access_type,
        "album_id": str(album["_id"]),
        "album_name": album["album_name"]
    }


