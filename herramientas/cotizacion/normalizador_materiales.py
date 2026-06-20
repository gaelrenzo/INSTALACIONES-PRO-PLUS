#!/usr/bin/env python3
"""Legacy wrapper — re-exports from electra.infraestructura.presupuestos.normalizador_materiales."""

from __future__ import annotations

import sys
from pathlib import Path

_src = Path(__file__).resolve().parent.parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from electra.infraestructura.presupuestos.normalizador_materiales import (
    cargar_equivalencias,
    comparar_specs,
    detectar_categoria,
    extraer_especificaciones,
    fmt_num,
    limpiar_texto,
    normalizar_nombre_material,
    quitar_sufijos_circuito,
    score_tecnico,
    similitud_texto,
    tokenizar,
)

__all__ = [
    "cargar_equivalencias",
    "comparar_specs",
    "detectar_categoria",
    "extraer_especificaciones",
    "fmt_num",
    "limpiar_texto",
    "normalizar_nombre_material",
    "quitar_sufijos_circuito",
    "score_tecnico",
    "similitud_texto",
    "tokenizar",
]
