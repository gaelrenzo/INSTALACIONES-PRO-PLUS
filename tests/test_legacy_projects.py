from __future__ import annotations

import subprocess
from pathlib import Path


def test_proyecto_aquiles_no_rompe() -> None:
    ruta = Path("proyectos", "aquiles", "proyecto.yaml")
    assert ruta.exists(), "proyecto.yaml de aquiles debe existir"


def test_proyecto_renzo_no_rompe() -> None:
    ruta = Path("proyectos", "renzo", "proyecto.yaml")
    assert ruta.exists(), "proyecto.yaml de renzo debe existir"
