"""Value objects inmutables del dominio eléctrico."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Coordenadas(BaseModel):
    x: float = Field(description="Coordenada X en metros")
    y: float = Field(description="Coordenada Y en metros")


class Dimension(BaseModel):
    largo: float = Field(gt=0, description="Largo en metros")
    ancho: float = Field(gt=0, description="Ancho en metros")


class Potencia(BaseModel):
    watts: float = Field(ge=0, description="Potencia en vatios")


class SeccionConductor(BaseModel):
    mm2: float = Field(gt=0, description="Sección transversal en mm²")
    material: str = "cobre"


class Tension(BaseModel):
    voltios: float = Field(gt=0, description="Tensión en voltios")


class Porcentaje(BaseModel):
    valor: float = Field(ge=0, le=100, description="Valor porcentual 0-100")
