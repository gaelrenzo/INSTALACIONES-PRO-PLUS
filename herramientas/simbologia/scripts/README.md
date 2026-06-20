# Scripts de simbología

| Script | Función |
|--------|---------|
| `generar_simbologia_dge_dxf.py` | Genera un catálogo DXF/PDF de todos los símbolos eléctricos normativos DGE |

## Uso

```bash
python3 herramientas/simbologia/scripts/generar_simbologia_dge_dxf.py
```

Los símbolos se definen en `simbologia_normativa_dge.json` y son usados por `electrical_overlay.py` para dibujar luminarias, interruptores, tomacorrientes, tableros, etc.
