from __future__ import annotations

import pytest
import yaml

from electra_core.modelos.topologia import (
    RedElectrica,
    Tablero,
    Circuito,
    Carga,
    Cable,
    TipoNormativa,
)
from electra_core.core.normativas.cne import CNEPeru


@pytest.fixture
def norma() -> CNEPeru:
    return CNEPeru()


def test_caida_tension_ok(norma: CNEPeru) -> None:
    circuito = Circuito(
        nombre="C1",
        cable=Cable(seccion_mm2=4.0),
        caida_tension_max_porcentaje=2.0,
        largo_metros=30,
    )
    alertas = norma.validar_caida_tension(circuito)
    assert len(alertas) == 0


def test_caida_tension_excede(norma: CNEPeru) -> None:
    circuito = Circuito(
        nombre="C1",
        cable=Cable(seccion_mm2=2.5),
        caida_tension_max_porcentaje=3.0,
        largo_metros=50,
    )
    alertas = norma.validar_caida_tension(circuito)
    assert any("CNE" in a for a in alertas)


def test_calculo_resistencia_pst(norma: CNEPeru) -> None:
    R = norma.calcular_resistencia_pst(100, 2.4, 16)
    assert 10 < R < 40


def test_calculo_caida_tension(norma: CNEPeru) -> None:
    cable = Cable(seccion_mm2=4.0)
    caida = norma.calcular_caida_tension(cable, 20, 30)
    assert 0 < caida < 5
