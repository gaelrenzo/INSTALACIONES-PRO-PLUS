# Auditoria de especificaciones tecnicas y ACU

Fecha de revision: 2026-06-13.

## Entradas revisadas

- Borrador recibido: `fuentes/documentos-recibidos/especificaciones-tecnicas-acu-borrador-2026-06-10.pdf`.
- Fotografia de la pizarra: `fuentes/fotos-clase/pizarra-especificaciones-acu-2026-06-13.png`.
- Datos de calculo: `datos/calculos.json`.
- Planos y datos electricos canonicos de los pisos 1 y 2.
- BOM: `presupuesto/bom_final_aquiles.json`.
- Presupuesto referencial fechado el 8 de junio de 2026.
- Codigo Nacional de Electricidad - Utilizacion y RNE EM.010 conservados en `referencias/normativa/`.

## Hallazgos del borrador rapido

| Hallazgo | Riesgo | Correccion aplicada |
|---|---|---|
| Indicaba 190 m de canalizacion para C1 a C8. | No era reproducible desde el BOM. | Se concilio la suma: 152 m. |
| Indicaba cinco salidas especiales. | Omitia una salida del metrado. | Se documentaron seis: C3=1, C6=3, C7=1 y C8=1. |
| Sumaba una partida general de canalizacion y ACU de puntos que ya incluian tuberia y cable. | Doble conteo de materiales y mano de obra. | Los ACU de dispositivos excluyen tuberia y conductores; la valorizacion usa partidas no superpuestas. |
| Presentaba tablero para 8 circuitos/polos como solucion cerrada. | No reserva modulos para ITM bipolares, diferenciales y dos protecciones futuras. | La capacidad se deja pendiente del unifilar y se exige la reserva de la Regla 050-108(2). |
| Combinaba ITM general 2P-63 A con diferencial general 2P-40 A. | La corriente nominal del diferencial quedaba por debajo de la proteccion aguas arriba. | Se especifica que cada diferencial debe tener corriente nominal igual o mayor que su proteccion aguas arriba. |
| El BOM denomina trifasico al alimentador principal. | Contradice el suministro monofasico de 220 V. | El nuevo documento usa exclusivamente la denominacion monofasica. |
| C6 figura con conductor de 10 mm2 y tubo de 20 mm en el BOM, mientras el modelo de calculo propone 32 mm. | Inconsistencia de ocupacion y especificacion. | El documento adopta 32 mm para el escenario de 10 mm2 y marca la regeneracion del presupuesto como pendiente. |
| Los precios no distinguian evidencia comercial de supuestos. | Daba apariencia de cotizacion definitiva. | Cada recurso del ACU se marca como verificado (V) o estimado (E). |
| No habia trazabilidad normativa por regla. | Dificultaba defender los criterios ante el docente. | Se incorporaron las reglas CNE-U 020-132, 030-002, 050-108, 060-712, 150-400 y 150-402. |

## Decisiones tecnicas

- Resistencia maxima de puesta a tierra: 25 ohm, conforme a CNE-U 060-712. El valor de 15 ohm que aparecia en el antiguo capitulo de montaje no se mantiene como exigencia normativa.
- Proteccion diferencial: sensibilidad no mayor de 30 mA; no sustituye al sistema de puesta a tierra.
- Los circuitos bajo un diferencial se agrupan como maximo de a tres, salvo diferencial individual por circuito.
- La altura de 1.20 m para interruptores, 0.30 m para tomacorrientes generales y 1.10 m para puntos sobre mesa se conserva como criterio del proyecto. La exigencia normativa comprobada para tableros es que ninguna manija supere 1.70 m.
- Las cargas de cocina, lavadora y bomba siguen sujetas a confirmacion de placa. Por ello no se publica un ACU cerrado de tableros ni salidas especiales.

## Resultado

El contenido corregido se integra en:

- `expediente/capitulos/03-especificaciones-materiales.tex`.
- `expediente/capitulos/04-especificaciones-montaje.tex`.
- `expediente/especificaciones_tecnicas_acu.tex` como documento independiente.
- `entregables/especificaciones-tecnicas-acu.pdf` como salida revisada.

El documento independiente responde en forma directa a la estructura solicitada en clase: requisitos de materiales, metodo de ejecucion, metodo de medicion y valorizacion, unidad de medida y ACU de partidas representativas.
