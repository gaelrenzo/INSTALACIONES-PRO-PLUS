from __future__ import annotations

import yaml
from pydantic import ValidationError

from electra_core.core.topologia import GrafoTopologico
from electra_core.core.resolver import ResolverRed
from electra_core.modelos.topologia import RedElectrica


class Orquestador:
    def __init__(self, ruta_yaml: str) -> None:
        self.ruta_yaml = ruta_yaml
        self.red: RedElectrica | None = None
        self.grafo: GrafoTopologico | None = None
        self.resolver: ResolverRed | None = None

    def cargar_yaml(self) -> RedElectrica:
        with open(self.ruta_yaml, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.red = RedElectrica.model_validate(data)
        return self.red

    def construir_grafo(self) -> GrafoTopologico:
        if not self.red:
            self.cargar_yaml()
        self.grafo = GrafoTopologico(self.red)
        return self.grafo

    def ejecutar_flujo(self) -> dict:
        if not self.red:
            self.cargar_yaml()
        self.resolver = ResolverRed(self.red)
        return self.resolver.ejecutar_flujo()

    def validar_normativa(self) -> list[str]:
        from electra_core.core.normativas.cne import CNEPeru
        if not self.red:
            self.cargar_yaml()
        norma = CNEPeru()
        return norma.validar_red(self.red)

    def generar_dxf(self, ruta_salida: str) -> str:
        from electra_core.dominios.cad.generador_dxf import GeneradorDXF
        if not self.red:
            self.cargar_yaml()
        gen = GeneradorDXF()
        return gen.exportar_diagrama(self.red, ruta_salida)

    def generar_ifc(self, ruta_salida: str) -> str:
        from electra_core.dominios.bim.exportador_ifc import ExportadorIFC
        if not self.red:
            self.cargar_yaml()
        exp = ExportadorIFC()
        return exp.exportar_ifc(self.red, ruta_salida)

    def generar_presupuesto(self) -> dict:
        from electra_core.dominios.cotizaciones.calculador_bom import CalculadorBOM
        if not self.red:
            self.cargar_yaml()
        bom = CalculadorBOM()
        return bom.calcular_bom(self.red)

    def generar_reporte(self, plantilla: str = "reporte_tecnico.html") -> str:
        from electra_core.dominios.documentos.generador_pdf import GeneradorPDF
        if not self.red:
            self.cargar_yaml()
        gen = GeneradorPDF()
        return gen.generar_reporte(self.red, plantilla)

    def ejecutar_completo(self, ruta_dxf: str = "salida.dxf", ruta_ifc: str = "salida.ifc") -> dict:
        resultados = {}
        self.cargar_yaml()
        resultados["grafo"] = self.construir_grafo()
        resultados["flujo"] = self.ejecutar_flujo()
        resultados["validacion"] = self.validar_normativa()
        resultados["dxf"] = self.generar_dxf(ruta_dxf)
        resultados["presupuesto"] = self.generar_presupuesto()
        resultados["reporte"] = self.generar_reporte()
        try:
            resultados["ifc"] = self.generar_ifc(ruta_ifc)
        except ImportError:
            resultados["ifc"] = "ifcopenshell no disponible"
        return resultados
