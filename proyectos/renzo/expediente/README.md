# Expediente LaTeX

`main.tex` es la raiz del documento. Los capitulos y tablas auxiliares se
mantienen dentro de esta carpeta para evitar mezclarlos con datos o planos.

No ejecutar `pdflatex` directamente en la carpeta del proyecto. Usar:

```bash
python3 herramientas/pipeline_automatizado.py --proyecto renzo
```

El PDF temporal se genera en `build/renzo/expediente/main.pdf`.
