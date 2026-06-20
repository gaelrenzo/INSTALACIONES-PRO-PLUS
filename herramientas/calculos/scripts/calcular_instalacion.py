#!/usr/bin/env python3
"""
Calculadora de instalaciones eléctricas — DEPRECATED.

Usa `python -m electra.aplicacion.cli calculos --proyecto <id>` en su lugar.
Soportado hasta v2.0 para compatibilidad.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

warnings.warn(
    "calcular_instalacion.py esta obsoleto. Usa: python -m electra.aplicacion.cli calculos --proyecto <id>",
    DeprecationWarning, stacklevel=2,
)

import argparse
import json
import math
import os

from electra.dominio.calculos.escenarios import ejecutar_calculos as _ejecutar_calculos
from electra.dominio.calculos.escenarios import (
    ejecutar_escenario as run_scenario,
)


def run_calculations(data, amp_data=None):
    """Legacy wrapper — amp_data se ignora; la carga de ampacidades es interna."""
    return _ejecutar_calculos(data)
from electra.infraestructura.reportes import generar_tablas_latex, generar_reporte_markdown

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AMPACIDADES_PATH = Path(__file__).resolve().parent.parent / "datos" / "ampacidades.yaml"
_AMPACIDADES_CACHE = None

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def cargar_ampacidades(path=None):
    """Legacy ampacity loader — delegates to CNEPeru or fallback."""
    from electra.dominio.calculos.cne import CNEPeru

    global _AMPACIDADES_CACHE
    if _AMPACIDADES_CACHE is not None:
        return _AMPACIDADES_CACHE

    ruta = Path(path) if path else DEFAULT_AMPACIDADES_PATH
    if ruta.exists() and HAS_YAML:
        with open(ruta, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    else:
        data = _ampacidades_fallback()

    _AMPACIDADES_CACHE = data
    return data


def _ampacidades_fallback():
    return {
        "cobre": {
            "conductividad_rho_mohm": 0.0175,
            "ducto": {1.5: 15, 2.5: 20, 4.0: 28, 6.0: 36, 10.0: 50, 16.0: 66, 25.0: 88},
        },
        "aluminio": {
            "conductividad_rho_mohm": 0.0282,
            "ducto": {2.5: 16, 4.0: 22, 6.0: 28, 10.0: 40, 16.0: 55, 25.0: 72},
        },
        "itm_estandar_a": [10, 16, 20, 25, 32, 40, 50, 63, 80, 100],
    }


def get_ampacity(section, material="cobre", modo="ducto", amp_data=None):
    data = amp_data or cargar_ampacidades()
    return data.get(material, {}).get(modo, {}).get(float(section), 0)


def find_appropriate_itm(ib, max_capacity, amp_data=None):
    data = amp_data or cargar_ampacidades()
    itm_list = data.get("itm_estandar_a", [10, 16, 20, 25, 32, 40, 50, 63, 80, 100])
    for rating in itm_list:
        if rating >= ib and rating <= max_capacity:
            return rating
    for rating in itm_list:
        if rating >= ib:
            return rating
    return itm_list[-1] if itm_list else 100


def select_conductor_for_design(id_current, minimum_section=2.5, material="cobre", modo="ducto", amp_data=None):
    data = amp_data or cargar_ampacidades()
    tabla = data.get(material, {}).get(modo, {})
    for section, ampacity in sorted(tabla.items()):
        if section >= minimum_section and ampacity >= id_current:
            return section, ampacity
    if tabla:
        section = max(tabla)
        return section, tabla[section]
    return minimum_section, 0


def load_data(filepath: str) -> dict:
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def parse_args():
    parser = argparse.ArgumentParser(description="Calculos electricos (legacy)")
    parser.add_argument("--input", required=True, help="JSON de entrada")
    parser.add_argument("--output-dir", required=True, help="Directorio de salida")
    parser.add_argument("--ampacidades", default=None, help="YAML de ampacidades (ignorado)")
    return parser.parse_args()


def main():
    args = parse_args()
    data = load_data(args.input)
    os.makedirs(args.output_dir, exist_ok=True)

    results = run_calculations(data)

    with open(os.path.join(args.output_dir, "resultados.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    generar_tablas_latex(results, args.output_dir)
    generar_reporte_markdown(results, os.path.join(args.output_dir, "reporte_calculos.md"))

    print(f"\nResultados exportados a: {args.output_dir}")


if __name__ == "__main__":
    main()
