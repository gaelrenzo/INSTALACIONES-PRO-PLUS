# Scripts de cálculo

| Script | Función |
|--------|---------|
| `calcular_instalacion.py` | Motor de cálculos: demanda, conductores, protecciones, caída de tensión por circuito. Genera resultados.json + tablas LaTeX |
| `generar_bom.py` | Genera lista de materiales (BOM) desde los resultados de cálculo |

## Uso

```bash
python3 herramientas/calculos/scripts/calcular_instalacion.py \
  --input proyectos/aquiles/datos/calculos.json \
  --output-dir build/aquiles/calculos
```

## Entrada

JSON con: proyecto, ubicación, parámetros eléctricos, circuitos base, escenarios.

## Salida

- `resultados.json`: cálculos por escenario
- `reporte_calculos.md`: resumen legible
- `*.tex`: tablas LaTeX para el expediente
