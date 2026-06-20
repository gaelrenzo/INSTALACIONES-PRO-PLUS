from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class CalcularRequest(BaseModel):
    proyecto_id: str
    escenarios: Optional[List[Dict[str, Any]]] = None


class CalcularResponse(BaseModel):
    proyecto_id: str
    resumen: Dict[str, Any]
    escenarios: List[Dict[str, Any]]
    warnings: List[str] = []


class CadRequest(BaseModel):
    proyecto_id: str
    formato: str = "dxf"


class CadResponse(BaseModel):
    proyecto_id: str
    archivos: Dict[str, str]


class CotizarRequest(BaseModel):
    proyecto_id: str
    proveedores: Optional[List[str]] = None


class CotizarResponse(BaseModel):
    proyecto_id: str
    resumen: Dict[str, Any]
    cotizaciones: List[Dict[str, Any]]


class ExpedienteRequest(BaseModel):
    proyecto_id: str
    compilar_pdf: bool = True


class ExpedienteResponse(BaseModel):
    proyecto_id: str
    archivos: Dict[str, str]
