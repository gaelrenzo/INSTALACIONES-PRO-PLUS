"""Generación de tablas LaTeX para informes de cálculos eléctricos."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional


def tex_escape(value: Any) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def fmt_num(value: Optional[float], digits: int = 0) -> str:
    if value is None:
        return "Por confirmar"
    if digits == 0:
        return f"{value:,.0f}"
    return f"{value:,.{digits}f}"


def _write_tex(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def area_table(data: Dict, output_dir: str) -> str:
    labels = [
        ("terreno_m2", "Area de terreno"),
        ("techada_primer_piso_m2", "Area techada primer piso"),
        ("techada_segundo_piso_m2", "Area techada segundo piso"),
        ("techada_total_calculo_m2", "Area techada total de calculo"),
    ]
    lines = [
        r"\begin{table}[H]",
        r"\centering",
        r"\caption{Datos base de areas usados para calculo preliminar.}",
        r"\label{tab:areas_base_calculo}",
        r"\begin{small}",
        r"\begin{tabularx}{\textwidth}{l c l L}",
        r"\toprule",
        r"\textbf{Dato} & \textbf{Valor (m$^2$)} & \textbf{Estado} & \textbf{Fuente / observacion} \\",
        r"\midrule",
    ]
    for key, label in labels:
        item = data["areas"][key]
        value = item.get("valor")
        value_tex = "Por confirmar" if value is None else fmt_num(float(value), 2)
        lines.append(
            f"{tex_escape(label)} & {value_tex} & {tex_escape(item.get('estado', 'preliminar'))} & {tex_escape(item.get('fuente', ''))} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabularx}", r"\end{small}", r"\end{table}"])
    out = os.path.join(output_dir, "tabla_areas.tex")
    _write_tex(out, "\n".join(lines))
    return out


def scenarios_table(results: Dict, output_dir: str) -> str:
    lines = [
        r"\begin{table}[H]",
        r"\centering",
        r"\caption{Comparacion de escenarios de maxima demanda preliminar.}",
        r"\label{tab:escenarios_demanda}",
        r"\begin{scriptsize}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{l c c c c c c c c}",
        r"\toprule",
        r"\textbf{Escenario} & \textbf{P.I. (W)} & \textbf{MD circ. (W)} & \textbf{MD CNE (W)} & \textbf{MD adopt. (W)} & \textbf{Ib (A)} & \textbf{Cond. (mm$^2$)} & \textbf{ITM} & \textbf{dV alim. (\%)} \\",
        r"\midrule",
    ]
    for scenario in results["escenarios"].values():
        res = scenario["resumen_general"]
        lines.append(
            f"{tex_escape(scenario['nombre'])} & "
            f"{fmt_num(res['potencia_instalada_total_w'])} & "
            f"{fmt_num(res['maxima_demanda_circuitos_w'])} & "
            f"{fmt_num(res['maxima_demanda_cne_w'])} & "
            f"{fmt_num(res['maxima_demanda_adoptada_w'])} & "
            f"{fmt_num(res['corriente_empleo_ib_total_a'], 2)} & "
            f"{fmt_num(res['alimentador_seccion_mm2'], 1)} & "
            f"{tex_escape(res['alimentador_itm_sugerido'])} & "
            f"{fmt_num(res['alimentador_caida_tension_porc'], 3)} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}%", r"}", r"\end{scriptsize}", r"\end{table}"])
    out = os.path.join(output_dir, "tabla_escenarios.tex")
    _write_tex(out, "\n".join(lines))
    return out


def cargas_table(scenario_result: Dict, output_dir: str, filename: str) -> str:
    label_id = scenario_result["id"].replace("_", "-")
    lines = [
        r"\begin{table}[H]",
        r"\centering",
        rf"\caption{{Cuadro de cargas preliminar - {tex_escape(scenario_result['nombre'])}.}}",
        rf"\label{{tab:cuadro-cargas-{label_id}}}",
        r"\begin{small}",
        r"\begin{tabular}{l l c c c}",
        r"\toprule",
        r"\textbf{Circuito} & \textbf{Descripcion (Uso)} & \textbf{P.I. (W)} & \textbf{F.D.} & \textbf{M.D. (W)} \\",
        r"\midrule",
    ]
    for circ in scenario_result["circuitos_calculados"]:
        lines.append(
            f"{tex_escape(circ['id'])} & {tex_escape(circ['descripcion'])} & "
            f"{fmt_num(circ['potencia_instalada_w'])} & {circ['factor_demanda']:.2f} & "
            f"{fmt_num(circ['maxima_demanda_w'], 1)} \\\\"
        )
    res = scenario_result["resumen_general"]
    lines.extend([
        r"\midrule",
        f"\\multicolumn{{2}}{{l}}{{\\textbf{{Total instalado / MD circuitos}}}} & "
        f"\\textbf{{{fmt_num(res['potencia_instalada_total_w'])}}} & & "
        f"\\textbf{{{fmt_num(res['maxima_demanda_circuitos_w'], 1)}}} \\\\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{small}",
        r"\end{table}",
    ])
    out = os.path.join(output_dir, filename)
    _write_tex(out, "\n".join(lines))
    return out


def conductores_table(scenario_result: Dict, output_dir: str, filename: str) -> str:
    res = scenario_result["resumen_general"]
    label_id = scenario_result["id"].replace("_", "-")
    lines = [
        r"\begin{table}[H]",
        r"\centering",
        rf"\caption{{Seleccion preliminar de conductores y protecciones - {tex_escape(scenario_result['nombre'])}.}}",
        rf"\label{{tab:conductores-protecciones-{label_id}}}",
        r"\begin{scriptsize}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{l c c c c c l c c c}",
        r"\toprule",
        r"\textbf{Circ.} & \textbf{P.I. (W)} & \textbf{M.D. (W)} & \textbf{Ib (A)} & \textbf{Id (A)} & \textbf{Cond.} & \textbf{ITM} & \textbf{Iz (A)} & \textbf{dV (\%)} & \textbf{Estado} \\",
        r"\midrule",
        f"Alim. & {fmt_num(res['potencia_instalada_total_w'])} & {fmt_num(res['maxima_demanda_adoptada_w'])} & "
        f"{fmt_num(res['corriente_empleo_ib_total_a'], 2)} & {fmt_num(res['corriente_diseno_id_total_a'], 2)} & "
        f"{fmt_num(res['alimentador_seccion_mm2'], 1)} mm$^2$ & {tex_escape(res['alimentador_itm_sugerido'])} & "
        f"{fmt_num(res['alimentador_ampacidad_iz_a'])} & {fmt_num(res['alimentador_caida_tension_porc'], 3)} & "
        f"{tex_escape(res['cumple_conductor_alimentador'])} \\\\",
        r"\midrule",
    ]
    for circ in scenario_result["circuitos_calculados"]:
        estado = f"{circ['cumple_conductor']}/{circ['cumple_coordinacion']}/{circ['cumple_caida']}"
        lines.append(
            f"{tex_escape(circ['id'])} & {fmt_num(circ['potencia_instalada_w'])} & "
            f"{fmt_num(circ['maxima_demanda_w'], 1)} & {fmt_num(circ['corriente_empleo_ib_a'], 2)} & "
            f"{fmt_num(circ['corriente_diseno_id_a'], 2)} & {fmt_num(circ['seccion_conductor_mm2'], 1)} mm$^2$ & "
            f"{tex_escape(circ['itm_sugerido'])} & {fmt_num(circ['ampacidad_conductor_iz_a'])} & "
            f"{fmt_num(circ['caida_tension_porc'], 3)} & {tex_escape(estado)} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}%", r"}", r"\end{scriptsize}", r"\end{table}"])
    out = os.path.join(output_dir, filename)
    _write_tex(out, "\n".join(lines))
    return out


def generar_tablas_latex(results: Dict, output_dir: str) -> List[str]:
    os.makedirs(output_dir, exist_ok=True)
    files = []
    files.append(area_table(results, output_dir))
    files.append(scenarios_table(results, output_dir))

    design = results["escenario_dimensionamiento"]
    files.append(cargas_table(design, output_dir, "tabla_cargas.tex"))
    files.append(conductores_table(design, output_dir, "tabla_conductores.tex"))

    for scenario in results["escenarios"].values():
        suffix = scenario["id"]
        files.append(cargas_table(scenario, output_dir, f"tabla_cargas_{suffix}.tex"))
        files.append(conductores_table(scenario, output_dir, f"tabla_conductores_{suffix}.tex"))

    return files
