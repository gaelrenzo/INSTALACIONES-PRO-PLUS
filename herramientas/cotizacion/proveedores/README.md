# Conectores de proveedores

Módulos individuales para consultar precios en línea de materiales eléctricos.

| Proveedor | Archivo | Método |
|-----------|---------|--------|
| **Promart** | `promart.py` | Web scraping |
| **Sodimac** | `sodimac.py` | Web scraping |
| **Maestro** | `maestro.py` | Web scraping |
| **MercadoLibre** | `mercadolibre.py` | Web scraping |
| **Ventas Perú** | `ventas_peru.py` | Web scraping |
| **Base** | `base.py` | Clase abstracta base |

Todas implementan: `buscar(material) → lista de resultados con precio, unidad, URL, fecha`.
