#!/usr/bin/env python3
"""Conector Promart Peru."""

from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List
from urllib.parse import quote, urljoin

import httpx
from bs4 import BeautifulSoup

from modelos import ResultadoProveedor
from .base import DEFAULT_HEADERS, ProveedorBase, parse_precio


class PromartProveedor(ProveedorBase):
    nombre = "Promart"
    slug = "promart"
    base_url = "https://www.promart.pe"
    search_url_template = "https://www.promart.pe/search?q={q}"
    prioridad = 0.82

    def buscar(self, query: str, max_resultados: int = 5) -> List[ResultadoProveedor]:
        api_url = f"{self.base_url}/api/catalog_system/pub/products/search?ft={quote(query)}"
        self.last_html = None
        self.last_url = api_url
        self.last_status = None
        self.last_error = None
        self.last_requested_url = api_url
        self.last_redirected = False
        self.last_state = "pendiente_manual"
        self.last_method = "api_vtex"
        self.request_history = []
        try:
            with httpx.Client(
                headers={**DEFAULT_HEADERS, "Accept": "application/json,text/html,*/*"},
                follow_redirects=True,
                timeout=httpx.Timeout(self.timeout, connect=min(self.timeout, 8.0)),
            ) as client:
                response = client.get(api_url)
            self.last_status = response.status_code
            self.last_url = str(response.url)
            self.last_html = response.text
            self.last_redirected = bool(response.history) or self.last_url.rstrip("/") != api_url.rstrip("/")
            time.sleep(max(0.0, self.delay))
            if response.status_code < 400 and "application/json" in response.headers.get("content-type", ""):
                data = response.json()
                resultados = self._parse_api_products(data, query)[:max_resultados]
                if resultados:
                    self.last_state = "ok_precio" if any(r.precio is not None for r in resultados) else "ok_sin_precio"
                    self._registrar_intento(api_url, response, "api_vtex", len(resultados), self.last_state)
                    return resultados
            return super().buscar(query, max_resultados)
        except Exception as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            return super().buscar(query, max_resultados)

    def parsear_resultados(self, html: str, query: str) -> List[ResultadoProveedor]:
        resultados = self.parse_json_ld(html, query)
        resultados.extend(self._parse_vtex_scripts(html, query))
        resultados.extend(self.parse_selectores_genericos(
            html,
            query,
            card_selectors=[
                "li[layout]", ".prateleira li", ".product-shelf li",
                ".shelf-item", ".product-card", ".vtex-product-summary-2-x-container",
            ],
            title_selectors=[
                ".product-name", ".productName", ".vtex-product-summary-2-x-productBrand",
                "a[title]", "h2", "h3",
            ],
            price_selectors=[
                ".best-price", ".price", ".product-price", ".vtex-product-price-1-x-sellingPrice",
                "[data-price]",
            ],
            link_selectors=["a[href]"],
        ))
        return deduplicar(resultados)

    def _parse_api_products(self, data: Any, query: str) -> List[ResultadoProveedor]:
        resultados: List[ResultadoProveedor] = []
        if not isinstance(data, list):
            return resultados
        for product in data:
            if not isinstance(product, dict):
                continue
            nombre = product.get("productName") or product.get("productTitle")
            marca = product.get("brand")
            link = product.get("link")
            precio = None
            disponibilidad = "no especificada"
            unidad = None
            for item in product.get("items", []) or []:
                unidad = item.get("measurementUnit") or unidad
                for seller in item.get("sellers", []) or []:
                    offer = seller.get("commertialOffer", {}) or {}
                    price = parse_precio(offer.get("Price"))
                    if price is not None:
                        precio = price if precio is None else min(precio, price)
                    if offer.get("IsAvailable") is True:
                        disponibilidad = f"disponible ({offer.get('AvailableQuantity', 'stock no especificado')})"
                    elif offer.get("IsAvailable") is False:
                        disponibilidad = "sin stock"
            if nombre:
                resultados.append(self.resultado(
                    query=query,
                    producto=nombre,
                    precio=precio,
                    url=link or self.last_url,
                    marca=marca,
                    disponibilidad=disponibilidad,
                    metodo="api",
                    confianza=0.88 if precio is not None else 0.55,
                    observaciones="Extraido de endpoint publico VTEX de Promart",
                    unidad_detectada=unidad,
                ))
        return resultados

    def _parse_vtex_scripts(self, html: str, query: str) -> List[ResultadoProveedor]:
        resultados: List[ResultadoProveedor] = []
        soup = BeautifulSoup(html or "", "lxml")
        for script in soup.find_all("script"):
            raw = script.string or script.get_text("", strip=False)
            if not raw:
                continue
            if "productName" not in raw and "items" not in raw and "skus" not in raw:
                continue
            for obj in extraer_objetos_json(raw):
                for product in iter_productos_vtex(obj):
                    nombre = product.get("productName") or product.get("name") or product.get("productTitle")
                    link = product.get("link") or product.get("productLink") or product.get("url")
                    precio = (
                        product.get("price")
                        or product.get("sellingPrice")
                        or product.get("bestPrice")
                        or product.get("Price")
                    )
                    precio_val = parse_precio(precio)
                    if not precio_val:
                        precio_val = parse_precio(json.dumps(product, ensure_ascii=False)[:1200])
                    if nombre:
                        resultados.append(self.resultado(
                            query=query,
                            producto=nombre,
                            precio=precio_val,
                            url=urljoin(self.base_url, link) if link else self.last_url,
                            marca=product.get("brand") or product.get("productBrand"),
                            disponibilidad=product.get("availability"),
                            metodo="json",
                            confianza=0.70 if precio_val else 0.45,
                            observaciones="Extraido de datos VTEX embebidos",
                        ))
        return resultados


def extraer_objetos_json(texto: str) -> List[Any]:
    objetos: List[Any] = []
    for match in re.finditer(r"(\{[^{}]{20,}\}|\[[^\[\]]{20,}\])", texto):
        raw = match.group(0)
        if not any(k in raw for k in ("productName", "sellingPrice", "items", "skus")):
            continue
        try:
            objetos.append(json.loads(raw))
        except Exception:
            continue
    return objetos


def iter_productos_vtex(data: Any):
    if isinstance(data, dict):
        if any(k in data for k in ("productName", "productTitle", "sellingPrice", "bestPrice")):
            yield data
        for val in data.values():
            yield from iter_productos_vtex(val)
    elif isinstance(data, list):
        for item in data:
            yield from iter_productos_vtex(item)


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
