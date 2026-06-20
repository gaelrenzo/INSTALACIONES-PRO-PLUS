from fastapi import APIRouter, Depends

from backend.app.models.calculo import CalcularRequest, CalcularResponse
from backend.app.core.electra_bridge import ElectraBridge
from backend.app.db.supabase import get_supabase

router = APIRouter()


@router.post("/", response_model=CalcularResponse)
async def calcular(data: CalcularRequest, sb=Depends(get_supabase)):
    proyecto = sb.table("proyectos").select("*").eq("id", data.proyecto_id).execute()
    pisos = sb.table("pisos").select("*").eq("proyecto_id", data.proyecto_id).execute()

    bridge = ElectraBridge()
    resultado = bridge.ejecutar_calculos(proyecto.data[0], pisos.data)

    sb.table("resultados").insert({
        "proyecto_id": data.proyecto_id,
        "tipo": "calculo",
        "resumen": resultado["resumen"],
    }).execute()

    sb.table("proyectos").update({"estado": "calculado"}).eq("id", data.proyecto_id).execute()

    return CalcularResponse(
        proyecto_id=data.proyecto_id,
        resumen=resultado["resumen"],
        escenarios=resultado["escenarios"],
        warnings=resultado.get("warnings", []),
    )
