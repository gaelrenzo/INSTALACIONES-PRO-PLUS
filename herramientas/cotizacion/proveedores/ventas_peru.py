#!/usr/bin/env python3
"""Conector opcional Ventas Peru."""

from __future__ import annotations

from typing import List

from modelos import ResultadoProveedor
from .base import ProveedorBase


class VentasPeruProveedor(ProveedorBase):
    nombre = "Ventas Peru"
    slug = "ventas_peru"
    base_url = "https://www.ventas.pe"
    search_url_template = "https://www.ventas.pe/search?q={q}"
    prioridad = 0.55

    def parsear_resultados(self, html: str, query: str) -> List[ResultadoProveedor]:
        resultados = self.parse_json_ld(html, query)
        resultados.extend(self.parse_selectores_genericos(
            html,
            query,
            card_selectors=[".product", ".product-item", ".item", "article", "li"],
            title_selectors=[".product-title", ".title", "h2", "h3", "a[title]"],
            price_selectors=[".price", ".precio", "[class*='price']", "[class*='precio']"],
            link_selectors=["a[href]"],
        ))
        return resultados
