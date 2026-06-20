#!/usr/bin/env python3
"""Genera los tres planos arquitectonicos canónicos en build/renzo."""

import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = PROJECT_DIR.parent.parent
LAYOUTS_DIR = PROJECT_DIR / "arquitectura" / "datos"
OUTPUT_DIR = REPO_DIR / "build" / "renzo" / "arquitectura"
GENERATOR_SCRIPT = REPO_DIR / "herramientas" / "cad" / "scripts" / "dxf_generator.py"

LAYOUTS = ("piso-1", "piso-2", "piso-3")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    failures = []

    for layout in LAYOUTS:
        json_path = LAYOUTS_DIR / f"{layout}.json"
        dxf_path = OUTPUT_DIR / f"{layout}.dxf"
        print(f"Compilando: {json_path} -> {dxf_path}")

        result = subprocess.run(
            [
                sys.executable,
                str(GENERATOR_SCRIPT),
                "--input",
                str(json_path),
                "--output",
                str(dxf_path),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"[OK] {layout}")
        else:
            print(result.stderr or result.stdout)
            failures.append(layout)

    if failures:
        print(f"Fallaron {len(failures)} layouts: {', '.join(failures)}")
        return 1

    print("Arquitectura canónica generada correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
