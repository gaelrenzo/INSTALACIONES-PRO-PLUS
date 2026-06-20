"""Caso de uso: generación de BOM (lista de materiales)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional

from electra.aplicacion.orquestador.dto import EtapaResultado


def ejecutar(
    proyecto_id: str,
    config: Dict[str, Any],
    calculo_json: Optional[Path],
    output_dir: Path,
) -> EtapaResultado:
    try:
        if not calculo_json or not calculo_json.exists():
            raise FileNotFoundError(f"Calculo JSON no encontrado: {calculo_json}")

        with open(calculo_json) as f:
            calculo = json.load(f)

        design = calculo.get("escenario_dimensionamiento", calculo)
        circuitos = design.get("circuitos_calculados", [])
        resumen = design.get("resumen_general", {})

        materiales = _build_materiales(circuitos, resumen)

        bom = {
            "proyecto": calculo.get("proyecto", config.get("proyecto", proyecto_id)),
            "propietario": calculo.get("propietario", config.get("propietario", "")),
            "fecha": str(date.today()),
            "resumen": {
                "potencia_instalada_w": resumen.get("potencia_instalada_total_w", 0),
                "maxima_demanda_w": resumen.get("maxima_demanda_adoptada_w", 0),
            },
            "materiales": materiales,
        }

        bom_dir = output_dir / "bom"
        bom_dir.mkdir(parents=True, exist_ok=True)
        bom_path = bom_dir / "bom.json"
        with open(bom_path, "w") as f:
            json.dump(bom, f, indent=2, ensure_ascii=False)

        return EtapaResultado(
            nombre="BOM",
            exitoso=True,
            mensaje=f"BOM generado: {len(materiales)} materiales",
            archivos_generados={"bom_json": bom_path},
            datos=bom,
        )
    except Exception as e:
        return EtapaResultado(
            nombre="BOM",
            exitoso=False,
            mensaje="Error en generacion BOM",
            error=str(e),
        )


def _build_materiales(
    circuitos: list[Dict[str, Any]], resumen: Dict[str, Any]
) -> list[Dict[str, Any]]:
    materiales = []
    total_cond = 0.0
    total_tubo = 0.0

    long_alim = resumen.get("alimentador_longitud_m", 10)
    seccion_alim = resumen.get("alimentador_seccion_mm2", 10)
    materiales.append({
        "item": f"Cable TW THW {seccion_alim:.0f} mm2 (alimentador)",
        "unidad": "m", "cantidad": round(long_alim * 2 * 1.1),
        "uso": "Alimentador principal",
    })
    materiales.append({
        "item": f"Tubo PVC SAP {seccion_alim * 2 + 4:.0f} mm (alimentador)",
        "unidad": "m", "cantidad": round(long_alim * 1.1),
        "uso": "Alimentador principal",
    })
    materiales.append({
        "item": f"Interruptor termomagnetico {resumen.get('alimentador_itm_sugerido', '2P 40A')}",
        "unidad": "und", "cantidad": 1, "uso": "Proteccion general",
    })

    for c in circuitos:
        long = c.get("longitud_m", 15)
        seccion = c.get("seccion_conductor_mm2", 2.5)
        cond_m = round(long * 2 * 1.1)
        tubo_m = round(long * 1.1)
        materiales.extend([
            {"item": f"Cable TW THW {seccion:.0f} mm2 - {c['id']}", "unidad": "m", "cantidad": cond_m, "uso": c.get("descripcion", "")},
            {"item": f"Tubo PVC SAP {c.get('diametro_tubo_mm', 20)} mm - {c['id']}", "unidad": "m", "cantidad": tubo_m, "uso": c.get("descripcion", "")},
            {"item": f"ITM {c.get('itm_sugerido', '1P 16A')} - {c['id']}", "unidad": "und", "cantidad": 1, "uso": f"Proteccion {c['id']}"},
            {"item": c.get("diferencial_sugerido", "Diferencial general 2P-40A-30mA"), "unidad": "und", "cantidad": 1, "uso": f"Diferencial {c['id']}"},
        ])
        total_cond += cond_m
        total_tubo += tubo_m

    materiales.append({
        "item": f"Tablero general para {len(circuitos)} circuitos",
        "unidad": "und", "cantidad": 1, "uso": "Distribucion",
    })
    materiales.append({
        "item": "Varilla de puesta a tierra 5/8 x 2.4 m",
        "unidad": "und", "cantidad": 1, "uso": "SPAT",
    })
    materiales.append({
        "item": "Cable de tierra TW 10 mm2 (verde/amarillo)",
        "unidad": "m", "cantidad": round(total_tubo * 0.3),
        "uso": "SPAT y conexiones",
    })

    return materiales
