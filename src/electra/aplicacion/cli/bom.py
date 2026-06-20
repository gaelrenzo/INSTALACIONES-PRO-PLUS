"""CLI subcomando: generación de BOM con precios."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from electra.infraestructura.presupuestos.bom_precios import generar_bom


REPO_ROOT = Path(__file__).resolve().parents[4]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="electra bom",
        description="Generar lista de materiales y presupuesto",
    )
    parser.add_argument("--resultados", required=True, help="Ruta al JSON de resultados de calculo")
    parser.add_argument("--output", default="output/bom", help="Base del archivo de salida (sin extension)")
    return parser


def run(args: argparse.Namespace) -> int:
    resultados_path = args.resultados
    if not Path(resultados_path).exists():
        print(f"ERROR: No existe {resultados_path}")
        return 1

    bom = generar_bom(resultados_path, args.output)
    print(f"\nResumen de costos:")
    print(f"  Materiales:  S/ {bom['resumen']['costo_materiales_soles']:.2f}")
    print(f"  Mano de obra: S/ {bom['resumen']['mano_obra_40porc_soles']:.2f}")
    print(f"  TOTAL:       S/ {bom['resumen']['costo_total_soles']:.2f}")
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
