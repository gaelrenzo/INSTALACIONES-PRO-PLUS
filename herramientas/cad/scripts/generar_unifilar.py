#!/usr/bin/env python3
"""CLI wrapper — delegates to electra.infraestructura.cad.unifilar."""

import argparse
import json
import os
import sys

from electra.infraestructura.cad.unifilar import exportar_unifilar_pdf, generar_unifilar


def main():
    parser = argparse.ArgumentParser(
        description="Genera diagrama unifilar en DXF desde resultados de calculo"
    )
    parser.add_argument("--resultados", required=True, help="JSON de resultados del motor de calculos")
    parser.add_argument("--output", required=True, help="DXF o PDF de salida")
    args = parser.parse_args()

    if not os.path.exists(args.resultados):
        print(f"Error: No existe {args.resultados}")
        sys.exit(1)

    with open(args.resultados, "r", encoding="utf-8") as f:
        resultados = json.load(f)

    output_path = args.output
    if output_path.endswith(".pdf"):
        dxf_path = output_path.replace(".pdf", ".dxf")
        generar_unifilar(resultados, dxf_path)
        exportar_unifilar_pdf(dxf_path)
    else:
        generar_unifilar(resultados, output_path)
        exportar_unifilar_pdf(output_path)


if __name__ == "__main__":
    main()
