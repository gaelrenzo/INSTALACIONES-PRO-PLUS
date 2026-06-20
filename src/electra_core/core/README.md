# Core — Lógica base del dominio

Módulos fundamentales del sistema de ingeniería eléctrica.

| Módulo | Archivo | Función |
|--------|---------|---------|
| **Normativas** | `normativas/` | Estrategias de validación normativa (CNE Perú, IEC) |
| **Topología** | `topologia.py` | Grafo topológico de la red eléctrica (tableros, circuitos, cargas) |
| **Resolución** | `resolver.py` | Resolución de flujo de potencia y dimensionamiento |

## Normativas

- `base.py`: clase abstracta `EstrategiaNormativa`
- `cne.py`: implementación CNE Perú (caída de tensión, tableros, red)
- `iec.py`: implementación IEC (base)
