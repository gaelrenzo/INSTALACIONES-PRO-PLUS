"""Enums unificados del dominio eléctrico."""

from __future__ import annotations

from enum import Enum


class TipoCircuito(str, Enum):
    ALUMBRADO = "alumbrado"
    TOMACORRIENTE = "tomacorriente"
    ELECTROBOMBA = "electrobomba"
    CALENTADOR = "calentador"
    COCINA = "cocina"
    LAVADORA = "lavadora"
    SECADORA = "secadora"
    HIDROMASAJE = "hidromasaje"
    AIRE_ACONDICIONADO = "aire_acondicionado"
    RESERVA = "reserva"
    OTRO = "otro"


class TipoConductor(str, Enum):
    TW = "TW"
    THW = "THW"
    THHN = "THHN"
    THWN = "THWN"
    XHHW = "XHHW"
    PVC = "PVC"
    XLPE = "XLPE"


class TipoNormativa(str, Enum):
    CNE = "CNE"
    NEC = "NEC"
    IEC = "IEC"


class Fase(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    TRIFASICO = "ABC"
