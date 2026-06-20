"""CLI subcomando: generación de expediente técnico completo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from electra.infraestructura.reportes.expediente import generar_expediente


REPO_ROOT = Path(__file__).resolve().parents[4]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="electra expediente",
        description="Generar expediente tecnico completo (LaTeX + PDF)",
    )
    parser.add_argument("--proyecto", required=True, help="ID del proyecto")
    parser.add_argument("--output-dir", help="Directorio de salida (default: build/<proyecto>/expediente)")
    parser.add_argument("--skip-pdf", action="store_true", help="Saltar compilacion PDF")
    return parser


def run(args: argparse.Namespace) -> int:
    build_dir = REPO_ROOT / "build" / args.proyecto
    out_dir = Path(args.output_dir) if args.output_dir else build_dir / "expediente"

    if not (build_dir / "calculos" / "resultados.json").exists():
        print(f"ERROR: No hay resultados de calculos en {build_dir / 'calculos'}")
        print("Ejecuta primero: python -m electra.aplicacion.cli calculos --proyecto " + args.proyecto)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    tex_path = str(out_dir / f"expediente_{args.proyecto}.tex")

    print(f"Generando expediente técnico para: {args.proyecto}")
    print(f"  Salida: {tex_path}")

    result = generar_expediente(
        proyecto_id=args.proyecto,
        build_dir=build_dir,
        output_path=tex_path,
        compilar_pdf=not args.skip_pdf,
    )

    print(f"\nExpediente generado: {result}")
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
