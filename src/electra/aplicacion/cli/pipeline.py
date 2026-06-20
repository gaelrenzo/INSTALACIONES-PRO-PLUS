"""CLI subcomando: pipeline completo (cálculos → CAD → BOM)."""

from __future__ import annotations

import argparse
import sys

from electra.aplicacion.orquestador import ejecutar_pipeline_desde_cli


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="electra pipeline",
        description="Pipeline completo: calculos, CAD, BOM",
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--proyecto", help="ID del proyecto (carpeta en proyectos/)")
    source.add_argument("--generar-ejemplo", action="store_true", help="Generar config de ejemplo")
    parser.add_argument("--output-dir", help="Directorio de salida")
    parser.add_argument("--skip-cad", action="store_true", help="Saltar CAD")
    parser.add_argument("--skip-bom", action="store_true", help="Saltar BOM")
    return parser


def run(args: argparse.Namespace) -> int:
    return ejecutar_pipeline_desde_cli(args)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
