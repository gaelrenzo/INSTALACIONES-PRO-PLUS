from fastapi import APIRouter, Depends

from backend.app.models.calculo import ExpedienteRequest, ExpedienteResponse
from backend.app.core.electra_bridge import ElectraBridge
from backend.app.db.supabase import get_supabase

router = APIRouter()


@router.post("/", response_model=ExpedienteResponse)
async def generar_expediente(data: ExpedienteRequest, sb=Depends(get_supabase)):
    proyecto = sb.table("proyectos").select("*").eq("id", data.proyecto_id).execute()

    bridge = ElectraBridge()
    archivos = bridge.ejecutar_expediente(proyecto.data[0], compilar_pdf=data.compilar_pdf)

    sb.table("resultados").insert({
        "proyecto_id": data.proyecto_id,
        "tipo": "expediente",
        "archivos": archivos,
    }).execute()

    sb.table("proyectos").update({"estado": "completado"}).eq("id", data.proyecto_id).execute()

    return ExpedienteResponse(proyecto_id=data.proyecto_id, archivos=archivos)
