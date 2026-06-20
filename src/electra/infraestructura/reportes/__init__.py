"""Generación de reportes LaTeX, Markdown y expediente técnico."""

from __future__ import annotations

from .expediente import generar_expediente
from .latex import generar_tablas_latex
from .markdown import generar_reporte_markdown

__all__ = ["generar_expediente", "generar_tablas_latex", "generar_reporte_markdown"]
