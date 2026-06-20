# MEMORIA DE CÁLCULO

## Instalaciones eléctricas interiores - vivienda unifamiliar de 3 pisos

Proyecto académico para vivienda de tres niveles en Jr. Lima S/N (Coordenadas: 15°38'32.7"S 69°49'51.8"W), Capachica, Puno. Sistema monofásico 220 V, 60 Hz.

## Circuitos y Demanda Adoptados

El sistema eléctrico se organiza en 7 circuitos (alumbrado y tomacorrientes por nivel, más un circuito independiente de tomacorrientes especiales de cocina en el primer piso). Se han eliminado motores o bombas especiales para ajustarse al levantamiento real de puntos:

| Circuito | Uso | Puntos | Pot. Instalada (W) | F. Demanda | Máx. Demanda (W) |
| --- | --- | :---: | :---: | :---: | :---: |
| **C1** | Alumbrado primer piso | 4 | 500 W | 1.00 | 500 W |
| **C2** | Tomacorrientes generales 1er piso | 5 | 1000 W | 1.00 | 1000 W |
| **C3** | Tomacorrientes de cocina (1er piso) | 3 | 1500 W | 1.00 | 1500 W |
| **C4** | Alumbrado segundo piso | 4 | 500 W | 1.00 | 500 W |
| **C5** | Tomacorrientes del segundo piso | 8 | 1500 W | 0.70 | 1050 W |
| **C6** | Alumbrado tercer piso | 4 | 500 W | 1.00 | 500 W |
| **C7** | Tomacorrientes del tercer piso | 6 | 1500 W | 0.70 | 1050 W |
| **Total** | | **34** | **7000 W** | | **6100 W** |

- **Potencia Instalada Total:** 7,000 W
- **Máxima Demanda Estimada:** 6,100 W

## Corriente de Diseño ($I_{dem}$)

Fórmula monofásica aplicada:

```text
I = P / (V x cos φ)
```

Con:
- $P = 6,100\text{ W}$ (Máxima Demanda)
- $V = 220\text{ V}$ (Tensión nominal)
- $\cos \phi = 0.90$ (Factor de potencia)

Cálculo:

```text
I = 6100 / (220 x 0.90) = 6100 / 198 = 30.81 A
```

## Conductores y Protecciones Generales

1.  **Interruptor General Termomagnético:** Se selecciona una llave general de **2P - 40 A** (adecuada para cubrir la corriente de diseño de 30.81 A y proteger el alimentador principal).
2.  **Interruptor Diferencial General:** Se propone un interruptor diferencial general de **2P - 40 A / 30 mA** en el Tablero General para protección total.
3.  **Conductor Alimentador Principal:** Se adopta un cable alimentador de **2 x 10 mm² Cu + 1 x 10 mm² Cu (PE)** desde el medidor hasta el TG-01.

## Conductores y Protecciones de Circuitos Derivados

| Circuito | Uso | Interruptor Termomagnético / Diferencial | Conductor Eléctrico |
| --- | --- | --- | --- |
| **C1** | Alumbrado primer piso | 2P-10A | 3 x 1.5 mm² Cu (PW) |
| **C2** | Tomacorrientes generales 1er piso | 2P-16A / ID-25A - 30mA | 3 x 2.5 mm² Cu (PW) |
| **C3** | Tomacorrientes especiales cocina | 2P-20A / ID-25A - 30mA | 3 x 2.5 mm² Cu (PW) |
| **C4** | Alumbrado segundo piso | 2P-10A | 3 x 1.5 mm² Cu (PW) |
| **C5** | Tomacorrientes del segundo piso | 2P-16A / ID-25A - 30mA | 3 x 2.5 mm² Cu (PW) |
| **C6** | Alumbrado tercer piso | 2P-10A | 3 x 1.5 mm² Cu (PW) |
| **C7** | Tomacorrientes del tercer piso | 2P-16A / ID-25A - 30mA | 3 x 2.5 mm² Cu (PW) |

*Nota: Todos los circuitos de tomacorrientes (C2, C3, C5, C7) incorporan obligatoriamente conductores de protección a tierra y protección diferencial independiente de 25A - 30mA para salvaguardar la vida de las personas según el CNE-U.*
