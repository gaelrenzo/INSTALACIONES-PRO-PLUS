from typing import List
from fastapi import APIRouter, Depends, HTTPException

from backend.app.models.proyecto import ProyectoCreate, ProyectoResponse
from backend.app.db.supabase import get_supabase

router = APIRouter()


@router.get("/", response_model=List[ProyectoResponse])
async def listar_proyectos(sb=Depends(get_supabase)):
    resp = sb.table("proyectos").select("*").execute()
    return resp.data


@router.post("/", response_model=ProyectoResponse, status_code=201)
async def crear_proyecto(data: ProyectoCreate, sb=Depends(get_supabase)):
    resp = sb.table("proyectos").insert(data.model_dump()).execute()
    return resp.data[0]


@router.get("/{proyecto_id}", response_model=ProyectoResponse)
async def obtener_proyecto(proyecto_id: str, sb=Depends(get_supabase)):
    resp = sb.table("proyectos").select("*").eq("id", proyecto_id).execute()
    if not resp.data:
        raise HTTPException(404, "Proyecto no encontrado")
    return resp.data[0]


@router.delete("/{proyecto_id}", status_code=204)
async def eliminar_proyecto(proyecto_id: str, sb=Depends(get_supabase)):
    sb.table("proyectos").delete().eq("id", proyecto_id).execute()
