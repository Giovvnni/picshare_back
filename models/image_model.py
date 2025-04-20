from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Album(BaseModel):
    album_name: str
    created_at: Optional[datetime] = None
    master_key: Optional[str] = None  # Clave maestra tipo wallet
    read_only_keys: Optional[List[str]] = []  # Lista de claves de solo lectura


class Image(BaseModel):
    id: Optional[str] = None
    album_id : str
    filename : str
    uploaded_at : datetime
    encrypted : bool

