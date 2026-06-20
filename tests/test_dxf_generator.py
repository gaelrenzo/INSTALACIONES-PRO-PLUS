from __future__ import annotations

import ezdxf

from electra_core.modelos.topologia import (
    RedElectrica,
    Tablero,
    Circuito,
    Carga,
    Cable,
    TipoNormativa,
)
from electra_core.dominios.cad.generador_dxf import GeneradorDXF


def _red_mock() -> RedElectrica:
    return RedElectrica(
        nombre_proyecto="Mock",
        normativa=TipoNormativa.CNE,
        tableros=[
            Tablero(
                nombre="TG",
                circuitos=[
                    Circuito(
                        nombre="C1",
                        cable=Cable(seccion_mm2=2.5),
                        cargas=[Carga(nombre="L1", potencia_w=100)],
                        largo_metros=10,
                    ),
                ],
            ),
        ],
    )


def test_generar_dxf_en_memoria(tmp_path) -> None:
    ruta = str(tmp_path / "test.dxf")
    gen = GeneradorDXF()
    resultado = gen.exportar_diagrama(_red_mock(), ruta)
    doc = ezdxf.readfile(resultado)
    msp = doc.modelspace()
    entities = list(msp)
    assert len(entities) > 0
    assert any(e.dxftype() == "LINE" for e in entities)
    assert any(e.dxftype() == "TEXT" for e in entities)
