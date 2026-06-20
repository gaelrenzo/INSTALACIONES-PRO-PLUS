from fastapi import APIRouter

from backend.app.api.proyectos import router as proyectos_router
from backend.app.api.calculos import router as calculos_router
from backend.app.api.cad import router as cad_router
from backend.app.api.cotizar import router as cotizar_router
from backend.app.api.expediente import router as expediente_router

api_router = APIRouter()

api_router.include_router(proyectos_router, prefix="/proyectos", tags=["Proyectos"])
api_router.include_router(calculos_router, prefix="/calcular", tags=["Cálculos"])
api_router.include_router(cad_router, prefix="/generar", tags=["CAD"])
api_router.include_router(cotizar_router, prefix="/cotizar", tags=["Cotización"])
api_router.include_router(expediente_router, prefix="/expediente", tags=["Expediente"])
