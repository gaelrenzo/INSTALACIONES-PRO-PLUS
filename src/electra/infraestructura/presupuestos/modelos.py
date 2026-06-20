#!/usr/bin/env python3
"""Modelos de datos del cotizador multi-proveedor."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MaterialBOM:
    id: str
    nombre_original: str
    nombre_normalizado: str
    categoria: str
    unidad: str
    cantidad: float
    descripcion_uso: str = ""
    especificaciones: Dict[str, Any] = field(default_factory=dict)
    precio_referencial: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResultadoProveedor:
    proveedor: str
    consulta: str
    proveedor_slug: str = ""
    producto: Optional[str] = None
    vendedor: Optional[str] = None
    marca: Optional[str] = None
    precio: Optional[float] = None
    moneda: str = "PEN"
    unidad_detectada: Optional[str] = None
    url: Optional[str] = None
    disponibilidad: Optional[str] = None
    fecha_consulta: str = ""
    metodo_extraccion: str = "fallback"
    confianza: float = 0.0
    observaciones: str = ""
    estado_proveedor: str = "pendiente_manual"
    url_solicitada: Optional[str] = None
    url_final: Optional[str] = None
    tipo_enlace: str = "producto"
    codigo_http: Optional[int] = None
    hubo_redirect: bool = False
    resultados_crudos: int = 0
    resultados_aceptados: int = 0
    motivo_fallo: str = ""
    score_precio: float = 0.0
    score_tecnico: float = 0.0
    score_proveedor: float = 0.0
    score_disponibilidad: float = 0.0
    score_total: float = 0.0
    
    # Campos de conversion comercial
    unidad_bom: Optional[str] = None
    cantidad_bom: Optional[float] = None
    unidad_comercial: Optional[str] = None
    contenido_comercial: Optional[float] = 1.0
    unidad_contenido: Optional[str] = None
    cantidad_comercial_a_comprar: Optional[float] = None
    precio_equivalente_unitario: Optional[float] = None
    subtotal_compra_real: Optional[float] = None
    sobrante: Optional[float] = 0.0
    confianza_conversion: float = 1.0
    observacion_conversion: str = ""
    tipo_coincidencia: str = "exacta"
    tipo_precio: str = "verificado_tienda"
    observacion_precio: str = "Precio verificado en tienda con URL."
    proveedor_origen_estimacion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResultadoProveedor":
        allowed = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in allowed})


@dataclass
class ComparativaItem:
    material_bom: MaterialBOM
    resultados_por_proveedor: List[ResultadoProveedor] = field(default_factory=list)
    resultado_recomendado: Optional[ResultadoProveedor] = None
    motivo_recomendacion: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "material_bom": self.material_bom.to_dict(),
            "resultados_por_proveedor": [r.to_dict() for r in self.resultados_por_proveedor],
            "resultado_recomendado": (
                self.resultado_recomendado.to_dict()
                if self.resultado_recomendado else None
            ),
            "motivo_recomendacion": self.motivo_recomendacion,
        }
