from __future__ import annotations

from electra_core.core.normativas.cne import CNEPeru
from electra_core.modelos.topologia import RedElectrica, Cable


class MotorValidacionCNE:
    def __init__(self) -> None:
        self.norma = CNEPeru()

    def validar_red(self, red: RedElectrica) -> list[str]:
        return self.norma.validar_red(red)

    def disenar_puesta_tierra(
        self, resistividad: float, longitud_m: float, diametro_mm: float
    ) -> dict:
        R = self.norma.calcular_resistencia_pst(resistividad, longitud_m, diametro_mm)
        alertas = []
        if R > self.norma.RESISTENCIA_PST_FUERZA:
            alertas.append(f"Resistencia {R:.2f} ohm excede límite fuerza 25 ohm")
        if R > self.norma.RESISTENCIA_PST_EQUIPOS:
            alertas.append(f"Resistencia {R:.2f} ohm excede límite equipos 5 ohm")
        return {"resistencia_ohm": round(R, 2), "alertas": alertas}

    def calcular_caida_tension_circuito(
        self, cable: Cable, corriente_a: float, largo_metros: float
    ) -> float:
        return self.norma.calcular_caida_tension(cable, corriente_a, largo_metros)
