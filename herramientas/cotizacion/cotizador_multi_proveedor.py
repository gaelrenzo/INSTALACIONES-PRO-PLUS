#!/usr/bin/env python3
"""Legacy wrapper — delegates to electra.infraestructura.presupuestos.cotizador_multi_proveedor."""

from __future__ import annotations

import sys
from pathlib import Path

_src = Path(__file__).resolve().parent.parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from electra.infraestructura.presupuestos.cotizador_multi_proveedor import main

if __name__ == "__main__":
    sys.exit(main())
