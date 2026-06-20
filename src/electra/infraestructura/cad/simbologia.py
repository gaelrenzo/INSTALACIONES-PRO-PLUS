"""DGE symbology catalog generator — DXF blocks, SVG export, PDF rendering."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from ezdxf.enums import TextEntityAlignment


def _cargar_biblioteca_json(json_path: str) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _crear_capas(doc):
    COLOR_ROJO = 1
    COLOR_AMARILLO = 2
    COLOR_GRIS_OSCURO = 8
    COLOR_GRIS_CLARO = 9
    COLOR_CIAN = 4
    capas = [
        ("SIMBOLOS_DGE", COLOR_AMARILLO, 25),
        ("TEXTOS_CODIGOS", COLOR_ROJO, 18),
        ("TEXTOS_NOMBRES", 7, 13),
        ("CELDAS_GUIA", COLOR_GRIS_OSCURO, 9),
        ("OBSERVACIONES", COLOR_GRIS_CLARO, 9),
        ("TITULOS", COLOR_CIAN, 30),
        ("MARCOS", 7, 35),
    ]
    for name, color, lw in capas:
        if name not in doc.layers:
            doc.layers.new(name, dxfattribs={"color": color, "lineweight": lw})


def _crear_bloque_simbolo(doc, simbolo):
    block_name = simbolo["block_name"]
    if block_name in doc.blocks:
        return doc.blocks.get(block_name)

    block = doc.blocks.new(name=block_name)
    layer = "SIMBOLOS_DGE"

    for prim in simbolo["primitivas"]:
        tipo = prim["tipo"]
        try:
            if tipo == "linea":
                block.add_line(
                    (float(prim["x1"]), float(prim["y1"])),
                    (float(prim["x2"]), float(prim["y2"])),
                    dxfattribs={"layer": layer},
                )
            elif tipo == "circulo":
                block.add_circle(
                    (float(prim["cx"]), float(prim["cy"])),
                    float(prim["r"]),
                    dxfattribs={"layer": layer},
                )
            elif tipo == "circulo_relleno":
                r = float(prim["r"])
                cx = float(prim["cx"])
                cy = float(prim["cy"])
                block.add_circle((cx, cy), r, dxfattribs={"layer": layer})
                hatch = block.add_hatch(dxfattribs={"layer": layer})
                hatch.set_solid_fill()
                edge_path = hatch.paths.add_edge_path()
                edge_path.add_arc((cx, cy), r, 0, 360)
            elif tipo == "rectangulo":
                x = float(prim["x"])
                y = float(prim["y"])
                w = float(prim["w"])
                h = float(prim["h"])
                pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
                block.add_lwpolyline(pts, dxfattribs={"layer": layer})
            elif tipo == "rectangulo_relleno":
                x = float(prim["x"])
                y = float(prim["y"])
                w = float(prim["w"])
                h = float(prim["h"])
                block.add_solid(
                    [(x, y), (x + w, y), (x, y + h), (x + w, y + h)],
                    dxfattribs={"layer": layer},
                )
            elif tipo == "arco":
                cx = float(prim["cx"])
                cy = float(prim["cy"])
                r = float(prim["r"])
                start = float(prim["ang_ini"])
                end = float(prim["ang_fin"])
                block.add_arc((cx, cy), r, start, end, dxfattribs={"layer": layer})
            elif tipo == "texto":
                text_entity = block.add_text(
                    str(prim["contenido"]),
                    dxfattribs={"layer": layer, "height": float(prim["h"])},
                )
                text_entity.set_placement(
                    (float(prim["x"]), float(prim["y"])),
                    align=TextEntityAlignment.MIDDLE_CENTER,
                )
            elif tipo == "punto":
                block.add_circle(
                    (float(prim["x"]), float(prim["y"])),
                    float(prim["r"]),
                    dxfattribs={"layer": layer},
                )
        except Exception as e:
            print(f"Error procesando primitiva {prim} en simbolo {simbolo['id']}: {e}")

    return block


def _dibujar_lamina_catalogo(doc, data):
    msp = doc.modelspace()
    simbolos = data["simbolos"]

    categorias = {}
    for sim in simbolos:
        cat = sim.get("categoria", "OTROS SIMBOLOS DGE").upper()
        if cat not in categorias:
            categorias[cat] = []
        categorias[cat].append(sim)

    celda_w = 60.0
    celda_h = 35.0
    cols_por_fila = 3
    separacion_y = 15.0

    start_x = 0.0
    start_y = 0.0
    current_y = start_y

    for cat, sim_list in categorias.items():
        current_y -= 10.0
        msp.add_text(
            f"=== CATEGORIA: {cat} ===",
            dxfattribs={"layer": "TITULOS", "height": 3.5},
        ).set_placement((start_x, current_y), align=TextEntityAlignment.MIDDLE_LEFT)
        current_y -= 12.0

        for i, sim in enumerate(sim_list):
            col = i % cols_por_fila
            row = i // cols_por_fila

            x = start_x + col * (celda_w + 10.0)
            y = current_y - row * (celda_h + 10.0)

            rect_pts = [(x, y), (x + celda_w, y), (x + celda_w, y - celda_h), (x, y - celda_h), (x, y)]
            msp.add_lwpolyline(rect_pts, dxfattribs={"layer": "CELDAS_GUIA"})

            _crear_bloque_simbolo(doc, sim)
            sym_x = x + 15.0
            sym_y = y - 17.5
            scale_factor = 45.0

            msp.add_blockref(
                sim["block_name"],
                insert=(sym_x, sym_y),
                dxfattribs={"layer": "SIMBOLOS_DGE", "xscale": scale_factor, "yscale": scale_factor, "zscale": scale_factor},
            )

            text_x = x + 30.0

            msp.add_text(
                f"COD: {sim['codigo_dge']}",
                dxfattribs={"layer": "TEXTOS_CODIGOS", "height": 1.8},
            ).set_placement((text_x, y - 8.0), align=TextEntityAlignment.MIDDLE_LEFT)

            nombre = sim["nombre"]
            if len(nombre) > 28:
                partes = nombre.split(" ")
                mitad = len(partes) // 2
                nombre_l1 = " ".join(partes[:mitad])
                nombre_l2 = " ".join(partes[mitad:])
                msp.add_text(
                    nombre_l1,
                    dxfattribs={"layer": "TEXTOS_NOMBRES", "height": 1.4},
                ).set_placement((text_x, y - 15.0), align=TextEntityAlignment.MIDDLE_LEFT)
                msp.add_text(
                    nombre_l2,
                    dxfattribs={"layer": "TEXTOS_NOMBRES", "height": 1.4},
                ).set_placement((text_x, y - 20.0), align=TextEntityAlignment.MIDDLE_LEFT)
                y_offset_obs = -26.0
            else:
                msp.add_text(
                    nombre,
                    dxfattribs={"layer": "TEXTOS_NOMBRES", "height": 1.5},
                ).set_placement((text_x, y - 16.0), align=TextEntityAlignment.MIDDLE_LEFT)
                y_offset_obs = -24.0

            obs = sim.get("observaciones", "")
            if len(obs) > 30:
                obs = obs[:28] + "..."
            if obs:
                msp.add_text(
                    f"* {obs}",
                    dxfattribs={"layer": "OBSERVACIONES", "height": 1.0},
                ).set_placement((text_x, y + y_offset_obs), align=TextEntityAlignment.MIDDLE_LEFT)

        filas = (len(sim_list) - 1) // cols_por_fila + 1
        current_y -= filas * (celda_h + 10.0) + separacion_y

    extents_min_x = start_x - 5.0
    extents_max_x = start_x + cols_por_fila * (celda_w + 10.0)
    extents_min_y = current_y + separacion_y
    extents_max_y = start_y + 10.0

    marco_pts = [
        (extents_min_x, extents_max_y),
        (extents_max_x, extents_max_y),
        (extents_max_x, extents_min_y),
        (extents_min_x, extents_min_y),
        (extents_min_x, extents_max_y),
    ]
    msp.add_lwpolyline(marco_pts, dxfattribs={"layer": "MARCOS"})

    msp.add_text(
        "BIBLIOTECA COMPLETA DE SIMBOLOGIA ELECTRICA - NORMA DGE (SECCION 9)",
        dxfattribs={"layer": "TITULOS", "height": 4.5},
    ).set_placement((start_x + 10.0, start_y + 5.0), align=TextEntityAlignment.MIDDLE_LEFT)


def _exportar_a_svg_simbolos(data, svg_dir: str) -> int:
    Path(svg_dir).mkdir(parents=True, exist_ok=True)
    simbolos = data.get("simbolos", [])
    count = 0

    for sim in simbolos:
        block_name = sim.get("block_name", f"simbolo_{sim['id']}")
        primitivas = sim.get("primitivas", [])
        if not primitivas:
            continue

        xs, ys = [], []
        for p in primitivas:
            if p["tipo"] in ("linea",):
                xs.extend([float(p["x1"]), float(p["x2"])])
                ys.extend([float(p["y1"]), float(p["y2"])])
            elif p["tipo"] in ("circulo", "circulo_relleno", "arco", "punto"):
                xs.append(float(p["cx"]) - float(p["r"]))
                xs.append(float(p["cx"]) + float(p["r"]))
                ys.append(float(p["cy"]) - float(p["r"]))
                ys.append(float(p["cy"]) + float(p["r"]))
            elif p["tipo"] in ("rectangulo", "rectangulo_relleno"):
                xs.extend([float(p["x"]), float(p["x"]) + float(p["w"])])
                ys.extend([float(p["y"]), float(p["y"]) + float(p["h"])])

        if not xs:
            continue

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        pad = 2
        width = max_x - min_x + 2 * pad
        height = max_y - min_y + 2 * pad

        svg = Element("svg", {
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": f"{min_x - pad} {min_y - pad} {width} {height}",
            "width": f"{width * 10}",
            "height": f"{height * 10}",
        })

        style = Element("style")
        style.text = ".sym { stroke: #FFD700; stroke-width: 0.3; fill: none; } .sym-fill { fill: #FFD700; } .sym-text { fill: white; font-family: monospace; font-size: 0.5px; }"
        svg.append(style)

        bg = SubElement(svg, "rect", {
            "x": f"{min_x - pad}", "y": f"{min_y - pad}",
            "width": f"{width}", "height": f"{height}",
            "fill": "#1a1a2e",
        })

        for p in primitivas:
            try:
                if p["tipo"] == "linea":
                    SubElement(svg, "line", {"x1": str(p["x1"]), "y1": str(p["y1"]), "x2": str(p["x2"]), "y2": str(p["y2"]), "class": "sym"})
                elif p["tipo"] == "circulo":
                    SubElement(svg, "circle", {"cx": str(p["cx"]), "cy": str(p["cy"]), "r": str(p["r"]), "class": "sym"})
                elif p["tipo"] == "circulo_relleno":
                    SubElement(svg, "circle", {"cx": str(p["cx"]), "cy": str(p["cy"]), "r": str(p["r"]), "class": "sym sym-fill"})
                elif p["tipo"] == "rectangulo":
                    SubElement(svg, "rect", {"x": str(p["x"]), "y": str(p["y"]), "width": str(p["w"]), "height": str(p["h"]), "class": "sym"})
                elif p["tipo"] == "rectangulo_relleno":
                    SubElement(svg, "rect", {"x": str(p["x"]), "y": str(p["y"]), "width": str(p["w"]), "height": str(p["h"]), "class": "sym sym-fill"})
                elif p["tipo"] == "arco":
                    cx, cy, r = float(p["cx"]), float(p["cy"]), float(p["r"])
                    a1, a2 = math.radians(float(p["ang_ini"])), math.radians(float(p["ang_fin"]))
                    x1 = cx + r * math.cos(a1)
                    y1 = cy + r * math.sin(a1)
                    x2 = cx + r * math.cos(a2)
                    y2 = cy + r * math.sin(a2)
                    large = 1 if abs(a2 - a1) > math.pi else 0
                    SubElement(svg, "path", {"d": f"M {x1},{y1} A {r},{r} 0 {large} 1 {x2},{y2}", "class": "sym"})
                elif p["tipo"] == "texto":
                    SubElement(svg, "text", {"x": str(p["x"]), "y": str(p["y"]), "class": "sym-text", "text-anchor": "middle", "dominant-baseline": "central"}).text = str(p.get("contenido", ""))
                elif p["tipo"] == "punto":
                    SubElement(svg, "circle", {"x": str(p["x"]), "y": str(p["y"]), "r": str(p.get("r", 0.3)), "class": "sym sym-fill"})
            except Exception as e:
                print(f"Error SVG en {sim['id']}: {e}")

        xml_str = minidom.parseString(tostring(svg)).toprettyxml(indent="  ")
        filepath = Path(svg_dir) / f"{block_name}.svg"
        filepath.write_text(xml_str, encoding="utf-8")
        count += 1

    return count


def generate_symbology_catalog(json_path: str, output_dxf: str, output_svg_dir: str | None = None) -> str:
    import ezdxf

    data = _cargar_biblioteca_json(json_path)

    doc = ezdxf.new("R2010")
    _crear_capas(doc)
    _dibujar_lamina_catalogo(doc, data)

    Path(output_dxf).parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(output_dxf)

    if output_svg_dir:
        _exportar_a_svg_simbolos(data, output_svg_dir)

    return output_dxf


def generate_symbology_pdf(dxf_path: str, pdf_path: str) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import RenderContext, Frontend
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    import ezdxf

    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    fig = plt.figure(figsize=(22, 34), dpi=150)
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax.set_aspect("equal")
    ax.axis("off")
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp, finalize=True)
    Path(pdf_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(pdf_path, dpi=200, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    return pdf_path
