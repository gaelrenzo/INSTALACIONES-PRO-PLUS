#!/usr/bin/env python3
"""CLI wrapper — delegates to electra.infraestructura.cad.dxf_generator."""

import argparse
import json
import os
import sys

from electra.infraestructura.cad.dxf_generator import generate_dxf, generate_pdf_from_dxf


def main():
    parser = argparse.ArgumentParser(description="Generador automático de planos DXF a partir de JSON")
    parser.add_argument("--input", default="layout_example.json", help="Ruta del archivo JSON de entrada")
    parser.add_argument("--output", default="plan_distribucion.dxf", help="Ruta del archivo DXF de salida")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = args.input
    if not os.path.isabs(input_path) and not os.path.exists(input_path):
        candidates = [
            os.path.join(script_dir, args.input),
            os.path.join(script_dir, "..", "data", args.input),
        ]
        for possible_path in candidates:
            if os.path.exists(possible_path):
                input_path = possible_path
                break

    if not os.path.exists(input_path):
        print(f"Error: El archivo de entrada '{args.input}' no existe.", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    output_dir = os.path.dirname(os.path.abspath(args.output))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    result = generate_dxf(data, args.output)
    print(f"DXF generado: {result}")

    pdf = generate_pdf_from_dxf(args.output)
    if pdf:
        print(f"PDF generado: {pdf}")


if __name__ == "__main__":
    main()
