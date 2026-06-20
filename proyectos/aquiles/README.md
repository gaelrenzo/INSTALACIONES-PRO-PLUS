# Proyecto Aquiles

Vivienda unifamiliar de dos pisos. El punto de entrada es `proyecto.yaml`.

```text
fuentes/             croquis, ubicación y referencias recibidas
arquitectura/        layouts y planos arquitectónicos canónicos
diseno-electrico/    datos y planos eléctricos por piso
datos/               parámetros de cálculo
presupuesto/         fuentes del BOM y presupuesto académico
expediente/          fuentes LaTeX
documentacion/       decisiones y coordinación
entregables/         resultados publicados
archivo/             material histórico conservado
```

Ejecución:

```bash
python3 herramientas/pipeline_automatizado.py --proyecto aquiles
python3 proyectos/aquiles/scripts/generar-metrados.py
```

Documentos LaTeX principales:

```text
expediente/main.tex                         expediente integral
expediente/especificaciones_tecnicas_acu.tex especificaciones y ACU solicitados en clase
```

La auditoria del borrador rapido y las decisiones de correccion estan en
`documentacion/auditoria-especificaciones-acu-2026-06-13.md`.

El CAD automático usa actualmente el primer piso como plano primario. El segundo piso sigue disponible como entrada canónica y debe procesarse o revisarse por separado antes de publicar una nueva entrega.
