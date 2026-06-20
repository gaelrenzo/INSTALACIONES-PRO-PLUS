#!/usr/bin/env python3
"""
Generador de BOM — DEPRECATED.

Usa `python -m electra.aplicacion.cli bom --resultados <path> --output <base>` en su lugar.
Soportado hasta v2.0 para compatibilidad.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

warnings.warn(
    "generar_bom.py esta obsoleto. Usa: python -m electra.aplicacion.cli bom",
    DeprecationWarning, stacklevel=2,
)

import argparse
import os

from electra.infraestructura.presupuestos.bom_precios import generar_bom


def parse_args():
    parser = argparse.ArgumentParser(description="Genera BOM (legacy)")
    parser.add_argument("--resultados", required=True, help="JSON de resultados")
    parser.add_argument("--output", default="output/bom", help="Base del archivo de salida")
    return parser.parse_args()


def main():
    args = parse_args()
    if not os.path.exists(args.resultados):
        print(f"Error: No existe {args.resultados}")
        sys.exit(1)
    generar_bom(args.resultados, args.output)


if __name__ == "__main__":
    main()
