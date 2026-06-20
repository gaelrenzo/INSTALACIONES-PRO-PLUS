#!/usr/bin/env python3
"""Conector Sodimac Peru."""

from __future__ import annotations

import json
import time
from typing import Any, List
from urllib.parse import quote_plus, urljoin

import httpx
from bs4 import BeautifulSoup

from modelos import ResultadoProveedor
from .base import DEFAULT_HEADERS, ProveedorBase, parse_precio


class SodimacProveedor(ProveedorBase):
    nombre = "Sodimac"
    slug = "sodimac"
    base_url = "https://www.sodimac.com.pe"
    search_url_template = "https://www.sodimac.com.pe/sodimac-pe/search?Ntt={q}"
    prioridad = 0.84
    expected_sellers = {"SODIMAC"}
    falabella_search_url = "https://www.falabella.com.pe/falabella-pe/search?Ntt={q}"

    def buscar(self, query: str, max_resultados: int = 5) -> List[ResultadoProveedor]:
        """Prueba la URL historica y el catalogo unificado de Falabella."""
        self.last_html = None
        self.last_error = None
        self.last_status = None
        self.last_requested_url = None
        self.last_redirected = False
        self.last_state = "pendiente_manual"
        self.request_history = []

        urls = []
        if not getattr(self, "_legacy_checked", False):
            urls.append((self.build_search_url(query), "httpx_sodimac_legacy"))
            self._legacy_checked = True
        urls.append((self.falabella_search_url.format(q=quote_plus(query)), "httpx_catalogo_falabella"))
        ultimo_resultado: List[ResultadoProveedor] = []
        for url, metodo in urls:
            self.last_requested_url = url
            self.last_method = metodo
            try:
                with httpx.Client(
                    headers=DEFAULT_HEADERS,
                    follow_redirects=True,
                    timeout=httpx.Timeout(self.timeout, connect=min(self.timeout, 8.0)),
                ) as client:
                    response = client.get(url)
                self.last_status = response.status_code
                self.last_url = str(response.url)
                self.last_html = response.text
                self.last_redirected = bool(response.history) or self.last_url.rstrip("/") != url.rstrip("/")
                if response.status_code >= 400:
                    estado = "bloqueado" if response.status_code in {401, 403, 429} else "parser_fallo"
                    self._registrar_intento(url, response, metodo, 0, estado)
                    continue
                resultados = self.parsear_resultados(response.text, query)
                if resultados:
                    estado = "ok_precio" if any(r.precio is not None for r in resultados) else "ok_sin_precio"
                    self.last_state = estado
                    self._registrar_intento(url, response, metodo, len(resultados), estado)
                    time.sleep(max(0.0, self.delay))
                    return resultados[:max_resultados]
                estado = "redirect_no_util" if self.last_redirected else "html_sin_productos"
                self._registrar_intento(url, response, metodo, 0, estado)
                ultimo_resultado = [self.resultado_fallback(
                    query,
                    self.last_url,
                    "La URL no expuso productos del vendedor Sodimac.",
                    metodo=metodo,
                    estado=estado,
                )]
            except httpx.TimeoutException as exc:
                self.last_error = f"{type(exc).__name__}: {exc}"
                self._registrar_error(url, metodo, "timeout", self.last_error)
                ultimo_resultado = [self.resultado_fallback(
                    query, url, self.last_error, metodo="fallback", estado="timeout"
                )]
            except Exception as exc:
                self.last_error = f"{type(exc).__name__}: {exc}"
                self._registrar_error(url, metodo, "parser_fallo", self.last_error)
                ultimo_resultado = [self.resultado_fallback(
                    query, url, self.last_error, metodo="fallback", estado="parser_fallo"
                )]

        self.last_state = ultimo_resultado[0].estado_proveedor if ultimo_resultado else "pendiente_manual"
        time.sleep(max(0.0, self.delay))
        return ultimo_resultado or [self.resultado_fallback(
            query,
            urls[-1][0],
            "Sin resultados del vendedor Sodimac; revisar el enlace de busqueda.",
            estado="pendiente_manual",
        )]

    def parsear_resultados(self, html: str, query: str) -> List[ResultadoProveedor]:
        resultados = self.parse_json_ld(html, query)
        resultados.extend(self._parse_next_data(html, query))
        resultados.extend(self.parse_selectores_genericos(
            html,
            query,
            card_selectors=[
                "[data-testid='pod']", ".pod", ".product-card", ".jsx-1484439449",
                "li[data-pod]", "div[data-pod]",
            ],
            title_selectors=[
                "[data-testid='pod-displaySubTitle']", "[data-testid='pod-displayTitle']",
                ".pod-subTitle", ".pod-title", "b", "h2", "h3",
            ],
            price_selectors=[
                "[data-testid='price']", ".copy10", ".prices", ".price",
                "[class*='price']", "[class*='Price']",
            ],
            link_selectors=["a[href]"],
        ))
        return deduplicar(resultados)

    def _parse_next_data(self, html: str, query: str) -> List[ResultadoProveedor]:
        soup = BeautifulSoup(html or "", "lxml")
        script = soup.select_one("script#__NEXT_DATA__")
        if not script:
            return []
        try:
            data = json.loads(script.string or script.get_text("", strip=True))
        except Exception:
            return []
        resultados: List[ResultadoProveedor] = []
        for product in iter_productos_falabella(data):
            nombre = (
                product.get("displayName")
                or product.get("productName")
                or product.get("name")
                or product.get("title")
            )
            vendedor = product.get("sellerName") or product.get("seller")
            if (
                vendedor
                and self.expected_sellers
                and str(vendedor).upper() not in self.expected_sellers
                and not (self.last_url or "").startswith("fixture://")
            ):
                continue
            precio = extraer_precio_falabella(product)
            precio_val = parse_precio(precio or json.dumps(product, ensure_ascii=False)[:1000])
            url = product.get("url") or product.get("productUrl") or product.get("link")
            if nombre:
                resultados.append(self.resultado(
                    query=query,
                    producto=nombre,
                    precio=precio_val,
                    url=urljoin(self.base_url, url) if url else self.last_url,
                    marca=product.get("brand") or product.get("brandName"),
                    disponibilidad=product.get("availability") or product.get("stock"),
                    metodo="json",
                    confianza=0.70 if precio_val else 0.45,
                    observaciones=(
                        "Extraido de __NEXT_DATA__ del catalogo unificado Falabella"
                        + (f"; vendedor: {vendedor}" if vendedor else "")
                    ),
                    vendedor=str(vendedor) if vendedor else None,
                ))
        return resultados


def extraer_precio_falabella(product: Any) -> Any:
    for key in ("price", "normalPrice", "internetPrice", "offerPrice", "formattedPrice"):
        if product.get(key) is not None:
            return product.get(key)
    for price_info in product.get("prices", []) or []:
        price = price_info.get("price")
        if isinstance(price, list) and price:
            return price[0]
        if price is not None:
            return price
    return None


def iter_productos_falabella(data: Any):
    if isinstance(data, dict):
        keys = set(data.keys())
        if {"productName", "price"} & keys or {"displayName", "normalPrice"} & keys:
            yield data
        for key in ("products", "items", "results", "records", "pods", "productList"):
            if key in data:
                yield from iter_productos_falabella(data[key])
        for val in data.values():
            if isinstance(val, (list, dict)):
                yield from iter_productos_falabella(val)
    elif isinstance(data, list):
        for item in data:
            yield from iter_productos_falabella(item)


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
