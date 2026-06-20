#!/usr/bin/env python3
"""Conector Maestro Peru."""

from __future__ import annotations

from typing import List

from modelos import ResultadoProveedor
from .sodimac import SodimacProveedor


class MaestroProveedor(SodimacProveedor):
    nombre = "Maestro"
    slug = "maestro"
    base_url = "https://www.maestro.com.pe"
    search_url_template = "https://www.maestro.com.pe/maestro-pe/search?Ntt={q}"
    prioridad = 0.78
    expected_sellers = {"MAESTRO"}

    def parsear_resultados(self, html: str, query: str) -> List[ResultadoProveedor]:
        resultados = super().parsear_resultados(html, query)
        for resultado in resultados:
            resultado.proveedor = self.nombre
            resultado.score_proveedor = self.prioridad
        return resultados
