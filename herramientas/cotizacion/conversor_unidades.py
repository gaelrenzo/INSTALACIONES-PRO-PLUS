#!/usr/bin/env python3
"""Legacy wrapper — re-exports from electra.infraestructura.presupuestos.conversor_unidades."""

from __future__ import annotations

import sys
from pathlib import Path

_src = Path(__file__).resolve().parent.parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from electra.infraestructura.presupuestos.conversor_unidades import (
    calcular_compra_comercial,
    calcular_precio_equivalente,
    calcular_sobrante,
    cargar_reglas_unidades,
    detectar_unidad_comercial,
    extraer_contenido_comercial,
    marcar_confianza_conversion,
    normalizar_unidad,
)

__all__ = [
    "calcular_compra_comercial",
    "calcular_precio_equivalente",
    "calcular_sobrante",
    "cargar_reglas_unidades",
    "detectar_unidad_comercial",
    "extraer_contenido_comercial",
    "marcar_confianza_conversion",
    "normalizar_unidad",
]
