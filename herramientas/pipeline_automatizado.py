#!/usr/bin/env python3
"""
Pipeline automatizado — wrapper legacy que delega a electra.aplicacion.orquestador.

DEPRECATED: Usa `python -m electra.aplicacion.cli pipeline --proyecto <id>` en su lugar.
Soportado hasta v2.0 para compatibilidad con scripts existentes.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

warnings.warn(
    "herramientas/pipeline_automatizado.py esta obsoleto. "
    "Usa: python -m electra.aplicacion.cli pipeline --proyecto <id>",
    DeprecationWarning,
    stacklevel=2,
)

from electra.aplicacion.orquestador import ejecutar_pipeline_desde_cli, Orquestador


REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = REPO_ROOT / "proyectos"


def _parse_args_legacy() -> tuple:
    import argparse
    parser = argparse.ArgumentParser(
        description="Pipeline automatizado de instalaciones electricas (legacy)"
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--config", help="Archivo YAML/JSON de configuracion del proyecto")
    source.add_argument("--proyecto", help="ID dentro de proyectos/")
    parser.add_argument("--generar-ejemplo", action="store_true")
    parser.add_argument("--output-dir")
    parser.add_argument("--skip-cad", action="store_true")
    parser.add_argument("--skip-bom", action="store_true")
    return parser.parse_args(), parser


def main() -> None:
    args, parser = _parse_args_legacy()

    if args.generar_ejemplo:
        from electra.aplicacion.orquestador.pipeline import _generar_config_ejemplo
        _generar_config_ejemplo(args.output_dir)
        return

    if not args.config and not args.proyecto:
        print("ERROR: Usa --proyecto <id> o --config <path>")
        sys.exit(1)

    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"ERROR: No existe: {config_path}")
            sys.exit(1)
        proyecto_id = config_path.parent.name or config_path.stem
    else:
        proyecto_id = args.proyecto
        config_path = PROJECTS_DIR / proyecto_id / "proyecto.yaml"
        if not config_path.exists():
            config_path = PROJECTS_DIR / proyecto_id / "proyecto.json"
        if not config_path.exists():
            print(f"ERROR: No existe proyecto: {proyecto_id}")
            sys.exit(1)

    orch = Orquestador.desde_proyecto(
        proyecto_id=proyecto_id,
        output_dir=Path(args.output_dir) if args.output_dir else None,
        skip_cad=args.skip_cad,
        skip_bom=args.skip_bom,
    )
    resultado = orch.ejecutar()

    print(f"\n{'=' * 60}")
    for etapa in resultado.etapas:
        status = "OK" if etapa.exitoso else "FAIL"
        print(f"  [{status}] {etapa.nombre}: {etapa.mensaje}")
        if not etapa.exitoso and etapa.error:
            print(f"         Error: {etapa.error}")

    print(f"\nResultados: {orch.config.output_dir}")
    print("=" * 60)
    sys.exit(0 if resultado.exitoso else 2)


if __name__ == "__main__":
    main()
