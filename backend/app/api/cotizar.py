from fastapi import APIRouter, Depends

from backend.app.models.calculo import CotizarRequest, CotizarResponse
from backend.app.core.electra_bridge import ElectraBridge
from backend.app.db.supabase import get_supabase

router = APIRouter()


@router.post("/", response_model=CotizarResponse)
async def cotizar(data: CotizarRequest, sb=Depends(get_supabase)):
    proyecto = sb.table("proyectos").select("*").eq("id", data.proyecto_id).execute()

    bridge = ElectraBridge()
    resultado = bridge.ejecutar_cotizacion(proyecto.data[0], data.proveedores)

    sb.table("resultados").insert({
        "proyecto_id": data.proyecto_id,
        "tipo": "cotizacion",
        "resumen": resultado["resumen"],
    }).execute()

    return CotizarResponse(
        proyecto_id=data.proyecto_id,
        resumen=resultado["resumen"],
        cotizaciones=resultado["cotizaciones"],
    )
