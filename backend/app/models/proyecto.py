from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel


class ProyectoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    ubicacion: Optional[Dict[str, Any]] = None


class ProyectoResponse(BaseModel):
    id: str
    user_id: str
    nombre: str
    descripcion: Optional[str] = None
    ubicacion: Optional[Dict[str, Any]] = None
    estado: str = "borrador"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
