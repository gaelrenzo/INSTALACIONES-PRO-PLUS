#!/usr/bin/env python3
"""Legacy wrapper — re-exports from electra.infraestructura.presupuestos.entrega_academica."""

from __future__ import annotations

import sys
from pathlib import Path

_src = Path(__file__).resolve().parent.parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from electra.infraestructura.presupuestos.entrega_academica import (
    GRUPOS_PROVEEDOR,
    TIPOS_ESTIMADOS,
    construir_filas_academicas,
    construir_recomendado,
    consolidar_filas,
    generar_entrega_final,
    slug_resultado,
)

__all__ = [
    "GRUPOS_PROVEEDOR",
    "TIPOS_ESTIMADOS",
    "construir_filas_academicas",
    "construir_recomendado",
    "consolidar_filas",
    "generar_entrega_final",
    "slug_resultado",
]
