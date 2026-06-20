"""CLI subcomando: ejecutar cálculos eléctricos multi-escenario."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from electra.dominio.calculos.escenarios import ejecutar_calculos
from electra.infraestructura.reportes import generar_tablas_latex, generar_reporte_markdown


REPO_ROOT = Path(__file__).resolve().parents[4]
PROJECTS_DIR = REPO_ROOT / "proyectos"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="electra calculos",
        description="Ejecutar calculos electricos multi-escenario",
    )
    parser.add_argument("--proyecto", required=True, help="ID del proyecto")
    parser.add_argument("--output-dir", help="Directorio de salida (default: build/<proyecto>/calculos)")
    return parser


def run(args: argparse.Namespace) -> int:
    proyecto_id = args.proyecto
    config_path = PROJECTS_DIR / proyecto_id / "proyecto.yaml"
    if not config_path.exists():
        config_path = PROJECTS_DIR / proyecto_id / "proyecto.json"

    if not config_path.exists():
        print(f"ERROR: No existe proyecto: {proyecto_id}")
        return 1

    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f) if config_path.suffix in (".yaml", ".yml") else json.load(f)

    pisos = config.get("pisos", [])
    circuitos_data = []
    for piso in pisos:
        for c in piso.get("circuitos", []):
            circuitos_data.append({
                "id": c.get("id", f"C{len(circuitos_data)+1}"),
                "descripcion": f"{c['uso']} - {piso['nombre']}",
                "potencia_instalada_w": c["potencia_w"],
                "factor_demanda": c.get("factor_demanda", 1.0),
                "longitud_m": c.get("longitud_m", 15.0),
                "seccion_conductor_mm2": c.get("seccion_mm2", 2.5),
                "diametro_tubo_mm": c.get("tubo_mm", 20),
                "estado": "definitivo",
                "fuente": "configuracion del proyecto",
            })

    escenarios = config.get("escenarios", [{
        "id": "escenario_base", "nombre": "Escenario base", "estado": "definitivo",
        "cocina_electrica": False, "circuito_overrides": {},
        "cne_050_200": {"aplicar": True, "cocina_electrica_normativa_w": 0},
    }])

    data = {
        "proyecto": config.get("proyecto", proyecto_id),
        "propietario": config.get("propietario", ""),
        "ubicacion": {
            "distrito": config.get("distrito", ""),
            "provincia": config.get("provincia", ""),
            "departamento": config.get("departamento", ""),
        },
        "areas": {
            "terreno_m2": {"valor": config.get("area_terreno_m2"), "estado": "definitivo", "fuente": "config"},
            "techada_primer_piso_m2": {"valor": config.get("area_techada_m2", {}).get("piso_1"), "estado": "definitivo", "fuente": "config"},
            "techada_segundo_piso_m2": {"valor": config.get("area_techada_m2", {}).get("piso_2"), "estado": "definitivo", "fuente": "config"},
            "techada_total_calculo_m2": {"valor": config.get("area_techada_total_m2"), "estado": "definitivo", "fuente": "config"},
        },
        "parametros_electricos": {
            "tension_v": config.get("tension_v", 220),
            "fases": config.get("fases", 1),
            "factor_potencia_cosphi": config.get("factor_potencia", 0.90),
            "factor_diseno_conductor": config.get("factor_diseno", 1.25),
            "resistividad_rho_mohm": config.get("resistividad_rho", 0.0175),
            "caida_tension_max_alimentador_porc": config.get("caida_alimentador_porc", 1.5),
            "caida_tension_max_derivados_porc": config.get("caida_derivados_porc", 2.5),
            "material_conductor": "cobre",
            "modo_instalacion": "ducto",
        },
        "alimentacion_principal": {
            "origen": "Medidor Concesionaria",
            "destino": "Tablero General (TG)",
            "longitud_m": config.get("longitud_alimentador_m", 10.0),
        },
        "escenario_dimensionamiento_id": escenarios[0]["id"],
        "circuitos_base": circuitos_data,
        "escenarios": escenarios,
    }

    out_dir = Path(args.output_dir or REPO_ROOT / "build" / proyecto_id / "calculos")
    out_dir.mkdir(parents=True, exist_ok=True)

    results = ejecutar_calculos(data)

    resultados_json = out_dir / "resultados.json"
    with open(resultados_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    generar_tablas_latex(results, str(out_dir))
    generar_reporte_markdown(results, str(out_dir / "reporte_calculos.md"))

    print(f"\n--- RESUMEN ---")
    for scenario in results["escenarios"].values():
        res = scenario["resumen_general"]
        print(
            f"{scenario['id']}: PI={res['potencia_instalada_total_w']:.0f} W, "
            f"MD_circ={res['maxima_demanda_circuitos_w']:.0f} W, "
            f"MD_CNE={res['maxima_demanda_cne_w']:.0f} W, "
            f"MD_adoptada={res['maxima_demanda_adoptada_w']:.0f} W, "
            f"Ib={res['corriente_empleo_ib_total_a']:.2f} A, "
            f"Cond={res['alimentador_seccion_mm2']:.1f} mm2, "
            f"ITM={res['alimentador_itm_sugerido']}, "
            f"dV={res['alimentador_caida_tension_porc']:.3f}%"
        )

    print(f"\nResultados: {resultados_json}")
    print(f"Tablas LaTeX: {out_dir}")
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
