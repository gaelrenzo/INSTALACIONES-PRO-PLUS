"""Generación de reportes Markdown para cálculos eléctricos."""

from __future__ import annotations

import os
from typing import Any, Dict


def generar_reporte_markdown(results: Dict, output_filepath: str) -> str:
    lines = [
        "# Reporte Tecnico de Calculos Electricos",
        f"**Propietario:** {results['propietario']}",
        f"**Proyecto:** {results['proyecto']}",
        "**Estado de los Calculos:** Preliminar / Sujeto a validacion",
        "",
        "## 1. Comparacion de Escenarios",
        "",
        "| Escenario | P.I. (W) | MD circuitos (W) | MD CNE (W) | MD adoptada (W) | Ib (A) | Id (A) | Alimentador | ITM | dV alim. (%) | Metodo |",
        "|---|---:|---:|---:|---:|---:|---:|---|---:|---:|",
    ]
    for scenario in results["escenarios"].values():
        res = scenario["resumen_general"]
        lines.append(
            f"| {scenario['nombre']} | {res['potencia_instalada_total_w']:.0f} | "
            f"{res['maxima_demanda_circuitos_w']:.0f} | {res['maxima_demanda_cne_w']:.0f} | "
            f"{res['maxima_demanda_adoptada_w']:.0f} | {res['corriente_empleo_ib_total_a']:.2f} | "
            f"{res['corriente_diseno_id_total_a']:.2f} | {res['alimentador_seccion_mm2']:.1f} mm2 | "
            f"{res['alimentador_itm_sugerido']} | {res['alimentador_caida_tension_porc']:.3f} | "
            f"{res['metodo_gobernante']} |"
        )

    design = results["escenario_dimensionamiento"]
    res = design["resumen_general"]
    lines.extend([
        "",
        f"## 2. Escenario de dimensionamiento preliminar: {design['nombre']}",
        "",
        f"- Potencia instalada total: {res['potencia_instalada_total_w']:.0f} W",
        f"- Maxima demanda adoptada: {res['maxima_demanda_adoptada_w']:.0f} W",
        f"- Corriente de empleo del alimentador: {res['corriente_empleo_ib_total_a']:.2f} A",
        f"- Corriente de diseno preliminar del conductor: {res['corriente_diseno_id_total_a']:.2f} A",
        f"- Alimentador sugerido: {res['alimentador_seccion_mm2']:.1f} mm2",
        f"- Interruptor general sugerido: {res['alimentador_itm_sugerido']}",
        f"- Caida de tension del alimentador: {res['alimentador_caida_tension_porc']:.3f}%",
        "",
        "## 3. Notas",
        "",
        "- Los escenarios alternativos son comparativos y deben confirmarse con el propietario.",
        "- El factor 1.25 se mantiene como criterio preliminar de dimensionamiento del conductor; REVISAR sustento normativo final.",
        "- Los circuitos de alumbrado se actualizaron a conductor minimo 2.5 mm2 conforme auditoria CNE-U 030-002.",
    ])

    os.makedirs(os.path.dirname(output_filepath) or ".", exist_ok=True)
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return output_filepath
