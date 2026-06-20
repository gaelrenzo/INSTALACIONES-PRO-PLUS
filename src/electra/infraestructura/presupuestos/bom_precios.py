"""Generación de BOM con precios referenciales y presupuesto."""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional


PRECIOS_REF: Dict[str, float] = {
    "cable_1.5": 0.85, "cable_2.5": 1.20, "cable_4.0": 1.80, "cable_6.0": 2.50,
    "cable_10.0": 4.00, "cable_16.0": 6.00, "cable_25.0": 9.00,
    "cable_tierra_10": 3.50,
    "tubo_20": 1.50, "tubo_25": 2.00, "tubo_32": 3.00, "tubo_40": 4.00,
    "itm_2p_10": 12.00, "itm_2p_16": 14.00, "itm_2p_20": 15.00, "itm_2p_25": 18.00,
    "itm_2p_32": 22.00, "itm_2p_40": 28.00, "itm_2p_50": 35.00, "itm_2p_63": 45.00,
    "diferencial_2p_25_30ma": 45.00, "diferencial_2p_40_30ma": 55.00, "diferencial_2p_63_30ma": 70.00,
    "tablero_4": 35.00, "tablero_6": 45.00, "tablero_8": 55.00, "tablero_12": 75.00,
    "varilla_tierra": 25.00, "luminaria_led": 15.00,
    "interruptor_simple": 8.00, "interruptor_conmutado": 12.00,
    "tomacorriente_doble": 10.00, "tomacorriente_tierra": 12.00,
    "caja_rectangular": 2.50, "caja_octogonal": 3.00,
    "cinta_aislar": 5.00, "breaker_simple": 8.00,
}


def _get_precio(key: str, default: float = 0) -> float:
    return PRECIOS_REF.get(key, default)


def _itm_precio_key(amperaje: int) -> str:
    for k in [63, 50, 40, 32, 25, 20, 16, 10]:
        if amperaje <= k:
            return f"itm_2p_{k}"
    return "itm_2p_63"


def _tubo_precio_key(diametro_mm: int) -> str:
    for k in [40, 32, 25, 20]:
        if diametro_mm >= k:
            return f"tubo_{k}"
    return "tubo_20"


def _cable_precio_key(seccion: float) -> str:
    for k in [25.0, 16.0, 10.0, 6.0, 4.0, 2.5, 1.5]:
        if seccion >= k - 0.01:
            return f"cable_{k}"
    return "cable_2.5"


def _tex_escape(value: Any) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def _fmt_num(value: Optional[float], digits: int = 2) -> str:
    if value is None:
        return "0"
    return f"{value:,.{digits}f}"


def generar_bom(resultados_path: str, output_base: str) -> Dict[str, Any]:
    with open(resultados_path, encoding="utf-8") as f:
        resultados = json.load(f)

    design = resultados["escenario_dimensionamiento"]
    resumen = design["resumen_general"]
    circuitos = design["circuitos_calculados"]

    materiales: List[Dict[str, Any]] = []
    total_costo = 0.0

    def agregar(item: str, unidad: str, cantidad: float, precio_unit: float, uso: str) -> None:
        nonlocal total_costo
        costo = cantidad * precio_unit
        total_costo += costo
        materiales.append({
            "item": item, "unidad": unidad, "cantidad": cantidad,
            "precio_unit_soles": round(precio_unit, 2),
            "costo_soles": round(costo, 2), "uso": uso,
        })

    long_alim = resumen.get("alimentador_longitud_m", 10)
    seccion_alim = resumen.get("alimentador_seccion_mm2", 10.0)
    cable_m = round(long_alim * 3 * 1.1)
    agregar(
        f"Cable TW THW {seccion_alim:.1f} mm2 (alimentador trifasico)".replace(".0", ""),
        "m", cable_m, _get_precio(_cable_precio_key(seccion_alim)),
        "Alimentador principal desde medidor a TG",
    )

    tubo_m = round(long_alim * 1.1)
    diam_tubo = max(20, int(seccion_alim * 2.5))
    agregar(f"Tubo PVC SAP {diam_tubo} mm (alimentador)", "m", tubo_m,
            _get_precio(_tubo_precio_key(diam_tubo)), "Alimentador principal")

    itm_alim = resumen["alimentador_itm_a"]
    agregar(f"ITM {resumen['alimentador_itm_sugerido']}", "und", 1,
            _get_precio(_itm_precio_key(itm_alim)), "Proteccion general del alimentador")

    n_circuitos = len(circuitos)
    for n in [4, 6, 8, 12]:
        if n_circuitos <= n:
            agregar(f"Tablero general para {n} circuitos", "und", 1,
                    _get_precio(f"tablero_{n}"), "Distribucion de circuitos")
            break

    agregar("Interruptor diferencial 2P-40A-30mA", "und", 1,
            _get_precio("diferencial_2p_40_30ma"), "Proteccion diferencial general")

    for c in circuitos:
        seccion = c["seccion_conductor_mm2"]
        length = c["longitud_m"]
        diam_tubo = c.get("diametro_tubo_pvc_mm", c.get("diametro_tubo_mm", 20))

        cond_m = round(length * 2 * 1.1)
        agregar(
            f"Cable TW THW {seccion:.1f} mm2 - {c['id']}".replace(".0", ""),
            "m", cond_m, _get_precio(_cable_precio_key(seccion)),
            c["descripcion"],
        )

        tubo_m = round(length * 1.1)
        agregar(f"Tubo PVC SAP {diam_tubo} mm - {c['id']}", "m", tubo_m,
                _get_precio(_tubo_precio_key(diam_tubo)), c["descripcion"])

        itm_rating = c["itm_a"]
        agregar(f"ITM {c['itm_sugerido']} - {c['id']}", "und", 1,
                _get_precio(_itm_precio_key(itm_rating)), f"Proteccion {c['id']}")

        if "Ver" not in c.get("diferencial_sugerido", ""):
            diff_rating = "2P-25A-30mA" if itm_rating <= 20 else "2P-40A-30mA"
            agregar(
                f"Diferencial {diff_rating} - {c['id']}", "und", 1,
                _get_precio("diferencial_2p_25_30ma" if itm_rating <= 20 else "diferencial_2p_40_30ma"),
                f"Proteccion diferencial {c['id']}",
            )

        n_cajas = max(1, round(length / 3))
        agregar(f"Caja rectangular/octogonal - {c['id']}", "und", n_cajas,
                _get_precio("caja_rectangular"), f"Accesorios {c['id']}")

    total_cond = sum(round(c["longitud_m"] * 2 * 1.1) for c in circuitos)
    total_tubo = sum(round(c["longitud_m"] * 1.1) for c in circuitos)

    agregar("Cable de tierra TW 10 mm2 (verde/amarillo)", "m", round(total_tubo * 0.3),
            _get_precio("cable_tierra_10"), "Puesta a tierra y conexiones equipotenciales")
    agregar("Varilla de puesta a tierra 5/8 x 2.4 m", "und", 1,
            _get_precio("varilla_tierra"), "Sistema de puesta a tierra (SPAT)")
    agregar("Cinta de aislar electrica", "und", 3,
            _get_precio("cinta_aislar"), "Empalmes y conexiones")

    mano_obra = total_costo * 0.40
    total_final = total_costo + mano_obra

    bom = {
        "proyecto": resultados["proyecto"],
        "propietario": resultados["propietario"],
        "fecha": str(date.today()),
        "resumen": {
            "potencia_instalada_w": resumen["potencia_instalada_total_w"],
            "maxima_demanda_w": resumen["maxima_demanda_adoptada_w"],
            "total_cable_m": round(total_cond),
            "total_tubo_m": round(total_tubo),
            "costo_materiales_soles": round(total_costo, 2),
            "mano_obra_40porc_soles": round(mano_obra, 2),
            "costo_total_soles": round(total_final, 2),
        },
        "materiales": materiales,
    }

    json_path = f"{output_base}.json"
    os.makedirs(os.path.dirname(json_path) or ".", exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(bom, f, indent=2, ensure_ascii=False)

    md_lines = [
        f"# Lista de Materiales y Presupuesto",
        f"**Proyecto:** {bom['proyecto']}",
        f"**Propietario:** {bom['propietario']}",
        f"**Fecha:** {bom['fecha']}",
        "",
        "## Resumen",
        f"- Potencia instalada: {bom['resumen']['potencia_instalada_w']:.0f} W",
        f"- Maxima demanda: {bom['resumen']['maxima_demanda_w']:.0f} W",
        f"- Total cable: {bom['resumen']['total_cable_m']} m",
        f"- Total tuberia: {bom['resumen']['total_tubo_m']} m",
        f"- **Costo materiales:** S/ {bom['resumen']['costo_materiales_soles']:.2f}",
        f"- **Mano de obra (40%):** S/ {bom['resumen']['mano_obra_40porc_soles']:.2f}",
        f"- **COSTO TOTAL:** S/ {bom['resumen']['costo_total_soles']:.2f}",
        "",
        "## Materiales",
        "",
        "| Item | Unidad | Cantidad | P.Unit (S/) | Costo (S/) | Uso |",
        "|---|---:|---:|---:|---:|:---|",
    ]
    for m in materiales:
        md_lines.append(
            f"| {m['item']} | {m['unidad']} | {m['cantidad']} | "
            f"{m['precio_unit_soles']:.2f} | {m['costo_soles']:.2f} | {m['uso']} |"
        )
    md_lines.extend([
        "",
        f"**Costo total de materiales: S/ {total_costo:.2f}**",
        f"**Mano de obra (40%): S/ {mano_obra:.2f}**",
        f"**COSTO TOTAL DEL PROYECTO: S/ {total_final:.2f}**",
    ])
    md_path = f"{output_base}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    tex_lines = [
        r"\begin{table}[H]",
        r"\centering",
        r"\caption{Lista de Materiales y Presupuesto Referencial}",
        r"\label{tab:bom}",
        r"\begin{small}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{l c c c c}",
        r"\toprule",
        r"\textbf{Item} & \textbf{Und} & \textbf{Cant} & \textbf{P.U. (S/)} & \textbf{Parcial (S/)} \\",
        r"\midrule",
    ]
    for m in materiales:
        tex_lines.append(
            f"{_tex_escape(m['item'])} & {_tex_escape(m['unidad'])} & {m['cantidad']} & "
            f"{_fmt_num(m['precio_unit_soles'], 2)} & {_fmt_num(m['costo_soles'], 2)} \\\\"
        )
    tex_lines.extend([
        r"\midrule",
        f"\\multicolumn{{4}}{{l}}{{\\textbf{{Costo total materiales}}}} & \\textbf{{{_fmt_num(total_costo, 2)}}} \\\\",
        f"\\multicolumn{{4}}{{l}}{{\\textbf{{Mano de obra (40\\%)}}}} & \\textbf{{{_fmt_num(mano_obra, 2)}}} \\\\",
        f"\\multicolumn{{4}}{{l}}{{\\textbf{{COSTO TOTAL}}}} & \\textbf{{{_fmt_num(total_final, 2)}}} \\\\",
        r"\bottomrule",
        r"\end{tabular}%",
        r"}",
        r"\end{small}",
        r"\end{table}",
    ])
    tex_path = f"{output_base}.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tex_lines))

    return bom
