"""Cálculos eléctricos — dominio puro."""

from __future__ import annotations

from .cne import CNEPeru
from .escenarios import ejecutar_calculos, ejecutar_escenario, calcular_circuito

__all__ = ["CNEPeru", "ejecutar_calculos", "ejecutar_escenario", "calcular_circuito"]
