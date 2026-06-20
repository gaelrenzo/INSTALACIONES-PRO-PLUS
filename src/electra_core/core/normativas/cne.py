from __future__ import annotations

import math

from electra_core.modelos.topologia import (
    RedElectrica,
    Tablero,
    Circuito,
    Cable,
    TipoNormativa,
)
from electra_core.core.normativas.base import EstrategiaNormativa


class CNEPeru(EstrategiaNormativa):
    CAIDA_MAX_ALIMENTADOR = 2.5
    CAIDA_MAX_DERIVADO = 1.5
    CAIDA_MAX_ACUMULADA = 4.0
    RESISTENCIA_PST_FUERZA = 25.0
    RESISTENCIA_PST_EQUIPOS = 5.0

    def validar_caida_tension(self, circuito: Circuito) -> list[str]:
        alertas = []
        caida = circuito.caida_tension_max_porcentaje
        if caida > self.CAIDA_MAX_ALIMENTADOR:
            alertas.append(
                f"Alimentador '{circuito.nombre}': caída {caida:.2f}% "
                f"excede límite CNE {self.CAIDA_MAX_ALIMENTADOR}%"
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

    def calcular_resistencia_pst(
        self, resistividad: float, longitud_m: float, diametro_mm: float
    ) -> float:
        d = diametro_mm / 1000
        return (resistividad / (2 * math.pi * longitud_m)) * math.log(4 * longitud_m / d)

    def calcular_caida_tension(
        self, cable: Cable, corriente_a: float, largo_metros: float
    ) -> float:
        R = 0.0172 / cable.seccion_mm2
        return (2 * largo_metros * R * corriente_a * 100) / 220.0
