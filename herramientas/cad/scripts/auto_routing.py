#!/usr/bin/env python3
"""CLI wrapper — delegates to electra.infraestructura.cad.auto_routing."""

import argparse
import json
import os
import sys

from electra.infraestructura.cad.auto_routing import auto_route_electrical


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description="Genera rutas ortogonales de canalizacion electrica con A* evitando obstaculos"
    )
    parser.add_argument("--electrical", required=True, help="JSON electrico de entrada")
    parser.add_argument("--layout", default=None, help="JSON de layout arquitectonico (opcional)")
    parser.add_argument("--output", required=True, help="JSON electrico de salida con rutas")
    parser.add_argument("--clearance", type=float, default=0.3, help="Distancia de separacion de muros (m)")
    parser.add_argument("--grid-res", type=float, default=0.1, help="Resolucion de la grilla A* (m)")
    args = parser.parse_args()

    if not os.path.exists(args.electrical):
        print(f"Error: No existe {args.electrical}")
        sys.exit(1)

    electrical_data = load_json(args.electrical)
    layout_data = None
    if args.layout:
        if os.path.exists(args.layout):
            layout_data = load_json(args.layout)
            print(f"Layout cargado: {args.layout}")
        else:
            print(f"Advertencia: No existe layout {args.layout}")

    result = auto_route_electrical(electrical_data, layout_data, args.clearance, args.grid_res)
    save_json(result, args.output)

    n_rutas = len(result.get("rutas", []))
    total_length = sum(r.get("total_length_m", 0) for r in result.get("rutas", []))
    print(f"Rutas generadas: {n_rutas}")
    print(f"Longitud total: {total_length:.2f} m")
    print(f"Salida: {args.output}")


if __name__ == "__main__":
    main()
