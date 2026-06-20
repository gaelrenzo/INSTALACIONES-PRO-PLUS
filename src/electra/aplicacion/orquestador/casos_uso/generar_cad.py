"""Caso de uso: generación de planos CAD (DXF/PDF)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from electra.aplicacion.orquestador.dto import EtapaResultado


def ejecutar(
    proyecto_id: str,
    config: Dict[str, Any],
    calculo_json: Optional[Path],
    output_dir: Path,
) -> EtapaResultado:
    from electra.infraestructura.cad import (
        auto_routing,
        dxf_generator,
        electrical_overlay,
        unifilar,
    )

    try:
        cad_dir = output_dir / "cad"
        cad_dir.mkdir(parents=True, exist_ok=True)

        layout_json = None
        layout_path = config.get("layout_json")
        if layout_path:
            lp = Path(str(layout_path))
            if lp.is_absolute() and lp.exists():
                layout_json = lp
            else:
                layout_json = output_dir.parent / lp
                if not layout_json.exists():
                    layout_json = None

        electrico_json_path = output_dir / "electrico.json"
        if not electrico_json_path.exists() and calculo_json and calculo_json.exists():
            with open(calculo_json) as f:
                calculo_data = json.load(f)
            electrico_data = _generar_json_electrico(calculo_data, config)
            with open(electrico_json_path, "w") as f:
                json.dump(electrico_data, f, indent=2)

        dxf_path = cad_dir / "plano_electrico.dxf"
        pdf_path = cad_dir / "plano_electrico.pdf"

        if layout_json and layout_json.exists():
            dxf_generator.generate(layout_json, dxf_path)
        else:
            dxf_generator.generate_default(dxf_path)

        if electrico_json_path.exists():
            electrical_overlay.superponer(
                str(dxf_path), str(electrico_json_path), str(dxf_path)
            )

        unifilar_path = cad_dir / "unifilar.dxf"
        unifilar.generate(electrico_json_path if electrico_json_path.exists() else dxf_path, unifilar_path)

        try:
            auto_routing.route(dxf_path, electrico_json_path if electrico_json_path.exists() else None, dxf_path)
        except Exception:
            pass

        return EtapaResultado(
            nombre="CAD",
            exitoso=True,
            mensaje=f"Planos generados en {cad_dir}",
            archivos_generados={
                "dxf": dxf_path,
                "unifilar": unifilar_path,
            },
        )
    except Exception as e:
        return EtapaResultado(
            nombre="CAD",
            exitoso=False,
            mensaje="Error en generacion CAD",
            error=str(e),
        )


def _generar_json_electrico(calculo: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    pisos = config.get("pisos", [])
    design = calculo.get("escenario_dimensionamiento", calculo)
    circuitos_calc = {c["id"]: c for c in design.get("circuitos_calculados", [])}
    resumen = design.get("resumen_general", {})

    data = {
        "title": {
            "text": f"PLANO ELECTRICO - {config.get('proyecto', 'PROYECTO').upper()}",
            "subtitle": f"Maxima Demanda: {resumen.get('maxima_demanda_adoptada_w', 0):.0f} W",
            "x": 7.5, "y": 10.7, "height": 0.28,
        },
        "luminarias": [],
        "interruptores": [],
        "tomacorrientes": [],
        "tableros": [],
        "medidores": [],
        "equipos": [],
        "rutas": [],
        "circuit_summary": [],
        "notes": [],
        "legend": {"x": 16.7, "y": 9.2, "width": 5.2, "height": 6.0, "title": "LEYENDA ELECTRICA"},
    }

    for c in design.get("circuitos_calculados", []):
        data["circuit_summary"].append({
            "id": c["id"],
            "label": f"{c['descripcion']} | {c['maxima_demanda_w']:.0f}W | {c['seccion_conductor_mm2']:.1f}mm2",
        })

    tg = config.get("tablero_general", {"x": 2.0, "y": 2.0})
    data["tableros"].append({
        "id": 0, "x": tg["x"], "y": tg["y"],
        "label": "TG", "note": f"ITM: {resumen.get('alimentador_itm_sugerido', '')}",
    })
    med = config.get("medidor", {"x": 0.5, "y": 0.5})
    data["medidores"].append({"id": 0, "x": med["x"], "y": med["y"], "label": "M"})

    for piso in pisos:
        for elem_type in ("luminarias", "interruptores", "tomacorrientes"):
            for elem in piso.get(elem_type, []):
                entry = {
                    "id": elem.get("id", len(data[elem_type])),
                    "x": elem["x"], "y": elem["y"],
                    "circuit": elem.get("circuit", "C1"),
                    "label": f"{elem.get('circuit', 'C1')}",
                }
                if elem_type in ("interruptores", "tomacorrientes"):
                    entry["kind"] = elem.get("kind", "simple" if elem_type == "interruptores" else "doble")
                data[elem_type].append(entry)

    data["equipos"] = config.get("equipos", [])
    data["rutas"] = config.get("rutas", [])
    data["notes"] = config.get("notas", [])
    return data
