"""CLI subcomando: cotización multi-proveedor y documento formal."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from electra.aplicacion.orquestador import Orquestador


REPO_ROOT = Path(__file__).resolve().parents[4]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="electra cotizar",
        description="Cotizacion multi-proveedor y documento formal",
    )
    parser.add_argument("--proyecto", required=True, help="ID del proyecto")
    parser.add_argument("--output-dir", help="Directorio de salida")
    parser.add_argument("--proveedores", nargs="*",
                        default=["promart", "sodimac", "maestro", "mercadolibre"],
                        help="Proveedores a consultar")
    return parser


def run(args: argparse.Namespace) -> int:
    orch = Orquestador.desde_proyecto(
        args.proyecto,
        output_dir=Path(args.output_dir) if args.output_dir else None,
        skip_cad=True,
        skip_bom=False,
    )
    resultado = orch.ejecutar()

    from electra.aplicacion.orquestador.casos_uso import generar_cotizacion

    calc_json = orch._calculo_json
    etapa_cot = generar_cotizacion.ejecutar(
        args.proyecto,
        orch.config.datos_config,
        calc_json,
        orch.config.output_dir,
        proveedores=args.proveedores,
    )
    resultado.agregar(etapa_cot)

    for etapa in resultado.etapas:
        status = "OK" if etapa.exitoso else "FAIL"
        print(f"  [{status}] {etapa.nombre}: {etapa.mensaje}")
        if not etapa.exitoso and etapa.error:
            print(f"         Error: {etapa.error}")

    return 0 if resultado.exitoso else 1


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
