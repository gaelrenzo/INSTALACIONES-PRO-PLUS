from __future__ import annotations

from electra_core.core.normativas.base import EstrategiaNormativa
from electra_core.modelos.topologia import RedElectrica, Tablero, Circuito


class IEC60364(EstrategiaNormativa):
    TEMP_AIRE_BASE = 30.0
    TEMP_SUELO_BASE = 20.0
    RESISTIVIDAD_TERRENO = 2.5

    def validar_caida_tension(self, circuito: Circuito) -> list[str]:
        alertas = []
        if circuito.caida_tension_max_porcentaje > 4.0:
            alertas.append(
                f"Circuito '{circuito.nombre}': caída {circuito.caida_tension_max_porcentaje:.2f}% "
                f"excede límite IEC 4%"
            )
        return alertas

    def validar_tablero(self, tablero: Tablero) -> list[str]:
        alertas = []
        for circuito in tablero.circuitos:
            alertas.extend(self.validar_caida_tension(circuito))
        return alertas

    def validar_red(self, red: RedElectrica) -> list[str]:
        alertas = []
        for tablero in red.tableros:
            alertas.extend(self.validar_tablero(tablero))
        return alertas
