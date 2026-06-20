#!/usr/bin/env python3
"""
Buscador automatizado de precios de materiales electricos.

Genera una tabla comparativa con enlaces a Sodimac, Promart, MercadoLibre,
Maestro y Google Shopping para cada material del BOM.

Estrategias de automatizacion (en orden de confiabilidad):
  1) ENLACES DIRECTOS (siempre disponible) - Abres el link y ves el precio actual
  2) GOOGLE API (requiere --google-api-key) - Busqueda programatica en Google Shopping
  3) PRECIOS MANUALES (--precio) - Cargar precios conocidos desde terminal
  4) CACHE LOCAL (--cache) - Reusa precios de busquedas anteriores

Uso:
  python3 buscador_precios.py --item "cable TW 2.5mm2"
  python3 buscador_precios.py --bom output/bom.json --output comparativa
  python3 buscador_precios.py --bom output/bom.json --actualizar bom.json
  python3 buscador_precios.py --precio "cable TW 2.5mm2=12.50" --precio "ITM 2P 20A=45.00"
  python3 buscador_precios.py --bom output/bom.json --google-api-key AIza... --google-cx 123...
  python3 buscador_precios.py --item "cable TW 2.5mm2" --solo-enlaces
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import date
from pathlib import Path

CACHE_DEFAULT = os.path.expanduser("~/.cache_precios_electricos.json")


def fetch_url(url, max_bytes=300000, timeout=15):
    """Descarga contenido HTML de una URL."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read(max_bytes)
            charset = resp.headers.get_content_charset() or "utf-8"
            return content.decode(charset, errors="replace")
    except Exception:
        return None


def precio_desde_texto(texto):
    """Extrae el primer precio en S/ de un texto."""
    if not texto:
        return None
    nums = re.findall(r'S/[.\s]*(\d+[.,]\d*)', texto)
    for n in nums:
        try:
            val = float(n.replace(",", ""))
            if 0.5 < val < 50000:
                return round(val, 2)
        except ValueError:
            pass
    nums = re.findall(r'(\d+[.,]\d*)', texto)
    for n in nums:
        try:
            val = float(n.replace(",", ""))
            if 0.5 < val < 50000:
                return round(val, 2)
        except ValueError:
            pass
    return None


PROVEEDORES = {
    "sodimac": {
        "nombre": "Sodimac",
        "url": "https://www.sodimac.com.pe/sodimac-pe/search?q={q}",
    },
    "promart": {
        "nombre": "Promart",
        "url": "https://www.promart.pe/search?q={q}",
    },
    "mercadolibre": {
        "nombre": "Mercado Libre",
        "url": "https://listado.mercadolibre.com.pe/{q}",
    },
    "maestro": {
        "nombre": "Maestro",
        "url": "https://www.maestro.com.pe/maestro-pe/search?q={q}",
    },
    "google": {
        "nombre": "Google Shopping",
        "url": "https://www.google.com/search?q={q}+precio+Peru&tbm=shop",
    }
}

MODO_ENLACES = ["sodimac", "promart", "mercadolibre", "maestro", "google"]

MATERIALES_TIPICOS = [
    "cable TW 1.5mm2", "cable TW 2.5mm2", "cable TW 4mm2", "cable TW 6mm2",
    "cable TW 10mm2", "cable TW 16mm2", "cable TW 25mm2", "cable TW 35mm2",
    "cable NH-90 1.5mm2", "cable NH-90 2.5mm2", "cable NH-90 4mm2", "cable NH-90 6mm2",
    "cable NH-90 10mm2", "cable NH-90 16mm2",
    "tubo PVC SAP 20mm", "tubo PVC SAP 25mm", "tubo PVC SAP 35mm", "tubo PVC SAP 40mm",
    "curva PVC SAP 20mm", "curva PVC SAP 25mm", "curva PVC SAP 35mm",
    "union PVC SAP 20mm", "union PVC SAP 25mm", "union PVC SAP 35mm",
    "caja pase cuadrada 100x100", "caja pase rectangular 100x50",
    "caja octogonal", "caja rectangular 4x2",
    "interruptor termomagnetico 1P 10A", "interruptor termomagnetico 1P 16A",
    "interruptor termomagnetico 1P 20A", "interruptor termomagnetico 1P 32A",
    "interruptor termomagnetico 2P 10A", "interruptor termomagnetico 2P 16A",
    "interruptor termomagnetico 2P 20A", "interruptor termomagnetico 2P 32A",
    "interruptor termomagnetico 2P 40A", "interruptor termomagnetico 2P 63A",
    "interruptor termomagnetico 3P 32A", "interruptor termomagnetico 3P 40A",
    "interruptor termomagnetico 3P 63A",
    "diferencial 2P 25A 30mA", "diferencial 2P 40A 30mA", "diferencial 2P 63A 30mA",
    "diferencial 4P 25A 30mA", "diferencial 4P 40A 30mA", "diferencial 4P 63A 30mA",
    "tablero distribucion 4 circuitos", "tablero distribucion 8 circuitos",
    "tablero distribucion 12 circuitos", "tablero distribucion 16 circuitos",
    "tablero distribucion 24 circuitos",
    "varilla puesta a tierra 5/8x2.4m", "conector varilla tierra",
    "luminaria LED empotrar 12W", "luminaria LED empotrar 18W",
    "luminaria LED superficie 18W", "luminaria LED superficie 36W",
    "brazo LED 10W", "brazo LED 18W",
    "interruptor simple Bticino", "interruptor doble Bticino", "interruptor triple Bticino",
    "tomacorriente doble con tierra Bticino", "tomacorriente simple con tierra Bticino",
    "placa interruptor simple", "placa interruptor doble", "placa tomacorriente",
    "cinta aislante 3M", "conector de cable tipo bayoneta",
    "terminal de ojo 16mm2", "terminal de ojo 25mm2", "terminal de ojo 35mm2",
]


def normalizar_nombre(nombre):
    """Normaliza nombre de material para matching case-insensitive."""
    n = nombre.lower().strip()
    n = re.sub(r'[-/,_]', ' ', n)
    n = re.sub(r'\s+', ' ', n)
    n = n.replace("  ", " ").strip()
    n = re.sub(r'\b(thw|tw|nh[ -]?90|sap)\b', '', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n


def buscar_en_cache(cache, item_name):
    """Busca item en cache con matching flexible."""
    if not cache:
        return None
    if item_name in cache:
        return cache[item_name]
    norm = normalizar_nombre(item_name)
    for k, v in cache.items():
        if normalizar_nombre(k) == norm:
            return v
    for k, v in cache.items():
        if norm in normalizar_nombre(k) or normalizar_nombre(k) in norm:
            return v
    return None


def cargar_cache(path=None):
    path = path or CACHE_DEFAULT
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def guardar_cache(cache, path=None):
    path = path or CACHE_DEFAULT
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except OSError:
        pass


def buscar_google_api(item_query, api_key, cx):
    """Busca via Google Custom Search API."""
    q = urllib.parse.quote(f"{item_query} precio Peru S/")
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx}&q={q}&gl=pe&hl=es"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())

        precios = []
        enlaces = []
        for item in data.get("items", []):
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            enlaces.append(link)

            p = precio_desde_texto(title) or precio_desde_texto(snippet)
            if p:
                precios.append(p)

        return {
            "precios": sorted(set(precios))[:5],
            "mejor_precio": min(precios) if precios else None,
            "enlaces": enlaces[:3],
        }
    except Exception as e:
        return {"precios": [], "mejor_precio": None, "error": str(e)[:100]}


def generar_enlaces(item_query):
    """Genera enlaces de busqueda para cada proveedor."""
    enlaces = {}
    for key, prov in PROVEEDORES.items():
        enlaces[key] = {
            "nombre": prov["nombre"],
            "url": prov["url"].format(q=urllib.parse.quote_plus(item_query)),
        }
    return enlaces


def buscar_item(item_query, cache=None, google_api_key=None, google_cx=None, solo_enlaces=False):
    """Busca precios para un item usando todas las estrategias disponibles."""
    enlaces = generar_enlaces(item_query)
    resultado = {
        "item": item_query,
        "fecha": str(date.today()),
        "enlaces": enlaces,
        "google_api": None,
        "precio_cache": None,
        "mejor_precio": None,
        "mejor_proveedor": None,
    }

    # Estrategia 1: Cache local
    precio_cache = buscar_en_cache(cache, item_query)
    if precio_cache:
        resultado["precio_cache"] = precio_cache
        print(f"  [cache] S/ {precio_cache:.2f}")

    # Estrategia 2: Google API (si configurada)
    if google_api_key and google_cx and not solo_enlaces:
        print(f"  [Google API]...", end=" ", flush=True)
        gres = buscar_google_api(item_query, google_api_key, google_cx)
        resultado["google_api"] = gres
        if gres.get("mejor_precio"):
            print(f"S/ {gres['mejor_precio']:.2f}")
        else:
            print("sin resultado")
        time.sleep(0.5)

    # Determinar mejor precio
    candidatos = []
    if resultado.get("precio_cache"):
        candidatos.append(("cache", resultado["precio_cache"]))
    if resultado.get("google_api") and resultado["google_api"].get("mejor_precio"):
        candidatos.append(("google", resultado["google_api"]["mejor_precio"]))

    if candidatos:
        mejor = min(candidatos, key=lambda x: x[1])
        resultado["mejor_precio"] = mejor[1]
        resultado["mejor_proveedor"] = mejor[0]

    return resultado


def buscar_bom(bom_path, cache=None, google_api_key=None, google_cx=None,
               output_base="comparativa", actualizar=None, solo_enlaces=False):
    """Busca precios para todos los materiales del BOM."""
    with open(bom_path, "r", encoding="utf-8") as f:
        bom = json.load(f)

    materiales = bom.get("materiales", bom if isinstance(bom, list) else [])
    if isinstance(materiales, list):
        items = []
        for m in materiales:
            nombre = m.get("item", m.get("nombre", ""))
            if not nombre:
                continue
            base = nombre.split(" - ")[0] if " - " in nombre else nombre
            items.append({
                "nombre_original": nombre,
                "nombre_busqueda": base,
                "cantidad": m.get("cantidad", 0),
                "unidad": m.get("unidad", "und"),
                "precio_actual": m.get("precio_unit_soles", m.get("precio_unitario", 0)),
            })
    else:
        items = [{"nombre_original": k, "nombre_busqueda": k, "cantidad": v.get("cantidad", 0),
                   "unidad": v.get("unidad", "und"), "precio_actual": v.get("precio", 0)}
                 for k, v in materiales.items()]

    total_estimado = 0
    resultados_por_item = []
    cache_actualizado = dict(cache or {})

    for idx, item in enumerate(items):
        nb = item["nombre_busqueda"]
        print(f"\n[{idx+1}/{len(items)}] {nb}")
        res = buscar_item(nb, cache_actualizado, google_api_key, google_cx, solo_enlaces)
        res["cantidad"] = item["cantidad"]
        res["unidad"] = item["unidad"]
        res["nombre_original"] = item["nombre_original"]
        resultados_por_item.append(res)

        precio = res.get("mejor_precio") or item.get("precio_actual") or 0
        subtotal = precio * item["cantidad"]
        total_estimado += subtotal

        if res.get("mejor_precio") and nb not in cache_actualizado:
            cache_actualizado[nb] = res["mejor_precio"]

    # Generar outputs
    generar_html(resultados_por_item, output_base)
    generar_json(resultados_por_item, f"{output_base}.json")

    print(f"\n{'='*55}")
    print(f"  TOTAL ESTIMADO: S/ {total_estimado:.2f}")
    print(f"{'='*55}")

    # Actualizar cache
    if cache_actualizado:
        guardar_cache(cache_actualizado)

    # Actualizar BOM si se pidio
    if actualizar:
        actualizar_bom(actualizar, resultados_por_item)

    # Sugerir Google API si no se uso
    if not google_api_key and not solo_enlaces:
        print("\nSUGERENCIA: Para busqueda automatica real de precios, usa:")
        print("  --google-api-key TU_API_KEY --google-cx TU_CX")
        print("  (Google Custom Search API, 100 busquedas/dia gratis)")
        print("  O asigna precios manuales con: --precio \"ITEM=12.50\"")

    return resultados_por_item


def generar_html(resultados, output_base):
    """Genera tabla HTML comparativa con enlaces."""
    rows = ""
    for r in resultados:
        item = r.get("nombre_original", r["item"])
        cant = r.get("cantidad", 0)
        unidad = r.get("unidad", "")
        mejor_precio = r.get("mejor_precio")
        enlaces = r.get("enlaces", {})

        cols = f'<td><strong>{item}</strong><br><small>{cant} {unidad}</small></td>'

        for prov in MODO_ENLACES:
            if prov in enlaces:
                url = enlaces[prov]["url"]
                cols += f'<td><a href="{url}" target="_blank" style="font-size:7.5pt">Abrir</a></td>'

        # Columna Google API
        gap = r.get("google_api") or {}
        gap_precios = gap.get("precios", [])
        if gap_precios:
            p_str = " / ".join(f"S/ {p:.2f}" for p in gap_precios[:2])
            cols += f'<td style="background:#dcfce7;font-weight:700">{p_str}</td>'
        else:
            cols += '<td style="color:#999">-</td>'

        # Columna cache
        pc = r.get("precio_cache")
        if pc:
            cols += f'<td style="background:#fef3c7">S/ {pc:.2f}</td>'
        else:
            cols += '<td style="color:#999">-</td>'

        # Columna mejor precio
        if mejor_precio and cant:
            total_item = f"S/ {mejor_precio * cant:.2f}"
        elif cant:
            total_item = "(sin precio)"
        else:
            total_item = "-"
        cols += f'<td style="font-weight:700">{total_item}</td>'
        rows += f"<tr>{cols}</tr>"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Comparativa de Precios - Materiales Electricos</title>
<style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f8; padding: 20px; color: #17212b; }}
    h1 {{ font-size: 14pt; color: #0f766e; margin: 0 0 4px 0; }}
    .sub {{ color: #5c6670; font-size: 8pt; margin-bottom: 16px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06); font-size: 8.5pt; }}
    th {{ background: #0f766e; color: #fff; padding: 8px 5px; font-size: 7pt; text-align: left; white-space: nowrap; }}
    td {{ padding: 7px 5px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }}
    tr:hover td {{ background: #f0fdfa; }}
    a {{ color: #1d4ed8; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .legend {{ font-size: 7.5pt; margin: 10px 0; }}
    .lg {{ display:inline-block; padding:1px 6px; border-radius:3px; margin-right:8px; font-size:7pt }}
    .gapi {{ background:#dcfce7; }} .cache {{ background:#fef3c7; }}
    @media print {{ body {{ padding: 10px; }} .no-print {{ display: none; }} }}
</style>
</head>
<body>
<h1>Comparativa de Precios - Materiales Electricos</h1>
<p class="sub">{date.today()} | Enlaces directos a cada proveedor + precios Google API</p>
<p class="legend">
    <span class="lg gapi">Google API</span> precio obtenido via Google Search API
    <span class="lg cache">Cache</span> precio de busqueda anterior
    <span class="no-print" style="float:right"><button onclick="window.print()" style="background:#0f766e;color:#fff;border:0;border-radius:4px;padding:6px 14px;cursor:pointer">Imprimir</button></span>
</p>
<table>
<thead><tr>
    <th>Material</th>
    <th>Sodimac</th><th>Promart</th><th>MLibre</th><th>Maestro</th><th>Google</th>
    <th>Google API</th><th>Cache</th><th>Total</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>
</body>
</html>"""

    out_path = f"{output_base}.html"
    os.makedirs(os.path.dirname(output_base) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nTabla: {out_path}")


def generar_json(resultados, path):
    data = {
        "fecha": str(date.today()),
        "items": []
    }
    for r in resultados:
        item_data = {
            "item": r.get("nombre_original", r["item"]),
            "cantidad": r.get("cantidad", 0),
            "unidad": r.get("unidad", ""),
            "mejor_precio": r.get("mejor_precio"),
            "mejor_proveedor": r.get("mejor_proveedor"),
            "precio_cache": r.get("precio_cache"),
            "enlaces": {k: v["url"] for k, v in r.get("enlaces", {}).items()},
            "google_api": r.get("google_api"),
        }
        data["items"].append(item_data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"JSON: {path}")


def actualizar_bom(bom_path, resultados):
    with open(bom_path, "r", encoding="utf-8") as f:
        bom = json.load(f)

    precio_map = {}
    for r in resultados:
        nombre = r.get("nombre_original", r["item"])
        precio = r.get("mejor_precio")
        if precio:
            precio_map[normalizar_nombre(nombre)] = precio
            precio_map[normalizar_nombre(r["item"])] = precio

    actualizados = 0
    for m in bom.get("materiales", []):
        item_name = m.get("item", "")
        norm = normalizar_nombre(item_name)
        if norm in precio_map:
            m["precio_unit_soles"] = round(precio_map[norm], 2)
            actualizados += 1

    backup = f"{bom_path}.bak"
    import shutil
    shutil.copy2(bom_path, backup)

    with open(bom_path, "w", encoding="utf-8") as f:
        json.dump(bom, f, indent=2, ensure_ascii=False)
    print(f"Backup: {backup}")
    print(f"Actualizados: {actualizados} precios en {bom_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Buscador de precios de materiales electricos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 buscador_precios.py --item "cable TW 2.5mm2"
  python3 buscador_precios.py --bom output/bom.json --output comparativa
  python3 buscador_precios.py --bom output/bom.json --actualizar bom.json
  python3 buscador_precios.py --precio "cable TW 2.5mm2=12.50" --precio "ITM 2P 20A=45"
  python3 buscador_precios.py --bom output/bom.json --google-api-key KEY --google-cx CX
  python3 buscador_precios.py --item "cable TW 2.5mm2" --solo-enlaces
        """
    )
    parser.add_argument("--item", help="Material a buscar")
    parser.add_argument("--bom", help="JSON del BOM con lista de materiales")
    parser.add_argument("--output", default="comparativa_precios", help="Archivo base de salida")
    parser.add_argument("--proveedores", help="Proveedores (sodimac,promart,mercadolibre,maestro,google)")
    parser.add_argument("--listar", action="store_true", help="Listar materiales tipicos")
    parser.add_argument("--actualizar", metavar="BOM_JSON", help="Actualizar precios en el BOM")
    parser.add_argument("--solo-enlaces", action="store_true", help="Solo generar enlaces (sin scraping)")
    parser.add_argument("--precio", action="append", help="Precio manual ITEM=12.50 (repetible)")
    parser.add_argument("--google-api-key", help="API key de Google Custom Search")
    parser.add_argument("--google-cx", help="CX (ID de buscador) de Google Custom Search")
    parser.add_argument("--cache", help="Archivo de cache de precios (default: ~/.cache_precios_electricos.json)")
    parser.add_argument("--no-cache", action="store_true", help="No usar cache local")
    parser.add_argument("--delay", type=float, default=0.5, help="Segundos entre consultas Google API")

    args = parser.parse_args()

    if args.listar:
        print("\nMateriales electricos tipicos:")
        print("-" * 50)
        for i, m in enumerate(MATERIALES_TIPICOS, 1):
            print(f"  {i:3d}. {m}")
        return

    # Cargar cache
    cache_path = args.cache or CACHE_DEFAULT
    cache = {} if args.no_cache else cargar_cache(cache_path)

    # Agregar precios manuales
    if args.precio:
        for p in args.precio:
            if "=" in p:
                item, val = p.split("=", 1)
                try:
                    cache[item.strip()] = float(val.strip())
                except ValueError:
                    print(f"  ERROR: precio invalido '{val}' en '{p}'")
        guardar_cache(cache, cache_path)

    # Si solo hay precios manuales y no hay item/bom, mostrar resumen
    if args.precio and not args.item and not args.bom:
        print("\nPrecios en cache:")
        for k, v in cache.items():
            print(f"  {k}: S/ {v:.2f}")
        print(f"\nCache guardado en: {cache_path}")
        return

    google_api_key = args.google_api_key or os.environ.get("GOOGLE_API_KEY")
    google_cx = args.google_cx or os.environ.get("GOOGLE_CX")

    if args.item:
        res = buscar_item(args.item, cache, google_api_key, google_cx, args.solo_enlaces)
        generar_html([res], args.output)
        generar_json([res], f"{args.output}.json")

    if args.bom:
        buscar_bom(args.bom, cache, google_api_key, google_cx,
                   args.output, args.actualizar, args.solo_enlaces)

    if not args.item and not args.bom and not args.precio:
        print("Usa --item, --bom, o --precio. Ej: python3 buscador_precios.py --item 'cable TW 2.5mm2'")


if __name__ == "__main__":
    main()
