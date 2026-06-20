# Coordinacion tecnica

## Revision del 10 de junio de 2026

Se alinearon los capitulos del expediente con siete circuitos electricos:

- Potencia instalada: **7000 W**.
- Demanda maxima: **6100 W**.
- Corriente de empleo: **30.81 A**.
- Alimentador: **10 mm2**.
- Proteccion general: **2P-40A**.
- Cuatro diferenciales para los circuitos de tomacorrientes C2, C3, C5 y C7.

Los textos afectados estan actualmente en:

- `../expediente/capitulos/01-memoria-descriptiva.tex`.
- `../expediente/capitulos/02-calculos-justificativos.tex`.
- `../expediente/capitulos/06-metrado.tex`.
- `../expediente/capitulos/09-presupuesto.tex`.

## Pendientes tecnicos

- Consolidar la diferencia entre puntos fisicos del modelo electrico y las
  tablas de metrado antes de comprar materiales.
- Revisar escalas, membretes y legibilidad de todos los planos publicados.
- Confirmar que cualquier cambio de circuitos se refleje en el modelo
  electrico, los metrados y el presupuesto.

## Fuente de verdad

Las entradas vigentes se declaran en `../proyecto.yaml`. El script
`../scripts/actualizar_metrados_latex.py` mantiene los capitulos de metrado y
presupuesto, pero no sustituye la revision del modelo canonico ni la validacion
humana.
