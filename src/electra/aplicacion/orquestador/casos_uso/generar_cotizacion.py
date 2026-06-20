"""Caso de uso: cotización multi-proveedor y generación de documento formal."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from electra.aplicacion.orquestador.dto import EtapaResultado
from electra.infraestructura.presupuestos.bom_precios import generar_bom as generar_bom_precios


def ejecutar(
    proyecto_id: str,
    config: Dict[str, Any],
    calculo_json: Optional[Path],
    output_dir: Path,
    proveedores: Optional[list[str]] = None,
) -> EtapaResultado:
    try:
        if not calculo_json or not calculo_json.exists():
            raise FileNotFoundError(f"JSON de calculos no encontrado: {calculo_json}")

        cot_dir = output_dir / "cotizacion"
        cot_dir.mkdir(parents=True, exist_ok=True)

        bom_base = str(cot_dir / "bom")
        bom = generar_bom_precios(str(calculo_json), bom_base)

        archivos = {
            "bom_json": cot_dir / "bom.json",
            "bom_md": cot_dir / "bom.md",
            "bom_tex": cot_dir / "bom.tex",
        }

        try:
            _generar_comparativa(bom, cot_dir, proveedores)
            archivos["comparativa_json"] = cot_dir / "comparativa.json"
        except Exception as e:
            pass

        try:
            _generar_cotizacion_formal(bom, config, cot_dir)
            archivos["cotizacion_html"] = cot_dir / "cotizacion.html"
        except Exception as e:
            pass

        resumen = bom.get("resumen", {})
        costo = resumen.get("costo_total_soles", 0)

        return EtapaResultado(
            nombre="Cotizacion",
            exitoso=True,
            mensaje=f"Presupuesto: S/ {costo:.2f}",
            archivos_generados={k: Path(v) if isinstance(v, str) else v for k, v in archivos.items()},
            datos=bom,
        )
    except Exception as e:
        return EtapaResultado(
            nombre="Cotizacion",
            exitoso=False,
            mensaje="Error en cotizacion",
            error=str(e),
        )


def _generar_comparativa(bom: Dict, output_dir: Path, proveedores: Optional[list[str]] = None) -> Dict:
    from electra.infraestructura.presupuestos.cotizador_multi_proveedor import (
        cargar_bom,
        construir_comparativa,
        generar_salidas,
        resumen_totales,
    )

    import tempfile
    import json
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(bom, f)
        bom_path = Path(f.name)

    try:
        raw_bom, materiales = cargar_bom(bom_path, max_materiales=None)
        comparativas = construir_comparativa(materiales, proveedores or None, output_dir)
        resumen = resumen_totales(comparativas)
        generar_salidas(comparativas, raw_bom, resumen, output_dir)

        comp_path = output_dir / "comparativa.json"
        with open(comp_path, "w", encoding="utf-8") as f:
            json.dump({"resumen": resumen, "materiales_count": len(comparativas)}, f, indent=2)

        return resumen
    finally:
        bom_path.unlink(missing_ok=True)


def _generar_cotizacion_formal(bom: Dict, config: Dict, output_dir: Path) -> str:
    from electra.infraestructura.presupuestos.generar_cotizacion import (
        DEFAULT_EMPRESA,
        generar_cotizacion_html,
    )

    empresa = {
        "nombre": config.get("empresa_nombre", DEFAULT_EMPRESA["nombre"]),
        "ruc": config.get("empresa_ruc", DEFAULT_EMPRESA["ruc"]),
        "direccion": config.get("empresa_direccion", DEFAULT_EMPRESA["direccion"]),
        "telefono": config.get("empresa_telefono", DEFAULT_EMPRESA["telefono"]),
        "email": config.get("empresa_email", DEFAULT_EMPRESA["email"]),
    }

    html_path = output_dir / "cotizacion.html"
    generar_cotizacion_html(bom, empresa, config.get("propietario", "Cliente"), str(html_path))
    return str(html_path)
