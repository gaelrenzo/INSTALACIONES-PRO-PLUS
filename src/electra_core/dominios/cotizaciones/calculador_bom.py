from __future__ import annotations

import polars as pl

from electra_core.interfaces.puertos import CalculadorPresupuesto
from electra_core.modelos.topologia import RedElectrica


class CalculadorBOM(CalculadorPresupuesto):
    def __init__(self, catalogo_csv: str | None = None) -> None:
        self.catalogo: pl.DataFrame | None = None
        if catalogo_csv:
            self.catalogo = pl.read_csv(catalogo_csv)

    def calcular_bom(self, red: RedElectrica) -> dict:
        materiales: dict[str, float] = {}
        for tablero in red.tableros:
            for circuito in tablero.circuitos:
                material = f"Cable {circuito.cable.seccion_mm2:.0f}mm²"
                cantidad = circuito.largo_metros * 3
                materiales[material] = materiales.get(material, 0) + cantidad

                for carga in circuito.cargas:
                    item = f"{carga.tipo.value}"
                    materiales[item] = materiales.get(item, 0) + 1

        return {
            "nombre_proyecto": red.nombre_proyecto,
            "materiales": materiales,
            "total_articulos": len(materiales),
        }
