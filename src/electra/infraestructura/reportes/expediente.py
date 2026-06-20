"""Generador de expediente técnico completo (LaTeX + PDF)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from electra.infraestructura.reportes.latex import tex_escape


def _leer_json(path: Path) -> Dict:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _fmt_fecha() -> str:
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "setiembre", "octubre", "noviembre", "diciembre"]
    from datetime import date as dt_date
    hoy = dt_date.today()
    return f"{hoy.day} de {meses[hoy.month - 1]} de {hoy.year}"


def _fmt(valor: Optional[float], decimales: int = 2) -> str:
    if valor is None:
        return "---"
    return f"{valor:,.{decimales}f}"


def _generar_caratula(data: Dict) -> str:
    proyecto = data.get("proyecto", "Proyecto")
    propietario = data.get("propietario", "Por definir")
    ubicacion = data.get("ubicacion", {})
    distrito = ubicacion.get("distrito", "")
    provincia = ubicacion.get("provincia", "")
    departamento = ubicacion.get("departamento", "")

    return rf"""
\begin{{titlepage}}
\centering
\vspace*{{2cm}}
{{\Huge\bfseries EXPEDIENTE TÉCNICO}}

\vspace{{0.5cm}}
{{\Large\bfseries INSTALACIONES ELÉCTRICAS EN BAJA TENSIÓN}}

\vspace{{1.5cm}}
{{\Large {tex_escape(proyecto)}}}

\vspace{{0.3cm}}
{{\large Propietario: {tex_escape(propietario)}}}

\vspace{{0.3cm}}
{{\large {tex_escape(distrito)}, {tex_escape(provincia)} -- {tex_escape(departamento)}}}

\vspace{{1.5cm}}
{{\large Fecha: {_fmt_fecha()}}}

\vfill
{{\small Basado en CNE-U 050-200 / CNE- Suministro 2011}}
\end{{titlepage}}
"""


def _generar_memoria_descriptiva(data: Dict, config: Dict) -> str:
    proyecto = data.get("proyecto", config.get("proyecto", "Proyecto"))
    propietario = data.get("propietario", config.get("propietario", ""))
    ubicacion = data.get("ubicacion", config)
    distrito = ubicacion.get("distrito", "")
    provincia = ubicacion.get("provincia", "")
    departamento = ubicacion.get("departamento", "")
    params = data.get("parametros_electricos", config)
    tension = params.get("tension_v", 220)
    fases = params.get("fases", 1)
    areas = data.get("areas", {})

    area_total = areas.get("techada_total_calculo_m2", {}).get("valor", "Por definir")

    design = data.get("escenario_dimensionamiento", {})
    resumen = design.get("resumen_general", {})

    return rf"""
\section{{Memoria Descriptiva}}

\subsection{{Datos Generales}}
\begin{{itemize}}
    \item Proyecto: {tex_escape(proyecto)}
    \item Propietario: {tex_escape(propietario)}
    \item Distrito: {tex_escape(distrito)}
    \item Provincia: {tex_escape(provincia)}
    \item Departamento: {tex_escape(departamento)}
    \item Área techada total: {area_total} m$^2$
    \item Tensión nominal: {tension} V
    \item Número de fases: {fases}
\end{{itemize}}

\subsection{{Alcance}}
El presente expediente comprende el diseño de las instalaciones eléctricas
interiores en baja tensión para la edificación mencionada, incluyendo:
\begin{{itemize}}
    \item Circuitos de alumbrado
    \item Circuitos de tomacorrientes
    \item Circuitos para equipos especiales
    \item Alimentador principal y tablero general
    \item Sistema de puesta a tierra (SPAT)
\end{{itemize}}

\subsection{{Normativa Aplicable}}
\begin{{itemize}}
    \item CNE-U 050-200: Cargas de diseño
    \item CNE-U 030-002: Secciones mínimas de conductores
    \item CNE- Suministro 2011: Alimentadores y protecciones
\end{{itemize}}

\subsection{{Resumen de Cargas}}
\begin{{itemize}}
    \item Potencia instalada total: {_fmt(resumen.get('potencia_instalada_total_w'), 0)} W
    \item Máxima demanda adoptada: {_fmt(resumen.get('maxima_demanda_adoptada_w'), 0)} W
    \item Corriente de empleo total: {_fmt(resumen.get('corriente_empleo_ib_total_a'), 2)} A
    \item Alimentador: {_fmt(resumen.get('alimentador_seccion_mm2'), 1)} mm$^2$
    \item ITM general: {tex_escape(resumen.get('alimentador_itm_sugerido', ''))}
\end{{itemize}}
"""


def _generar_calculos_justificativos(data: Dict, resultados_path: Path, output_dir: str) -> str:
    sections = [r"\section{Cálculos Justificativos}"]

    for esc_id, escenario in data.get("escenarios", {}).items():
        res = escenario["resumen_general"]
        label = esc_id.replace("_", "-")
        sections.append(rf"\subsection{{Escenario: {tex_escape(escenario.get('nombre', esc_id))}}}")

        sections.append(rf"""
\begin{{itemize}}
    \item Potencia instalada: {_fmt(res['potencia_instalada_total_w'], 0)} W
    \item Máxima demanda circuitos: {_fmt(res['maxima_demanda_circuitos_w'], 0)} W
    \item Máxima demanda CNE: {_fmt(res['maxima_demanda_cne_w'], 0)} W
    \item Máxima demanda adoptada: {_fmt(res['maxima_demanda_adoptada_w'], 0)} W
    \item Método gobernante: {tex_escape(res.get('metodo_gobernante', ''))}
    \item Corriente de empleo Ib: {_fmt(res['corriente_empleo_ib_total_a'], 2)} A
    \item Corriente de diseño Id: {_fmt(res['corriente_diseno_id_total_a'], 2)} A
    \item Alimentador: {_fmt(res['alimentador_seccion_mm2'], 1)} mm$^2$
    \item ITM general: {tex_escape(res['alimentador_itm_sugerido'])}
    \item Caída de tensión en alimentador: {_fmt(res['alimentador_caida_tension_porc'], 3)}\%
    \item Estado conductor: {tex_escape(res.get('cumple_conductor_alimentador', ''))}
    \item Estado coordinación: {tex_escape(res.get('cumple_coordinacion_alimentador', ''))}
    \item Estado caída de tensión: {tex_escape(res.get('cumple_caida_alimentador', ''))}
\end{{itemize}}
""")

        # Tabla de conductores para cada escenario
        suffix = esc_id
        tex_file = Path(output_dir) / f"tabla_conductores_{suffix}.tex"
        if not tex_file.exists():
            tex_file = Path(output_dir) / f"tabla_conductores.tex"

        if tex_file.exists():
            sections.append(rf"\input{{{tex_file.resolve()}}}")

    return "\n".join(sections)


def _generar_especificaciones_tecnicas() -> str:
    return r"""
\section{Especificaciones Técnicas}

\subsection{Conductores}
\begin{itemize}
    \item Tipo: TW (THW) para instalaciones empotradas en tubería PVC SAP
    \item Tensión de aislamiento: 600 V
    \item Sección mínima: 2.5 mm$^2$ para alumbrado (CNE-U 030-002)
    \item Sección mínima: 2.5 mm$^2$ para tomacorrientes
    \item Sección mínima: 4.0 mm$^2$ para cocinas y equipos especiales
    \item Alimentador principal: según cálculo de máxima demanda
    \item Cable de tierra: 10 mm$^2$ (verde/amarillo)
\end{itemize}

\subsection{Tuberías}
\begin{itemize}
    \item Tubería PVC SAP (pesada) para instalaciones empotradas
    \item Diámetro mínimo: 20 mm para 2 conductores de 2.5 mm$^2$
    \item Tubería para alimentador según sección calculada
\end{itemize}

\subsection{Protecciones}
\begin{itemize}
    \item Interruptores termomagnéticos (ITM): según norma IEC 60898
    \item Interruptores diferenciales: sensibilidad 30 mA
    \item Tablero general: metálico, para montaje empotrado
\end{itemize}

\subsection{Puesta a Tierra}
\begin{itemize}
    \item Varilla de cobre de 5/8" x 2.4 m
    \item Conductor de tierra: TW 10 mm$^2$ (verde/amarillo)
    \item Resistencia de puesta a tierra: $\leq$ 25 $\Omega$
\end{itemize}

\subsection{Elementos de Utilización}
\begin{itemize}
    \item Luminarias LED de acuerdo a la potencia y tipo de ambiente
    \item Interruptores simples y conmutados tipo empotrar
    \item Tomacorrientes dobles con contacto a tierra
    \item Tomacorrientes para cocina y equipos especiales
\end{itemize}
"""


def _generar_metrados_bom(bom: Dict) -> str:
    if not bom:
        return r"\section{Metrados y Presupuesto}\paragraph{No se encontraron datos de BOM.}"

    materiales = bom.get("materiales", [])
    resumen = bom.get("resumen", {})

    lines = [
        r"\section{Metrados y Presupuesto}",
        r"\subsection{Resumen de Costos}",
        r"\begin{table}[H]",
        r"\centering",
        r"\caption{Resumen económico}",
        r"\label{tab:resumen-economico}",
        r"\begin{tabular}{l r}",
        r"\toprule",
        r"\textbf{Concepto} & \textbf{Monto (S/)} \\",
        r"\midrule",
        f"Costo de materiales & S/ {_fmt(resumen.get('costo_materiales_soles', 0), 2)} \\\\",
        f"Mano de obra (40\%) & S/ {_fmt(resumen.get('mano_obra_40porc_soles', 0), 2)} \\\\",
        r"\midrule",
        f"\\textbf{{COSTO TOTAL}} & \\textbf{{S/ {_fmt(resumen.get('costo_total_soles', 0), 2)}}} \\\\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ]

    if materiales:
        lines.extend([
            r"\subsection{Metrados}",
            r"\begin{table}[H]",
            r"\centering",
            r"\caption{Lista de materiales y metrados}",
            r"\label{tab:metrados}",
            r"\begin{footnotesize}",
            r"\begin{tabular}{l c c c c}",
            r"\toprule",
            r"\textbf{Item} & \textbf{Und} & \textbf{Cant} & \textbf{P.U. (S/)} & \textbf{Parcial (S/)} \\",
            r"\midrule",
        ])
        for m in materiales:
            lines.append(
                f"{tex_escape(m.get('item', ''))} & {tex_escape(m.get('unidad', 'und'))} & "
                f"{m.get('cantidad', 0)} & {_fmt(m.get('precio_unit_soles', 0), 2)} & "
                f"{_fmt(m.get('costo_soles', 0), 2)} \\\\"
            )
        lines.extend([
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{footnotesize}",
            r"\end{table}",
        ])

    return "\n".join(lines)


def _generar_planos(proyecto_id: str, build_dir: Path) -> str:
    cad_dir = build_dir / "cad"
    sections = [r"\section{Planos}"]

    dxf = cad_dir / "plano_electrico.dxf"
    pdf = cad_dir / "plano_electrico.pdf"
    unifilar_dxf = cad_dir / "unifilar.dxf"

    if pdf.exists():
        sections.append(rf"""
\subsection{{Plano Eléctrico}}
Se adjunta el plano eléctrico de la instalación.
\vspace{{0.3cm}}

\begin{{center}}
    \includegraphics[width=\textwidth]{{{pdf.resolve()}}}
\end{{center}}
""")

    if dxf.exists():
        sections.append(rf"""
\subsection{{Plano DXF}}
El archivo DXF original se encuentra disponible en la carpeta de planos.
\vspace{{0.3cm}}

\begin{{center}}
    \texttt{{{tex_escape(str(dxf))}}}
\end{{center}}
""")

    if unifilar_dxf.exists():
        sections.append(rf"""
\subsection{{Diagrama Unifilar}}
Se adjunta el diagrama unifilar del alimentador principal y circuitos derivados.
""")

    return "\n".join(sections)


def generar_expediente(
    proyecto_id: str,
    build_dir: Path,
    output_path: str,
    compilar_pdf: bool = True,
) -> str:
    resultados_path = build_dir / "calculos" / "resultados.json"
    bom_path = build_dir / "cotizacion" / "bom.json"

    data = _leer_json(resultados_path)
    bom = _leer_json(bom_path)

    config = data if data else {}
    secciones = [
        _generar_caratula(data or {"proyecto": proyecto_id, "propietario": ""}),
        _generar_memoria_descriptiva(data, {}),
        "\\input{tabla_areas.tex}\n\\input{tabla_cargas.tex}",
        _generar_calculos_justificativos(data, resultados_path, str(build_dir / "calculos")),
        _generar_especificaciones_tecnicas(),
        _generar_metrados_bom(bom),
        _generar_planos(proyecto_id, build_dir),
    ]

    doc = rf"""
\documentclass[12pt,letterpaper]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[spanish]{{babel}}
\usepackage{{graphicx}}
\usepackage{{booktabs}}
\usepackage{{tabularx}}
\usepackage{{geometry}}
\usepackage{{hyperref}}
\usepackage{{float}}
\usepackage{{caption}}
\usepackage{{enumitem}}
\usepackage{{fancyhdr}}
\usepackage{{xcolor}}

\geometry{{margin=2.5cm}}
\pagestyle{{fancy}}
\lhead{{Expediente Técnico - {tex_escape(proyecto_id)}}}
\rhead{{\thepage}}

\begin{{document}}

{"".join(secciones)}

\end{{document}}
"""

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(doc)

    if compilar_pdf:
        _compilar_latex(output_path)

    return output_path


def _compilar_latex(tex_path: str) -> Optional[str]:
    pdf_path = tex_path.replace(".tex", ".pdf")
    tex_dir = os.path.dirname(tex_path) or "."

    try:
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", tex_dir, tex_path],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", tex_dir, tex_path],
                capture_output=True, text=True, timeout=120,
            )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"  [!] Compilación LaTeX no disponible: {e}")
        return None

    if os.path.exists(pdf_path):
        print(f"  [OK] PDF generado: {pdf_path}")
        return pdf_path
    print(f"  [!] No se generó el PDF (revisa logs en {tex_dir})")
    return None
