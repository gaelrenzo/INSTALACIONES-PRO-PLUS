"""Re-export — legacy GeneradorDXF kept for backward compat."""

from __future__ import annotations

import ezdxf
from ezdxf.math import Vec2

from electra_core.interfaces.puertos import ExportadorCAD
from electra_core.modelos.topologia import RedElectrica


class GeneradorDXF(ExportadorCAD):
    def exportar_diagrama(self, red: RedElectrica, ruta: str) -> str:
        doc = ezdxf.new("R2010")
        msp = doc.modelspace()
        y_offset = 0
        for i, tablero in enumerate(red.tableros):
            y = i * 30
            msp.add_text(
                tablero.nombre,
                dxfattribs={"height": 2.5, "insert": Vec2(5, y)},
            )
            for j, circuito in enumerate(tablero.circuitos):
                cy = y + 5 + j * 4
                msp.add_line(
                    Vec2(10, cy),
                    Vec2(30, cy),
                    dxfattribs={"layer": "CIRCUITOS"},
                )
                msp.add_text(
                    f"{circuito.nombre} "
                    f"({sum(c.potencia_w for c in circuito.cargas)/1000:.1f} kW)",
                    dxfattribs={"height": 1.5, "insert": Vec2(32, cy - 0.8)},
                )
        doc.saveas(ruta)
        return ruta


from electra.infraestructura.cad.dxf_generator import (  # noqa: E402, F401
    generate_dxf,
    generate_pdf_from_dxf,
)
