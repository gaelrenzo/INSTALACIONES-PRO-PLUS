"""Shared domain layer — value objects, enums, base events."""

from electra.dominio.shared.enums import Fase, TipoCircuito, TipoConductor, TipoNormativa
from electra.dominio.shared.eventos import EventoDominio
from electra.dominio.shared.value_objects import (
    Coordenadas,
    Dimension,
    Porcentaje,
    Potencia,
    SeccionConductor,
    Tension,
)

__all__ = [
    "Coordenadas",
    "Dimension",
    "Fase",
    "Porcentaje",
    "Potencia",
    "SeccionConductor",
    "Tension",
    "TipoCircuito",
    "TipoConductor",
    "TipoNormativa",
    "EventoDominio",
]
