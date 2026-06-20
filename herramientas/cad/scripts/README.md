# Scripts CAD

Generación y manipulación de planos DXF.

| Script | Función |
|--------|---------|
| `dxf_generator.py` | Genera plano arquitectónico DXF desde JSON (muros, puertas, ventanas, cotas, mobiliario) |
| `electrical_overlay.py` | Superpone simbología eléctrica sobre DXF arquitectónico (luminarias, tomacorrientes, interruptores, tableros) |
| `auto_routing.py` | Enrutamiento A* de canalizaciones entre tablero y puntos eléctricos |
| `generar_unifilar.py` | Genera diagrama unifilar en DXF |

## Flujo típico

```bash
# 1. Plano arquitectónico
python3 herramientas/cad/scripts/dxf_generator.py --input layout.json --output plano.dxf

# 2. Superposición eléctrica
python3 herramientas/cad/scripts/electrical_overlay.py --base plano.dxf --electrical electrico.json --output plano-electrico.dxf
```
