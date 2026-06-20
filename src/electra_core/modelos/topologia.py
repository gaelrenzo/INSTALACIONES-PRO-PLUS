from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


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


class Cable(BaseModel):
    seccion_mm2: float
    tipo: TipoConductor = TipoConductor.THW
    material: str = "cobre"
    fase: Fase = Fase.TRIFASICO
    largo_metros: float = 0.0
    caida_tension_porcentaje: float = 0.0
    temperatura_ambiente: float = 30.0
    factor_agrupamiento: float = 1.0
    factor_armonicos: float = 1.0
    ampacidad_a: float = 0.0


class Carga(BaseModel):
    nombre: str
    potencia_w: float
    factor_demanda: float = 1.0
    factor_potencia: float = 0.9
    tension_v: float = 220.0
    tipo: TipoCircuito = TipoCircuito.OTRO
    fase: Fase = Fase.A


class Tablero(BaseModel):
    nombre: str
    tension_v: float = 220.0
    proteccion_a: float = 0.0
    poder_corte_ka: float = 0.0
    circuitos: list[Circuito] = Field(default_factory=list)
    carga_total_w: float = 0.0


class Circuito(BaseModel):
    nombre: str
    tipo: TipoCircuito = TipoCircuito.OTRO
    cargas: list[Carga] = Field(default_factory=list)
    cable: Cable
    proteccion_a: float = 0.0
    largo_metros: float = 0.0
    caida_tension_max_porcentaje: float = 2.5
    fase: Fase = Fase.A

    @model_validator(mode="after")
    def _validar_caida(self):
        if self.caida_tension_max_porcentaje <= 0:
            raise ValueError("La caída de tensión máxima debe ser positiva")
        return self


class RedElectrica(BaseModel):
    nombre_proyecto: str
    normativa: TipoNormativa = TipoNormativa.CNE
    tableros: list[Tablero] = Field(default_factory=list)
    tension_acometida_v: float = 380.0
    demanda_total_w: float = 0.0
    factor_simultaneidad: float = 0.7

    def calcular_demanda_total(self) -> float:
        total = sum(t.carga_total_w for t in self.tableros)
        self.demanda_total_w = total * self.factor_simultaneidad
        return self.demanda_total_w
