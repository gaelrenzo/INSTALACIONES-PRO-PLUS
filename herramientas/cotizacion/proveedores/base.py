#!/usr/bin/env python3
"""Base comun para conectores de proveedores."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import quote_plus, urljoin

import httpx
from bs4 import BeautifulSoup

from modelos import ResultadoProveedor


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
}


def ahora_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def parse_precio(texto: Any) -> Optional[float]:
    if texto is None:
        return None
    if isinstance(texto, (int, float)):
        val = float(texto)
        return round(val, 2) if 0.05 <= val <= 100000 else None
    s = str(texto)
    s = s.replace("\xa0", " ")
    patrones = [
        r"S/\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{1,2})?)",
        r"([0-9]{1,3}(?:[.,][0-9]{3})+(?:[.,][0-9]{1,2})?)",
        r"\b([0-9]+[.,][0-9]{1,2})\b",
    ]
    for patron in patrones:
        for raw in re.findall(patron, s):
            val = normalizar_numero(raw)
            if val is not None and 0.05 <= val <= 100000:
                return round(val, 2)
    return None


def normalizar_numero(raw: str) -> Optional[float]:
    raw = raw.strip().replace(" ", "")
    if not raw:
        return None
    if "," in raw and "." in raw:
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif "," in raw:
        parts = raw.split(",")
        if len(parts[-1]) <= 2:
            raw = raw.replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif raw.count(".") > 1:
        raw = raw.replace(".", "")
    try:
        return float(raw)
    except ValueError:
        return None


def compactar(texto: str) -> str:
    return re.sub(r"\s+", " ", texto or "").strip()


def buscar_marca(texto: str) -> Optional[str]:
    marcas = [
        "Indeco", "Pavco", "Wavin", "Bticino", "Legrand", "Schneider",
        "Siemens", "Eaton", "3M", "Philips", "Opalux", "Kobrex",
        "Celima", "Kroton", "Promelsa", "Sica", "Veto",
    ]
    for marca in marcas:
        if re.search(rf"\b{re.escape(marca)}\b", texto or "", re.I):
            return marca
    return None


class ProveedorBase:
    nombre = ""
    slug = ""
    base_url = ""
    search_url_template = ""
    prioridad = 0.70

    def __init__(self, timeout: float = 12.0, delay: float = 1.0) -> None:
        self.timeout = timeout
        self.delay = delay
        self.last_html: Optional[str] = None
        self.last_url: Optional[str] = None
        self.last_status: Optional[int] = None
        self.last_error: Optional[str] = None
        self.last_requested_url: Optional[str] = None
        self.last_redirected: bool = False
        self.last_state: str = "pendiente_manual"
        self.last_method: str = "httpx"
        self.request_history: List[Dict[str, Any]] = []

    def build_search_url(self, query: str) -> str:
        return self.search_url_template.format(q=quote_plus(query))

    def buscar(self, query: str, max_resultados: int = 5) -> List[ResultadoProveedor]:
        url = self.build_search_url(query)
        self.last_html = None
        self.last_url = url
        self.last_status = None
        self.last_error = None
        self.last_requested_url = url
        self.last_redirected = False
        self.last_state = "pendiente_manual"
        self.last_method = "httpx_html"
        self.request_history = []

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
            time.sleep(max(0.0, self.delay))
            if response.status_code >= 400:
                self.last_state = "bloqueado" if response.status_code in {401, 403, 429} else "parser_fallo"
                self._registrar_intento(url, response, self.last_method, 0, self.last_state)
                return [self.resultado_fallback(
                    query,
                    self.last_url,
                    f"HTTP {response.status_code}; no se extrajo precio",
                    metodo="fallback",
                    estado=self.last_state,
                )]
            resultados = self.parsear_resultados(response.text, query)[:max_resultados]
            if resultados:
                self.last_state = "ok_precio" if any(r.precio is not None for r in resultados) else "ok_sin_precio"
                self._registrar_intento(url, response, self.last_method, len(resultados), self.last_state)
                return resultados
            self.last_state = "redirect_no_util" if self.last_redirected else "html_sin_productos"
            self._registrar_intento(url, response, self.last_method, 0, self.last_state)
            return [self.resultado_fallback(
                query,
                self.last_url,
                "No se encontraron productos/precios confiables en HTML",
                metodo="html",
                estado=self.last_state,
            )]
        except httpx.TimeoutException as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            self.last_state = "timeout"
            self._registrar_error(url, self.last_method, self.last_state, self.last_error)
            return [self.resultado_fallback(query, url, self.last_error, metodo="fallback", estado="timeout")]
        except Exception as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            self.last_state = "parser_fallo"
            self._registrar_error(url, self.last_method, self.last_state, self.last_error)
            return [self.resultado_fallback(query, url, self.last_error, metodo="fallback", estado="parser_fallo")]

    def _registrar_intento(
        self,
        requested_url: str,
        response: httpx.Response,
        metodo: str,
        resultados_crudos: int,
        estado: str,
    ) -> None:
        texto = response.text or ""
        self.request_history.append({
            "url_solicitada": requested_url,
            "url_final": str(response.url),
            "codigo_http": response.status_code,
            "hubo_redirect": bool(response.history) or str(response.url).rstrip("/") != requested_url.rstrip("/"),
            "timeout": False,
            "bloqueo": estado == "bloqueado",
            "html_tiene_productos": any(x in texto.lower() for x in ("product", "producto", "pod-display")),
            "html_tiene_json": "application/ld+json" in texto or "__NEXT_DATA__" in texto,
            "metodo": metodo,
            "resultados_crudos": resultados_crudos,
            "estado": estado,
            "motivo": "",
        })

    def _registrar_error(self, url: str, metodo: str, estado: str, motivo: str) -> None:
        self.request_history.append({
            "url_solicitada": url,
            "url_final": url,
            "codigo_http": None,
            "hubo_redirect": False,
            "timeout": estado == "timeout",
            "bloqueo": estado == "bloqueado",
            "html_tiene_productos": False,
            "html_tiene_json": False,
            "metodo": metodo,
            "resultados_crudos": 0,
            "estado": estado,
            "motivo": motivo,
        })

    def parsear_resultados(self, html: str, query: str) -> List[ResultadoProveedor]:
        raise NotImplementedError

    def resultado_fallback(
        self,
        query: str,
        url: str,
        observaciones: str,
        metodo: str = "fallback",
        estado: str = "pendiente_manual",
        tipo_enlace: str = "busqueda",
    ) -> ResultadoProveedor:
        return ResultadoProveedor(
            proveedor=self.nombre,
            proveedor_slug=self.slug,
            consulta=query,
            producto=None,
            marca=None,
            precio=None,
            url=url,
            disponibilidad="no extraido",
            fecha_consulta=ahora_iso(),
            metodo_extraccion=metodo,
            confianza=0.05,
            observaciones=observaciones,
            estado_proveedor=estado,
            url_solicitada=self.last_requested_url or url,
            url_final=self.last_url or url,
            tipo_enlace=tipo_enlace,
            codigo_http=self.last_status,
            hubo_redirect=self.last_redirected,
            motivo_fallo=observaciones,
            score_proveedor=self.prioridad,
        )

    def resultado(
        self,
        query: str,
        producto: Optional[str],
        precio: Optional[float],
        url: Optional[str],
        marca: Optional[str] = None,
        disponibilidad: Optional[str] = None,
        metodo: str = "html",
        confianza: float = 0.5,
        observaciones: str = "",
        unidad_detectada: Optional[str] = None,
        vendedor: Optional[str] = None,
    ) -> ResultadoProveedor:
        producto = compactar(producto or "")
        marca = marca or buscar_marca(producto)
        return ResultadoProveedor(
            proveedor=self.nombre,
            proveedor_slug=self.slug,
            consulta=query,
            producto=producto or None,
            vendedor=vendedor,
            marca=marca,
            precio=precio,
            moneda="PEN",
            unidad_detectada=unidad_detectada,
            url=url,
            disponibilidad=disponibilidad or "no especificada",
            fecha_consulta=ahora_iso(),
            metodo_extraccion=metodo,
            confianza=max(0.0, min(1.0, confianza)),
            observaciones=observaciones,
            estado_proveedor="ok_precio" if precio is not None else "ok_sin_precio",
            url_solicitada=self.last_requested_url,
            url_final=self.last_url,
            tipo_enlace="producto" if producto and url else "busqueda",
            codigo_http=self.last_status,
            hubo_redirect=self.last_redirected,
            score_proveedor=self.prioridad,
        )

    def parse_json_ld(self, html: str, query: str) -> List[ResultadoProveedor]:
        soup = BeautifulSoup(html or "", "lxml")
        resultados: List[ResultadoProveedor] = []
        for script in soup.select('script[type="application/ld+json"]'):
            raw = script.string or script.get_text("", strip=True)
            if not raw:
                continue
            try:
                data = json.loads(raw)
            except Exception:
                continue
            for item in self.iter_productos_json(data):
                producto = item.get("name") or item.get("title")
                offers = item.get("offers") or {}
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                precio = parse_precio(
                    offers.get("price")
                    or offers.get("lowPrice")
                    or item.get("price")
                    or item.get("priceAmount")
                )
                url = item.get("url") or offers.get("url")
                if url:
                    url = urljoin(self.base_url, url)
                if producto:
                    resultados.append(self.resultado(
                        query=query,
                        producto=producto,
                        precio=precio,
                        url=url or self.last_url or self.build_search_url(query),
                        marca=item.get("brand", {}).get("name") if isinstance(item.get("brand"), dict) else item.get("brand"),
                        disponibilidad=offers.get("availability") or item.get("availability"),
                        metodo="json",
                        confianza=0.75 if precio else 0.55,
                        observaciones="Extraido de JSON-LD",
                    ))
        return resultados

    def iter_productos_json(self, data: Any) -> Iterable[Dict[str, Any]]:
        if isinstance(data, dict):
            typ = data.get("@type") or data.get("type")
            if typ == "Product" or (isinstance(typ, list) and "Product" in typ):
                yield data
            for key in ("itemListElement", "items", "products", "results"):
                val = data.get(key)
                if val:
                    yield from self.iter_productos_json(val)
            item = data.get("item")
            if item:
                yield from self.iter_productos_json(item)
        elif isinstance(data, list):
            for x in data:
                yield from self.iter_productos_json(x)

    def parse_selectores_genericos(
        self,
        html: str,
        query: str,
        card_selectors: List[str],
        title_selectors: List[str],
        price_selectors: List[str],
        link_selectors: List[str],
        max_items: int = 10,
    ) -> List[ResultadoProveedor]:
        soup = BeautifulSoup(html or "", "lxml")
        resultados: List[ResultadoProveedor] = []
        cards = []
        for selector in card_selectors:
            cards = soup.select(selector)
            if cards:
                break

        for card in cards[:max_items]:
            producto = first_text(card, title_selectors)
            precio = parse_precio(first_text(card, price_selectors) or card.get_text(" ", strip=True))
            link = first_attr(card, link_selectors, "href")
            if link:
                link = urljoin(self.base_url, link)
            if producto or precio:
                resultados.append(self.resultado(
                    query=query,
                    producto=producto,
                    precio=precio,
                    url=link or self.last_url or self.build_search_url(query),
                    metodo="html",
                    confianza=0.65 if precio and producto else 0.35,
                    observaciones="Extraido con selectores HTML",
                ))
        return resultados


def first_text(node: Any, selectors: List[str]) -> Optional[str]:
    for selector in selectors:
        found = node.select_one(selector)
        if found:
            txt = compactar(found.get_text(" ", strip=True))
            if txt:
                return txt
    return None


def first_attr(node: Any, selectors: List[str], attr: str) -> Optional[str]:
    for selector in selectors:
        found = node.select_one(selector)
        if found and found.get(attr):
            return found.get(attr)
    if node.name == "a" and node.get(attr):
        return node.get(attr)
    return None
