#!/usr/bin/env python3
"""Legacy wrapper — re-exports from electra.infraestructura.presupuestos.modelos."""

from __future__ import annotations

import sys
from pathlib import Path

_src = Path(__file__).resolve().parent.parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from electra.infraestructura.presupuestos.modelos import (
    ComparativaItem,
    MaterialBOM,
    ResultadoProveedor,
)

__all__ = ["MaterialBOM", "ResultadoProveedor", "ComparativaItem"]
