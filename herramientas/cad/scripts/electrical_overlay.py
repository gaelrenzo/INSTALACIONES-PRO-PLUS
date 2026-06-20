#!/usr/bin/env python3
"""CLI wrapper — delegates to electra.infraestructura.cad.electrical_overlay."""

import argparse
import json
import os
import sys

from electra.infraestructura.cad.electrical_overlay import run_overlay


def main():
    parser = argparse.ArgumentParser(description="Agrega simbologia electrica a un DXF arquitectonico existente.")
    parser.add_argument("--base", required=True, help="DXF arquitectonico base")
    parser.add_argument("--electrical", required=True, help="JSON electrico")
    parser.add_argument("--output", required=True, help="DXF de salida")
    args = parser.parse_args()

    if not os.path.exists(args.base):
        print(f"Error: no existe el DXF base: {args.base}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(args.electrical):
        print(f"Error: no existe el JSON electrico: {args.electrical}", file=sys.stderr)
        sys.exit(1)

    with open(args.electrical, "r", encoding="utf-8") as f:
        electrical_data = json.load(f)

    result = run_overlay(args.base, electrical_data, args.output)
    print(f"DXF electrico generado: {result}")


if __name__ == "__main__":
    main()
