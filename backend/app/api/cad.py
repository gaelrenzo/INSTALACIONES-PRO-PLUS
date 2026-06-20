from fastapi import APIRouter, Depends

from backend.app.models.calculo import CadRequest, CadResponse
from backend.app.core.electra_bridge import ElectraBridge
from backend.app.db.supabase import get_supabase

router = APIRouter()


@router.post("/dxf", response_model=CadResponse)
async def generar_dxf(data: CadRequest, sb=Depends(get_supabase)):
    proyecto = sb.table("proyectos").select("*").eq("id", data.proyecto_id).execute()
    pisos = sb.table("pisos").select("*").eq("proyecto_id", data.proyecto_id).execute()

    bridge = ElectraBridge()
    archivos = bridge.ejecutar_cad(proyecto.data[0], pisos.data, data.formato)

    sb.table("resultados").insert({
        "proyecto_id": data.proyecto_id,
        "tipo": "cad",
        "archivos": archivos,
    }).execute()

    return CadResponse(proyecto_id=data.proyecto_id, archivos=archivos)
