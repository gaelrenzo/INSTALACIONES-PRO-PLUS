# Dominios — Módulos del negocio

Cada subcarpeta implementa un dominio específico de ingeniería eléctrica.

| Dominio | Carpeta | Función |
|---------|---------|---------|
| **CAD** | `cad/` | Generación de planos DXF |
| **BIM** | `bim/` | Exportación a IFC (ifcopenshell) |
| **Cálculos** | `calculos/` | Motor de cálculos CNE |
| **Cotizaciones** | `cotizaciones/` | Cálculo de BOM / presupuesto |
| **Documentos** | `documentos/` | Generación de reportes PDF |

## Dependencias

- CAD: `ezdxf`, `matplotlib`
- BIM: `ifcopenshell` (opcional)
- Cálculos: `pandas`, `pandapower`
- Documentos: `weasyprint`, `jinja2`
