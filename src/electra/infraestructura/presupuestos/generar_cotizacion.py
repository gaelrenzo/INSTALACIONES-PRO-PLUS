#!/usr/bin/env python3
"""
Generador de cotizaciones formales para instalaciones electricas.

Toma el BOM (JSON de materiales) y genera una cotizacion profesional
en formato HTML (imprimible como PDF) y LaTeX, lista para entregar al cliente.

Uso:
  python3 generar_cotizacion.py --bom output/bom.json --output cotizacion
  python3 generar_cotizacion.py --bom output/bom.json --output cotizacion --empresa "Mi Empresa SRL" --cliente "Juan Perez"
  python3 generar_cotizacion.py --bom output/bom.json --precios mis_precios.json
"""

import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_text(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def fmt(n):
    return f"{n:,.2f}"


DEFAULT_EMPRESA = {
    "nombre": "Tu Empresa de Instalaciones Electricas",
    "ruc": "20XXXXXXXXX",
    "direccion": "Av. Principal 123, Lima",
    "telefono": "999 999 999",
    "email": "contacto@tuempresa.pe",
    "web": "",
    "logo": ""
}

DEFAULT_TERMINOS = """
1. Validez de la cotizacion: 15 dias calendario.
2. Forma de pago: 50% adelanto, 50% contra entrega.
3. Los precios incluyen IGV (18%).
4. El plazo de ejecucion se acordara al momento de la aceptacion.
5. Los materiales pueden variar segun disponibilidad, manteniendo la calidad y especificaciones tecnicas.
"""


def generar_cotizacion_html(bom, empresa, cliente, output_path, precios=None):
    materiales = bom.get("materiales", [])
    resumen = bom.get("resumen", {})

    subtotal = sum(m.get("costo_soles", 0) for m in materiales) if materiales else 0
    if precios:
        subtotal = sum(
            m.get("cantidad", 0) * precios.get(m.get("item", ""), m.get("precio_unit_soles", 0))
            for m in materiales
        )

    if subtotal == 0 and "costo_materiales_soles" in resumen:
        subtotal = resumen["costo_materiales_soles"]

    mano_obra = subtotal * 0.40
    igv = (subtotal + mano_obra) * 0.18
    total = subtotal + mano_obra + igv

    rows_html = ""
    for i, m in enumerate(materiales, 1):
        cant = m.get("cantidad", 0)
        pu = m.get("precio_unit_soles", 0)
        if precios and m.get("item") in precios:
            pu = precios[m["item"]]
        parcial = cant * pu
        rows_html += f"""
        <tr>
            <td style="text-align:center">{i}</td>
            <td>{m.get('item', '')}</td>
            <td style="text-align:center">{m.get('unidad', 'und')}</td>
            <td style="text-align:center">{cant}</td>
            <td style="text-align:right">S/ {fmt(pu)}</td>
            <td style="text-align:right">S/ {fmt(parcial)}</td>
        </tr>"""

    fecha_emi = str(date.today())
    fecha_venc = str(date.today() + timedelta(days=15))
    nro_cotizacion = f"COT-{date.today().strftime('%Y%m%d')}-{hash(str(bom)) % 10000:04d}"

    empresa_n = empresa.get("nombre", DEFAULT_EMPRESA["nombre"])
    empresa_ruc = empresa.get("ruc", DEFAULT_EMPRESA["ruc"])
    empresa_dir = empresa.get("direccion", DEFAULT_EMPRESA["direccion"])
    empresa_tel = empresa.get("telefono", DEFAULT_EMPRESA["telefono"])
    empresa_email = empresa.get("email", DEFAULT_EMPRESA["email"])

    proyecto = bom.get("proyecto", "Proyecto de instalaciones electricas")
    propietario = bom.get("propietario", cliente or "Cliente")

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Cotizacion {nro_cotizacion}</title>
<style>
    @page {{ margin: 1.5cm; size: A4; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 11pt;
        color: #1a1a1a;
        padding: 30px;
        max-width: 210mm;
        margin: 0 auto;
        background: #fff;
    }}
    .header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        border-bottom: 3px solid #0f766e;
        padding-bottom: 20px;
        margin-bottom: 25px;
    }}
    .header .empresa h1 {{
        font-size: 18pt;
        color: #0f766e;
        margin-bottom: 4px;
    }}
    .header .empresa p {{
        font-size: 9pt;
        color: #555;
        line-height: 1.5;
    }}
    .header .cotizacion-nro {{
        text-align: right;
        background: #0f766e;
        color: #fff;
        padding: 10px 18px;
        border-radius: 6px;
    }}
    .header .cotizacion-nro h2 {{
        font-size: 11pt;
        font-weight: 400;
    }}
    .header .cotizacion-nro strong {{
        font-size: 14pt;
        display: block;
    }}
    .info-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 25px;
    }}
    .info-box {{
        border: 1px solid #d9e0e7;
        border-radius: 6px;
        padding: 12px 15px;
    }}
    .info-box h3 {{
        font-size: 9pt;
        color: #0f766e;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }}
    .info-box p {{
        font-size: 10pt;
        line-height: 1.5;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 25px;
    }}
    th {{
        background: #0f766e;
        color: #fff;
        padding: 10px 8px;
        font-size: 9pt;
        text-align: left;
    }}
    th.right {{ text-align: right; }}
    th.center {{ text-align: center; }}
    td {{
        padding: 7px 8px;
        border-bottom: 1px solid #e5e7eb;
        font-size: 9.5pt;
    }}
    tr:hover td {{ background: #f9fafb; }}
    .totales {{
        margin-left: auto;
        width: 350px;
        margin-bottom: 25px;
    }}
    .totales table {{ margin-bottom: 0; }}
    .totales td {{
        border: none;
        padding: 5px 10px;
        font-size: 10pt;
    }}
    .totales .total-final td {{
        font-size: 13pt;
        font-weight: 700;
        color: #0f766e;
        border-top: 2px solid #0f766e;
        padding-top: 8px;
    }}
    .terminos {{
        border: 1px solid #d9e0e7;
        border-radius: 6px;
        padding: 15px;
        background: #f9fafb;
        font-size: 9pt;
        line-height: 1.6;
        color: #555;
        margin-bottom: 20px;
    }}
    .terminos h3 {{
        color: #0f766e;
        font-size: 10pt;
        margin-bottom: 6px;
    }}
    .footer {{
        text-align: center;
        font-size: 8pt;
        color: #999;
        border-top: 1px solid #d9e0e7;
        padding-top: 12px;
    }}
    @media print {{
        body {{ padding: 0; }}
        .no-print {{ display: none; }}
    }}
    .badge {{
        display: inline-block;
        background: #dcfce7;
        color: #166534;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 8pt;
        font-weight: 600;
    }}
</style>
</head>
<body>

<div class="header">
    <div class="empresa">
        <h1>{empresa_n}</h1>
        <p>RUC: {empresa_ruc}<br>
        {empresa_dir}<br>
        Tel: {empresa_tel} | Email: {empresa_email}</p>
    </div>
    <div class="cotizacion-nro">
        <h2>COTIZACION</h2>
        <strong>{nro_cotizacion}</strong>
    </div>
</div>

<div class="info-grid">
    <div class="info-box">
        <h3>Cliente</h3>
        <p><strong>{propietario}</strong><br>
        {bom.get('proyecto', '')}</p>
    </div>
    <div class="info-box">
        <h3>Datos de la cotizacion</h3>
        <p>
        <strong>Emision:</strong> {fecha_emi}<br>
        <strong>Validez:</strong> {fecha_venc}<br>
        <strong>Estado:</strong> <span class="badge">Cotizacion</span>
        </p>
    </div>
</div>

<table>
<thead>
    <tr>
        <th style="width:40px;text-align:center">#</th>
        <th>Descripcion</th>
        <th style="width:50px;text-align:center">Und</th>
        <th style="width:50px;text-align:center">Cant</th>
        <th style="width:90px;text-align:right">P. Unitario</th>
        <th style="width:100px;text-align:right">Parcial</th>
    </tr>
</thead>
<tbody>
    {rows_html}
</tbody>
</table>

<div class="totales">
    <table>
        <tr><td style="text-align:right">Subtotal Materiales</td><td style="text-align:right;width:110px">S/ {fmt(subtotal)}</td></tr>
        <tr><td style="text-align:right">Mano de Obra (40%)</td><td style="text-align:right">S/ {fmt(mano_obra)}</td></tr>
        <tr><td style="text-align:right">IGV (18%)</td><td style="text-align:right">S/ {fmt(igv)}</td></tr>
        <tr class="total-final"><td style="text-align:right">TOTAL</td><td style="text-align:right">S/ {fmt(total)}</td></tr>
    </table>
</div>

<div class="terminos">
    <h3>Terminos y Condiciones</h3>
    {DEFAULT_TERMINOS.strip().replace(chr(10), '<br>')}
</div>

<div class="footer">
    Documento generado automaticamente el {fecha_emi} | {empresa_n} - RUC: {empresa_ruc}
</div>

<div class="no-print" style="margin-top:20px;text-align:center">
    <button onclick="window.print()" style="
        background:#0f766e;color:#fff;border:0;border-radius:6px;
        padding:10px 24px;font-size:11pt;cursor:pointer;
    ">Imprimir / Guardar PDF</button>
</div>

</body>
</html>"""

    write_text(f"{output_path}.html", html)
    print(f"Cotizacion HTML: {output_path}.html")

    return {
        "nro": nro_cotizacion,
        "cliente": propietario,
        "fecha": fecha_emi,
        "validez": fecha_venc,
        "subtotal": subtotal,
        "mano_obra": mano_obra,
        "igv": igv,
        "total": total
    }


def generar_cotizacion_latex(bom, empresa, cliente, output_path, precios=None):
    materiales = bom.get("materiales", [])
    resumen = bom.get("resumen", {})

    subtotal = sum(m.get("costo_soles", 0) for m in materiales) if materiales else 0
    if subtotal == 0 and "costo_materiales_soles" in resumen:
        subtotal = resumen["costo_materiales_soles"]

    mano_obra = subtotal * 0.40
    igv = (subtotal + mano_obra) * 0.18
    total = subtotal + mano_obra + igv
    nro_cot = f"COT-{date.today().strftime('%Y%m%d')}-{hash(str(bom)) % 10000:04d}"

    def tex(s):
        return s.replace("&", "\\&").replace("%", "\\%").replace("$", "\\$").replace("_", "\\_").replace("#", "\\#")

    rows = ""
    for i, m in enumerate(materiales, 1):
        cant = m.get("cantidad", 0)
        pu = m.get("precio_unit_soles", 0)
        parcial = cant * pu
        rows += f"{i} & {tex(m.get('item', ''))} & {m.get('unidad', 'und')} & {cant} & {fmt(pu)} & {fmt(parcial)} \\\\\n"

    fecha_emi = str(date.today())
    fecha_venc = str(date.today() + timedelta(days=15))
    proyecto = tex(bom.get("proyecto", "Proyecto"))
    propietario = tex(cliente or bom.get("propietario", "Cliente"))
    emp_n = tex(empresa.get("nombre", DEFAULT_EMPRESA["nombre"]))
    emp_ruc = tex(empresa.get("ruc", DEFAULT_EMPRESA["ruc"]))
    emp_dir = tex(empresa.get("direccion", DEFAULT_EMPRESA["direccion"]))

    tex_content = f"""\\documentclass[12pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{geometry,graphicx,booktabs,array,longtable}}
\\geometry{{margin=2cm,a4paper}}
\\usepackage{{fancyhdr}}
\\pagestyle{{fancy}}
\\fancyhead[L]{{{emp_n}}}
\\fancyhead[R]{{RUC: {emp_ruc}}}
\\fancyfoot[C]{{\\footnotesize Documento generado el {fecha_emi} -- {emp_n}}}

\\begin{{document}}

\\begin{{center}}
\\huge\\textbf{{COTIZACION}}\\\\[4pt]
\\Large\\textbf{{{nro_cot}}}
\\end{{center}}

\\vspace{{0.5cm}}

\\noindent
\\begin{{minipage}}{{0.48\\textwidth}}
\\textbf{{Cliente:}} {propietario}\\\\
\\textbf{{Proyecto:}} {proyecto}
\\end{{minipage}}
\\hfill
\\begin{{minipage}}{{0.48\\textwidth}}
\\raggedleft
\\textbf{{Emision:}} {fecha_emi}\\\\
\\textbf{{Validez:}} {fecha_venc}
\\end{{minipage}}

\\vspace{{0.5cm}}

\\begin{{center}}
\\begin{{tabular}}{{c l c c r r}}
\\toprule
\\textbf{{#}} & \\textbf{{Descripcion}} & \\textbf{{Und}} & \\textbf{{Cant}} & \\textbf{{P.U. (S/)}} & \\textbf{{Parcial (S/)}} \\\\
\\midrule
{rows}\\midrule
& \\multicolumn{{4}}{{l}}{{\\textbf{{Subtotal Materiales}}}} & \\textbf{{{fmt(subtotal)}}} \\\\
& \\multicolumn{{4}}{{l}}{{\\textbf{{Mano de Obra (40\\%)}}}} & \\textbf{{{fmt(mano_obra)}}} \\\\
& \\multicolumn{{4}}{{l}}{{\\textbf{{IGV (18\\%)}}}} & \\textbf{{{fmt(igv)}}} \\\\
\\multicolumn{{5}}{{l}}{{\\huge\\textbf{{TOTAL}}}} & \\huge\\textbf{{S/ {fmt(total)}}} \\\\
\\bottomrule
\\end{{tabular}}
\\end{{center}}

\\vspace{{0.5cm}}
\\noindent\\textbf{{Terminos y Condiciones:}}
\\begin{{small}}
\\begin{{enumerate}}
\\item Validez de la cotizacion: 15 dias calendario.
\\item Forma de pago: 50\\% adelanto, 50\\% contra entrega.
\\item Los precios incluyen IGV (18\\%).
\\item El plazo de ejecucion se acordara al momento de la aceptacion.
\\item Los materiales pueden variar segun disponibilidad, manteniendo la calidad.
\\end{{enumerate}}
\\end{{small}}

\\end{{document}}"""

    write_text(f"{output_path}.tex", tex_content)
    print(f"Cotizacion LaTeX: {output_path}.tex")

    try:
        import subprocess
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", f"{output_path}.tex"],
            capture_output=True, text=True, timeout=60
        )
        if os.path.exists(f"{output_path}.pdf"):
            print(f"Cotizacion PDF: {output_path}.pdf")
        else:
            print("PDF no generado (instala pdflatex para compilar)")
    except Exception:
        print("PDF no generado (pdflatex no disponible)")


def load_precios(path):
    precios = {}
    if path and os.path.exists(path):
        with open(path) as f:
            precios = json.load(f)
        print(f"Precios personalizados cargados: {len(precios)} items")
    return precios


def parse_args():
    parser = argparse.ArgumentParser(description="Genera cotizaciones profesionales para instalaciones electricas")
    parser.add_argument("--bom", required=True, help="JSON del BOM (generado por generar_bom.py)")
    parser.add_argument("--output", default="cotizacion", help="Ruta base de salida")
    parser.add_argument("--empresa", help="Archivo JSON con datos de la empresa")
    parser.add_argument("--cliente", help="Nombre del cliente (opcional, usa el del BOM si no se da)")
    parser.add_argument("--precios", help="JSON con precios personalizados (key: nombre item, value: precio)")
    parser.add_argument("--format", choices=["html", "latex", "both"], default="both", help="Formato de salida")
    parser.add_argument("--nombre-empresa", help="Nombre de la empresa (alternativa rapida)")
    parser.add_argument("--ruc", help="RUC de la empresa (alternativa rapida)")
    return parser.parse_args()


def main():
    args = parse_args()

    if not os.path.exists(args.bom):
        print(f"Error: No existe el BOM: {args.bom}")
        sys.exit(1)

    bom = load_json(args.bom)

    empresa = DEFAULT_EMPRESA.copy()
    if args.empresa and os.path.exists(args.empresa):
        empresa_custom = load_json(args.empresa)
        empresa.update(empresa_custom)
    if args.nombre_empresa:
        empresa["nombre"] = args.nombre_empresa
    if args.ruc:
        empresa["ruc"] = args.ruc

    precios = load_precios(args.precios)

    cliente = args.cliente or bom.get("propietario", "Cliente")

    print(f"\nGenerando cotizacion para: {cliente}")
    print(f"Proyecto: {bom.get('proyecto', 'N/E')}")
    print("-" * 50)

    if args.format in ("html", "both"):
        resultado = generar_cotizacion_html(bom, empresa, cliente, args.output, precios)
        print(f"\n  Subtotal:  S/ {fmt(resultado['subtotal'])}")
        print(f"  Mano obra: S/ {fmt(resultado['mano_obra'])}")
        print(f"  IGV:       S/ {fmt(resultado['igv'])}")
        print(f"  TOTAL:     S/ {fmt(resultado['total'])}")

    if args.format in ("latex", "both"):
        generar_cotizacion_latex(bom, empresa, cliente, args.output, precios)

    print(f"\nAbre {args.output}.html en tu navegador y usa Ctrl+P para imprimir/guardar PDF.")


if __name__ == "__main__":
    main()
