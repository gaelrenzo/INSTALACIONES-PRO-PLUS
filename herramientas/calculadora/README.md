# Calculadora interactiva de cargas

Interfaz web HTML/JS para levantar cargas eléctricas por ambiente.

## Uso

Abrir `index.html` en el navegador:

```
start herramientas/calculadora/index.html
```

## Funcionalidad

- Agregar cargas por ambiente: sala, cocina, dormitorio, etc.
- Especificar tipo: Alumbrado, Tomacorrientes, Cocina/lavandería, Especial
- Asignar a circuitos (C1–C8)
- Calcula automáticamente: demanda, conductor, protección, caída de tensión
- Exporta a: **Markdown**, **JSON**, **LaTeX**

## Pendiente

- Generar coordenadas (x, y) para cada elemento (necesario para el plano DXF)
- Exportar directamente al YAML que entiende `pipeline_automatizado.py`
- Guardar/recuperar proyectos
