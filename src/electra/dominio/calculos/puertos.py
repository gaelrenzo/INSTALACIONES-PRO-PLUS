"""Ports — abstract interfaces for norm strategy implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from electra_core.modelos.topologia import Circuito, RedElectrica, Tablero


class EstrategiaNormativa(ABC):
    @abstractmethod
    def validar_caida_tension(self, circuito: Circuito) -> list[str]: ...

    @abstractmethod
    def validar_tablero(self, tablero: Tablero) -> list[str]: ...

    @abstractmethod
    def validar_red(self, red: RedElectrica) -> list[str]: ...
