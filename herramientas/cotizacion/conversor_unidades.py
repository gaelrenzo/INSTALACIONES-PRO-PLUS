#!/usr/bin/env python3
"""Conversion entre unidades de diseno del BOM y empaques comerciales."""

from __future__ import annotations

import json
import math
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


BASE_DIR = Path(__file__).resolve().parent
REGLAS_PATH = BASE_DIR / "data" / "unidades_comerciales.json"

_reglas_cache: Optional[Dict[str, Any]] = None

UNIDADES_UNIDAD = {"u", "un", "und", "unidad", "unidades", "pieza", "piezas"}
UNIDADES_METRO = {"m", "mt", "mts", "metro", "metros"}


def cargar_reglas_unidades() -> Dict[str, Any]:
    global _reglas_cache
    if _reglas_cache is None:
        try:
            _reglas_cache = json.loads(REGLAS_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _reglas_cache = {"categorias": {}}
    return _reglas_cache


def limpiar_nombre(texto: str) -> str:
    texto = "".join(
        c
        for c in unicodedata.normalize("NFKD", texto or "")
        if not unicodedata.combining(c)
    )
    texto = texto.lower().replace("²", "2")
    return re.sub(r"\s+", " ", texto).strip()


def normalizar_unidad(unidad: Optional[str]) -> str:
    unidad_limpia = limpiar_nombre(unidad or "")
    if unidad_limpia in UNIDADES_UNIDAD:
        return "unidad"
    if unidad_limpia in UNIDADES_METRO:
        return "m"
    if unidad_limpia in {"rollos", "bobina", "bobinas", "carrete", "carretes"}:
        return "rollo"
    if unidad_limpia in {"tubos", "barra", "barras", "tramo", "tramos"}:
        return "tubo"
    if unidad_limpia in {"paquetes", "pack", "packs", "bolsa", "bolsas", "caja", "cajas"}:
        return "paquete"
    return unidad_limpia or "unidad"


def _regla_categoria(titulo: str, categoria: str) -> Dict[str, Any]:
    regla = cargar_reglas_unidades().get("categorias", {}).get(categoria, {})
    if categoria != "puesta a tierra" or not regla:
        return regla

    subcategoria = ""
    if any(x in titulo for x in ("varilla", "electrodo", "jabalina")):
        subcategoria = "varilla"
    elif any(x in titulo for x in ("cable", "conductor", "alambre")):
        subcategoria = "conductor"
    elif any(x in titulo for x in ("caja", "registro")):
        subcategoria = "caja registro"
    elif any(x in titulo for x in ("conector", "abrazadera", "grampa")):
        subcategoria = "conector"
    return regla.get("subcategorias", {}).get(subcategoria, regla)


def detectar_unidad_comercial(titulo_producto: str, categoria: str) -> str:
    titulo = limpiar_nombre(titulo_producto)
    regla = _regla_categoria(titulo, categoria)
    posibles = regla.get("unidades_comerciales_posibles", [])

    detectores = (
        ("rollo", ("rollo", "carrete", "bobina")),
        ("tubo", ("tubo", "barra", "tramo")),
        ("paquete", ("paquete", "pack", "bolsa", "caja de ")),
        ("m", ("por metro", "/m", "metro lineal")),
        ("unidad", ("unidad", " und", "pieza")),
    )
    posibles_norm = {normalizar_unidad(x) for x in posibles}
    for unidad, palabras in detectores:
        if unidad in posibles_norm and any(palabra in titulo for palabra in palabras):
            return unidad

    unidad_diseno = normalizar_unidad(regla.get("unidad_diseno"))
    if unidad_diseno == "m" and "m" in posibles_norm:
        return "m"
    if "unidad" in posibles_norm:
        return "unidad"
    return next(iter(posibles_norm), "unidad")


def extraer_contenido_comercial(
    titulo_producto: str,
    categoria: str,
) -> Tuple[float, str, float, str]:
    """Retorna contenido, unidad de contenido, confianza y observacion."""
    titulo = limpiar_nombre(titulo_producto)
    regla = _regla_categoria(titulo, categoria)
    if not regla:
        return 1.0, "unidad", 0.0, "falta regla de conversion comercial"

    unidad_diseno = normalizar_unidad(regla.get("unidad_diseno"))
    for patron in regla.get("patrones_extraccion", []):
        coincidencia = re.search(patron, titulo, flags=re.I)
        if not coincidencia:
            continue
        try:
            valor = float(coincidencia.group(1).replace(",", "."))
        except (ValueError, IndexError):
            continue
        if valor > 0:
            descriptor = "m" if unidad_diseno == "m" else "unidades"
            return (
                valor,
                unidad_diseno,
                1.0,
                f"Precio convertido desde empaque comercial de {valor:g} {descriptor}.",
            )

    unidad_comercial = detectar_unidad_comercial(titulo, categoria)
    if unidad_comercial in {"unidad", "m"}:
        return 1.0, unidad_diseno, 1.0, "Venta directa 1:1 con la unidad de diseno."

    if regla.get("asumir_si_no_encontrado", False):
        asumido = regla.get("longitud_asumida", regla.get("contenido_asumido", 1.0))
        observacion = regla.get("observacion_asumida", "contenido comercial asumido, revisar")
        confianza = 0.8 if not regla.get("requiere_longitud_explicita", False) else 0.5
        return float(asumido), unidad_diseno, confianza, observacion

    if regla.get("requiere_longitud_explicita", False):
        return (
            1.0,
            unidad_diseno,
            0.0,
            "Unidad comercial detectada, pero el titulo no indica su contenido; revisar.",
        )
    return 1.0, unidad_diseno, 0.7, "Conversion comercial 1:1 asumida."


def calcular_precio_equivalente(precio_producto: float, contenido_comercial: float) -> float:
    if precio_producto is None or precio_producto <= 0 or contenido_comercial <= 0:
        return 0.0
    return float(precio_producto) / float(contenido_comercial)


def calcular_sobrante(
    cantidad_bom: float,
    cantidad_comercial: float,
    contenido_comercial: float,
) -> float:
    return max(0.0, cantidad_comercial * contenido_comercial - cantidad_bom)


def marcar_confianza_conversion(
    unidad_bom: str,
    unidad_comercial: str,
    contenido_comercial: float,
    confianza_extraida: float,
) -> float:
    if contenido_comercial <= 0:
        return 0.0
    unidad_bom_norm = normalizar_unidad(unidad_bom)
    unidad_comercial_norm = normalizar_unidad(unidad_comercial)
    if unidad_bom_norm == "m" and unidad_comercial_norm in {"rollo", "tubo", "paquete"}:
        return max(0.0, min(1.0, confianza_extraida))
    if unidad_bom_norm == "unidad" and unidad_comercial_norm in {"unidad", "paquete", "rollo"}:
        return max(0.0, min(1.0, confianza_extraida))
    if unidad_bom_norm == unidad_comercial_norm:
        return max(0.0, min(1.0, confianza_extraida))
    return min(0.4, max(0.0, confianza_extraida))


def calcular_compra_comercial(
    cantidad_bom: float,
    unidad_bom: str,
    precio_producto: float,
    unidad_comercial: str,
    contenido_comercial: float,
) -> Tuple[float, float, float, float]:
    """Retorna cantidad comercial, subtotal real, sobrante y precio equivalente."""
    if precio_producto is None or precio_producto <= 0:
        return 0.0, 0.0, 0.0, 0.0
    cantidad_bom = max(0.0, float(cantidad_bom))
    contenido_comercial = float(contenido_comercial or 1.0)
    if contenido_comercial <= 0:
        contenido_comercial = 1.0

    cantidad_comercial = math.ceil(cantidad_bom / contenido_comercial)
    subtotal = cantidad_comercial * float(precio_producto)
    sobrante = calcular_sobrante(cantidad_bom, cantidad_comercial, contenido_comercial)
    precio_equivalente = calcular_precio_equivalente(precio_producto, contenido_comercial)
    return (
        float(cantidad_comercial),
        float(subtotal),
        float(sobrante),
        float(precio_equivalente),
    )
