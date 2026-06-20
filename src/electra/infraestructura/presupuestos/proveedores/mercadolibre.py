#!/usr/bin/env python3
"""Conector Mercado Libre Peru."""

from __future__ import annotations

import time
from typing import List
from urllib.parse import quote, quote_plus, urljoin

import httpx

from ..modelos import ResultadoProveedor
from .base import DEFAULT_HEADERS, ProveedorBase, parse_precio


class MercadoLibreProveedor(ProveedorBase):
    nombre = "Mercado Libre"
    slug = "mercadolibre"
    base_url = "https://www.mercadolibre.com.pe"
    search_url_template = "https://listado.mercadolibre.com.pe/{q}"
    prioridad = 0.68

    def build_search_url(self, query: str) -> str:
        return self.search_url_template.format(q=quote(query.replace(" ", "-")))

    def buscar(self, query: str, max_resultados: int = 5) -> List[ResultadoProveedor]:
        """Prueba API publica y HTML sin intentar evadir verificaciones."""
        self.last_html = None
        self.last_error = None
        self.last_status = None
        self.last_requested_url = None
        self.last_redirected = False
        self.last_state = "pendiente_manual"
        self.request_history = []

        api_url = f"https://api.mercadolibre.com/sites/MPE/search?q={quote_plus(query)}&limit={max_resultados}"
        try:
            response = httpx.get(
                api_url,
                headers={**DEFAULT_HEADERS, "Accept": "application/json"},
                follow_redirects=True,
                timeout=self.timeout,
            )
            self.last_requested_url = api_url
            self.last_status = response.status_code
            self.last_url = str(response.url)
            if response.status_code < 400:
                resultados = self._parse_api(response.json(), query)
                estado = "ok_precio" if any(r.precio is not None for r in resultados) else "ok_sin_precio"
                self._registrar_intento(api_url, response, "api_publica", len(resultados), estado)
                if resultados:
                    self.last_state = estado
                    return resultados[:max_resultados]
            else:
                estado = "bloqueado" if response.status_code in {401, 403, 429} else "parser_fallo"
                self._registrar_intento(api_url, response, "api_publica", 0, estado)
        except httpx.TimeoutException as exc:
            self._registrar_error(api_url, "api_publica", "timeout", f"{type(exc).__name__}: {exc}")
        except Exception as exc:
            self._registrar_error(api_url, "api_publica", "parser_fallo", f"{type(exc).__name__}: {exc}")

        search_url = self.build_search_url(query)
        self.last_requested_url = search_url
        try:
            response = httpx.get(
                search_url,
                headers=DEFAULT_HEADERS,
                follow_redirects=True,
                timeout=self.timeout,
            )
            self.last_status = response.status_code
            self.last_url = str(response.url)
            self.last_html = response.text
            self.last_redirected = bool(response.history) or self.last_url.rstrip("/") != search_url.rstrip("/")
            lower = response.text.lower()
            bloqueado = "suspicious-traffic" in lower or "account-verification" in lower
            if bloqueado:
                self.last_state = "bloqueado"
                self._registrar_intento(search_url, response, "httpx_html", 0, "bloqueado")
                return [self.resultado_fallback(
                    query,
                    search_url,
                    "Mercado Libre mostro verificacion de trafico; se conserva el enlace de busqueda y no se intento omitir el bloqueo.",
                    metodo="httpx_html",
                    estado="bloqueado",
                    tipo_enlace="busqueda",
                )]
            resultados = self.parsear_resultados(response.text, query)
            if resultados:
                estado = "ok_precio" if any(r.precio is not None for r in resultados) else "ok_sin_precio"
                self.last_state = estado
                self._registrar_intento(search_url, response, "httpx_html", len(resultados), estado)
                return resultados[:max_resultados]
            estado = "parser_fallo" if response.status_code < 400 else "bloqueado"
            self.last_state = estado
            self._registrar_intento(search_url, response, "httpx_html", 0, estado)
        except httpx.TimeoutException as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            self.last_state = "timeout"
            self._registrar_error(search_url, "httpx_html", "timeout", self.last_error)
        except Exception as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            self.last_state = "parser_fallo"
            self._registrar_error(search_url, "httpx_html", "parser_fallo", self.last_error)
        finally:
            time.sleep(max(0.0, self.delay))

        return [self.resultado_fallback(
            query,
            search_url,
            "Mercado Libre no expuso resultados parseables; revisar enlace de busqueda.",
            metodo="fallback",
            estado="pendiente_manual",
            tipo_enlace="busqueda",
        )]

    def _parse_api(self, data: object, query: str) -> List[ResultadoProveedor]:
        if not isinstance(data, dict):
            return []
        resultados: List[ResultadoProveedor] = []
        for item in data.get("results", []) or []:
            if not isinstance(item, dict):
                continue
            resultados.append(self.resultado(
                query=query,
                producto=item.get("title"),
                precio=parse_precio(item.get("price")),
                url=item.get("permalink"),
                disponibilidad="disponible" if item.get("available_quantity", 0) else "no especificada",
                metodo="api_publica",
                confianza=0.85 if item.get("price") else 0.55,
                observaciones="Extraido de API publica Mercado Libre",
                vendedor=(item.get("seller") or {}).get("nickname") if isinstance(item.get("seller"), dict) else None,
            ))
        return resultados

    def parsear_resultados(self, html: str, query: str) -> List[ResultadoProveedor]:
        lower = (html or "").lower()
        if "suspicious-traffic" in lower or "account-verification" in lower:
            return [self.resultado_fallback(
                query=query,
                url=self.last_url or self.build_search_url(query),
                observaciones=(
                    "Mercado Libre mostro verificacion de trafico; "
                    "no se intento omitir el bloqueo"
                ),
                metodo="fallback",
                estado="bloqueado",
            )]

        resultados = self.parse_json_ld(html, query)
        resultados.extend(self.parse_selectores_genericos(
            html,
            query,
            card_selectors=[
                "li.ui-search-layout__item", ".ui-search-result__wrapper",
                ".ui-search-result", ".poly-card",
            ],
            title_selectors=[
                ".poly-component__title", ".ui-search-item__title",
                "h2", "a[title]",
            ],
            price_selectors=[
                ".andes-money-amount", ".price-tag-fraction",
                ".ui-search-price__second-line", "[class*='price']",
            ],
            link_selectors=["a.poly-component__title", "a.ui-search-link", "a[href]"],
        ))
        for r in resultados:
            if r.url:
                r.url = urljoin(self.base_url, r.url)
        return deduplicar(resultados)


def deduplicar(resultados: List[ResultadoProveedor]) -> List[ResultadoProveedor]:
    vistos = set()
    out: List[ResultadoProveedor] = []
    for r in resultados:
        key = ((r.producto or "").lower(), r.url or "")
        if key in vistos:
            continue
        vistos.add(key)
        out.append(r)
    return out
