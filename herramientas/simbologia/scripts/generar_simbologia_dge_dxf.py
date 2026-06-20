#!/usr/bin/env python3
"""CLI wrapper — delegates a electra.infraestructura.cad.simbologia."""

from __future__ import annotations

import sys
from pathlib import Path

from electra.infraestructura.cad.simbologia import generate_symbology_catalog, generate_symbology_pdf


def main():
    BASE_DIR = Path(__file__).resolve().parent.parent
    JSON_PATH = BASE_DIR / "simbologia_normativa_dge.json"
    OUTPUT_DXF = BASE_DIR / "salidas" / "simbologia_dge_completa.dxf"
    OUTPUT_SVG = BASE_DIR / "salidas" / "svg"

    if not JSON_PATH.exists():
        print(f"Error: No existe el JSON de simbologia en: {JSON_PATH}")
        sys.exit(1)

    result = generate_symbology_catalog(str(JSON_PATH), str(OUTPUT_DXF), str(OUTPUT_SVG))
    print(f"Catalogo DXF generado: {result}")

    pdf_path = OUTPUT_DXF.with_suffix(".pdf")
    try:
        generate_symbology_pdf(str(OUTPUT_DXF), str(pdf_path))
        print(f"PDF generado: {pdf_path}")
    except Exception as e:
        print(f"No se pudo generar PDF: {e}")


if __name__ == "__main__":
    main()
