# Orquestador — Pipeline de ejecución

Coordina el flujo completo desde la carga de datos hasta la generación de entregables.

| Archivo | Función |
|---------|---------|
| `pipeline.py` | Clase `Orquestador` — carga YAML, construye grafo, ejecuta flujo, valida normativa, genera DXF/IFC/BOM/reporte |

## Flujo `ejecutar_completo()`

1. `cargar_yaml()` → `RedElectrica`
2. `construir_grafo()` → `GrafoTopologico`
3. `ejecutar_flujo()` → resolución de red
4. `validar_normativa()` → CNE Perú
5. `generar_dxf()` → plano DXF
6. `generar_presupuesto()` → BOM
7. `generar_reporte()` → PDF
8. `generar_ifc()` → modelo BIM (opcional)
