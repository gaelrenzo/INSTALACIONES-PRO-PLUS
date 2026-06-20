# Proyecto Renzo

Expediente de instalaciones electricas para una vivienda unifamiliar de tres
pisos en Capachica, Puno. El punto de entrada del proyecto es
`proyecto.yaml`; no se debe elegir una entrada por nombres como `v1`, `nuevo`
o `final`.

## Estructura activa

```text
fuentes/             archivos originales recibidos; no se sobrescriben
arquitectura/        tres layouts JSON canonicos y su interpretacion
diseno-electrico/    modelo electrico canonico y fuente editable del unifilar
datos/               parametros del proyecto, normativa y proveedores
expediente/          fuentes LaTeX del documento tecnico
documentacion/       borradores, reportes y decisiones de coordinacion
scripts/             automatizacion exclusiva de este proyecto
tests/               comprobaciones de calculo
entregables/         archivos revisados y publicados
archivo/             iteraciones historicas fuera del flujo activo
```

Los archivos regenerables se escriben en `build/renzo/`, fuera de esta
carpeta y sin seguimiento de Git.

## Entradas canonicas

- Arquitectura: `arquitectura/datos/piso-1.json`, `piso-2.json` y
  `piso-3.json`.
- Diseno electrico: `diseno-electrico/datos/modelo-electrico.json`.
- Parametros: `datos/parametros-proyecto.yaml`.
- Expediente: `expediente/main.tex`.

Las versiones anteriores se conservan en `archivo/` solo como referencia. No
son entradas validas para el pipeline.

## Ejecucion

Desde la raiz del repositorio:

```bash
python3 herramientas/pipeline_automatizado.py --proyecto renzo
python3 -m pytest -q proyectos/renzo/tests
```

El pipeline genera arquitectura, planos electricos, diagramas y el PDF del
expediente en `build/renzo/`. Copiar resultados a `entregables/` requiere una
revision tecnica y visual previa.

## Alcance actual

La estructura de datos ya tiene una unica version activa. Los generadores CAD
siguen siendo especificos de Renzo y se depuraran en la siguiente fase para
extraer logica reutilizable hacia `herramientas/`.
