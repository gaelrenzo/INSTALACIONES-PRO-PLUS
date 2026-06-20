from __future__ import annotations

from abc import ABC, abstractmethod

from electra_core.modelos.topologia import RedElectrica


class ExportadorCAD(ABC):
    @abstractmethod
    def exportar_diagrama(self, red: RedElectrica, ruta: str) -> str: ...


class ExportadorBIM(ABC):
    @abstractmethod
    def exportar_ifc(self, red: RedElectrica, ruta: str) -> str: ...


class GeneradorDocumento(ABC):
    @abstractmethod
    def generar_reporte(self, red: RedElectrica, plantilla: str) -> str: ...


class CalculadorPresupuesto(ABC):
    @abstractmethod
    def calcular_bom(self, red: RedElectrica) -> dict: ...
