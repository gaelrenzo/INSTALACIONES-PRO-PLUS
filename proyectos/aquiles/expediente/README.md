# Expediente LaTeX de Aquiles

Fuentes del expediente academico de instalaciones electricas interiores.

## Documentos compilables

- `main.tex`: expediente integral, capitulos 1 a 8.
- `especificaciones_tecnicas_acu.tex`: documento independiente solicitado en clase; incluye especificaciones tecnicas, medicion, valorizacion y ACU.
- `metrados_y_presupuesto_standalone.tex`: metrado y presupuesto como documento separado.

## Compilacion

Desde esta carpeta:

```bash
mkdir -p ../../../build/aquiles/expediente
latexmk -pdf -interaction=nonstopmode \
  -output-directory=../../../build/aquiles/expediente main.tex
latexmk -pdf -interaction=nonstopmode \
  -output-directory=../../../build/aquiles/expediente especificaciones_tecnicas_acu.tex
```

Las salidas publicadas se copian a:

```text
proyectos/aquiles/entregables/expediente.pdf
proyectos/aquiles/entregables/especificaciones-tecnicas-acu.pdf
```

## Fuentes principales

- `../datos/calculos.json`.
- `../diseno-electrico/datos/` y `../diseno-electrico/planos/`.
- `../presupuesto/bom_final_aquiles.json`.
- `../presupuesto/presupuesto_final_aquiles.json`.
- `../documentacion/auditoria-especificaciones-acu-2026-06-13.md`.
- `../../../referencias/normativa/`.

Los datos marcados como preliminares no deben usarse para compra o construccion sin
validacion tecnica. En particular, siguen pendientes la potencia de placa de cargas
especiales, la coordinacion final de protecciones y la capacidad modular de TG y T2.
