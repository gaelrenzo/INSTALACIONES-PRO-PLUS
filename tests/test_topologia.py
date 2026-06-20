from __future__ import annotations

import pytest
from pydantic import ValidationError

from electra_core.modelos.topologia import (
    RedElectrica,
    Tablero,
    Circuito,
    Carga,
    Cable,
    TipoCircuito,
    TipoConductor,
    TipoNormativa,
)


def _red_basica() -> RedElectrica:
    return RedElectrica(
        nombre_proyecto="Test",
        normativa=TipoNormativa.CNE,
        tableros=[
            Tablero(
                nombre="TG",
                circuitos=[
                    Circuito(
                        nombre="C1",
                        tipo=TipoCircuito.ALUMBRADO,
                        cable=Cable(seccion_mm2=2.5, tipo=TipoConductor.THW),
                        cargas=[Carga(nombre="L1", potencia_w=100)],
                        largo_metros=20,
                    )
                ],
            )
        ],
    )


def test_red_valida() -> None:
    red = _red_basica()
    assert red.nombre_proyecto == "Test"
    assert len(red.tableros) == 1
    assert len(red.tableros[0].circuitos) == 1


def test_red_demanda_total() -> None:
    red = _red_basica()
    total = red.calcular_demanda_total()
    assert total == 70.0  # 100 * 0.7


def test_caida_tension_invalida() -> None:
    with pytest.raises(ValidationError):
        Circuito(
            nombre="C1",
            cable=Cable(seccion_mm2=2.5),
            caida_tension_max_porcentaje=-1,
        )
