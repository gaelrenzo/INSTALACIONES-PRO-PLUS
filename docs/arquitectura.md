# Arquitectura del repositorio

## Principio central

El repositorio separa tres tipos de información:

- **Fuentes:** croquis, fotografías, normativa y documentos recibidos.
- **Datos canónicos:** JSON/YAML que representan la interpretación vigente.
- **Resultados:** DXF, PDF, tablas, BOM y reportes que pueden regenerarse.

Esta separación permite cambiar el motor de IA o CAD sin perder la evidencia original y evita usar una salida vieja como entrada accidental.

## Proyectos

Cada carpeta en `proyectos/` debe contener:

```text
proyecto.yaml
fuentes/
arquitectura/datos/
diseno-electrico/datos/
datos/
documentacion/
entregables/
expediente/        cuando el proyecto tenga fuentes de un documento tecnico
archivo/           material historico fuera del flujo activo
scripts/           solo extensiones realmente especificas
tests/             pruebas propias del proyecto
```

`proyecto.yaml` es el punto de entrada. Declara identidad, estado, rutas canónicas, automatización disponible y entregables publicados.

Una carpeta de proyecto no debe mezclar simultaneamente una estructura por
capitulos (`01_...`, `02_...`) con otra estructura por responsabilidad. Los
capitulos pertenecen dentro de `expediente/`; las hojas de calculo publicadas
pertenecen en `entregables/`; y las iteraciones antiguas pertenecen en
`archivo/`.

## Herramientas

- `pipeline_automatizado.py`: orquestación común.
- `calculos/`: demanda, conductores, protecciones y tablas LaTeX.
- `cad/`: generación arquitectónica, superposición eléctrica y PDF.
- `simbologia/`: biblioteca DGE y generador del catálogo.
- `cotizacion/`: BOM, normalización, proveedores, comparación y reportes.
- `calculadora/`: interfaz HTML independiente.

Las herramientas no deben incluir datos, nombres ni rutas de Aquiles o Renzo.

## Extensiones

Un proyecto con un formato CAD especial puede declarar `automatizacion.cad_personalizado` en su manifiesto. El pipeline conserva así una interfaz común sin forzar todos los diseños a un único esquema interno.

## Salidas

`build/<id>/` contiene la ejecución actual y está ignorado por Git.
`entregables/` contiene unicamente resultados revisados que si se desea
versionar. Los scripts nunca deben escribir directamente en `entregables/`.
