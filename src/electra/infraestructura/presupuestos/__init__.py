"""Presupuestos — adaptadores multi-proveedor para cotización de materiales eléctricos.

Este módulo implementa el sistema de cotización multi-proveedor que busca,
compara y recomienda precios de materiales eléctricos desde múltiples
tiendas online peruanas (Promart, Sodimac, Maestro, Mercado Libre, Ventas Perú).
"""

from __future__ import annotations

from .modelos import ComparativaItem, MaterialBOM, ResultadoProveedor
from .normalizador_materiales import (
    comparar_specs,
    detectar_categoria,
    extraer_especificaciones,
    normalizar_nombre_material,
    score_tecnico,
)
from .conversor_unidades import (
    calcular_compra_comercial,
    detectar_unidad_comercial,
    extraer_contenido_comercial,
    normalizar_unidad,
)
from .cotizador_multi_proveedor import (
    cargar_bom,
    construir_comparativa,
    generar_salidas,
    resumen_totales,
)
from .bom_precios import generar_bom
from .proveedores import PROVEEDORES_DISPONIBLES

__all__ = [
    "generar_bom",
    "MaterialBOM",
    "ResultadoProveedor",
    "ComparativaItem",
    "normalizar_nombre_material",
    "detectar_categoria",
    "extraer_especificaciones",
    "comparar_specs",
    "score_tecnico",
    "calcular_compra_comercial",
    "detectar_unidad_comercial",
    "extraer_contenido_comercial",
    "normalizar_unidad",
    "cargar_bom",
    "construir_comparativa",
    "generar_salidas",
    "resumen_totales",
    "PROVEEDORES_DISPONIBLES",
]
