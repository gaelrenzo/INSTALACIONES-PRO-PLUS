#!/usr/bin/env python3
"""Construye los resultados regenerables del proyecto Renzo."""

import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
REPO_DIR = PROJECT_DIR.parent.parent
EXPEDIENTE_DIR = PROJECT_DIR / "expediente"
BUILD_DIR = REPO_DIR / "build" / "renzo"
LATEX_BUILD_DIR = BUILD_DIR / "expediente"


def run_script(script_name, *args):
    script_path = SCRIPT_DIR / script_name
    print(f"\n====== Ejecutando: {script_name} ======")
    result = subprocess.run(
        [sys.executable, str(script_path), *args],
        cwd=str(PROJECT_DIR),
    )
    if result.returncode != 0:
        raise SystemExit(f"[ERROR] El script {script_name} falló.")
    print(f"[OK] {script_name} completado.")


def compile_latex():
    print("\n====== Compilando expediente/main.tex ======")
    LATEX_BUILD_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        "pdflatex",
        "-interaction=nonstopmode",
        f"-output-directory={LATEX_BUILD_DIR}",
        "main.tex",
    ]

    for pass_number in (1, 2):
        print(f"-> Pasada {pass_number} de LaTeX")
        result = subprocess.run(command, cwd=str(EXPEDIENTE_DIR))
        if result.returncode != 0:
            raise SystemExit(f"[ERROR] Falló la pasada {pass_number} de LaTeX.")

    pdf_path = LATEX_BUILD_DIR / "main.pdf"
    if not pdf_path.exists():
        raise SystemExit("[ERROR] No se encontró el PDF final.")
    print(f"[OK] Expediente generado en: {pdf_path}")


def main():
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    run_script("generar_arquitectura.py")
    run_script("generar_planos_desde_modelo.py")
    run_script("generar_planos_y_diagramas.py", "--solo-diagramas")
    run_script("actualizar_metrados_latex.py")
    compile_latex()
    print(f"\nResultados regenerables: {BUILD_DIR}")


if __name__ == "__main__":
    main()
