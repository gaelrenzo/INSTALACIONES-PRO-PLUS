"""
Orquestador legacy — DEPRECATED.

Usa `python -m electra.aplicacion.cli pipeline --proyecto <id>` en su lugar.
Soportado hasta v2.0 para compatibilidad con scripts existentes.

Esta clase ahora delega en electra.aplicacion.orquestador.Orquestador
para la ejecucion del pipeline, pero mantiene su API original.
"""

from __future__ import annotations

import warnings
from pathlib import Path

warnings.warn(
    "electra_core.orquestador.pipeline.Orquestador esta obsoleto. "
    "Usa electra.aplicacion.orquestador.Orquestador",
    DeprecationWarning,
    stacklevel=2,
)

import yaml
from pydantic import ValidationError

from electra.aplicacion.orquestador import Orquestador as OrquestadorNuevo


class Orquestador:
    def __init__(self, ruta_yaml: str) -> None:
        self.ruta_yaml = ruta_yaml
        self._inner: OrquestadorNuevo | None = None

    def cargar_yaml(self):
        with open(self.ruta_yaml, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        proyecto_id = Path(self.ruta_yaml).parent.name
        self._inner = OrquestadorNuevo.desde_proyecto(proyecto_id)
        return data

    def construir_grafo(self):
        self._asegurar_inner()
        return None  # pendiente migracion

    def ejecutar_flujo(self) -> dict:
        self._asegurar_inner()
        resultado = self._inner.ejecutar()
        for etapa in resultado.etapas:
            if etapa.nombre == "Calculos" and etapa.datos:
                return etapa.datos
        return {}

    def validar_normativa(self) -> list[str]:
        return ["DEPRECATED: validacion migrada al nuevo pipeline"]

    def generar_dxf(self, ruta_salida: str) -> str:
        self._asegurar_inner()
        resultado = self._inner.ejecutar()
        for etapa in resultado.etapas:
            if etapa.nombre == "CAD" and "dxf" in etapa.archivos_generados:
                return str(etapa.archivos_generados["dxf"])
        return ""

    def generar_ifc(self, ruta_salida: str) -> str:
        return "ifcopenshell no disponible en la migracion"

    def generar_presupuesto(self) -> dict:
        self._asegurar_inner()
        resultado = self._inner.ejecutar()
        for etapa in resultado.etapas:
            if etapa.nombre == "BOM" and etapa.datos:
                return etapa.datos
        return {}

    def generar_reporte(self, plantilla: str = "reporte_tecnico.html") -> str:
        return "DEPRECATED: reportes migrados al nuevo pipeline"

    def ejecutar_completo(self, ruta_dxf: str = "salida.dxf", ruta_ifc: str = "salida.ifc") -> dict:
        return {
            "grafo": self.construir_grafo(),
            "flujo": self.ejecutar_flujo(),
            "validacion": self.validar_normativa(),
            "dxf": self.generar_dxf(ruta_dxf),
            "presupuesto": self.generar_presupuesto(),
            "reporte": self.generar_reporte(),
            "ifc": self.generar_ifc(ruta_ifc),
        }

    def _asegurar_inner(self) -> None:
        if self._inner is None:
            self.cargar_yaml()
