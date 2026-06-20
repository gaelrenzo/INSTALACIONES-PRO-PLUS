import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # src/

from electra.infraestructura.presupuestos.normalizador_materiales import (
    detectar_categoria,
    extraer_especificaciones,
    normalizar_nombre_material,
)


def test_normaliza_cable_con_circuito():
    assert normalizar_nombre_material("Cable TW THW 2.5 mm2 - C1") == "cable electrico thw 2.5 mm2 cobre"


def test_normaliza_itm():
    assert normalizar_nombre_material("ITM 2P-10A - C1") == "interruptor termomagnetico 2 polos 10A"


def test_normaliza_diferencial():
    assert normalizar_nombre_material("Diferencial 2P-25A-30mA - C2") == "interruptor diferencial 2 polos 25A 30mA"


def test_detecta_specs():
    specs = extraer_especificaciones("Diferencial 2P-25A-30mA - C2")
    assert specs["polos"] == 2
    assert specs["amperaje_a"] == 25
    assert specs["sensibilidad_ma"] == 30


def test_detecta_categoria():
    assert detectar_categoria("Tubo PVC SAP 20 mm - C1") == "ductos/tuberias"
    assert detectar_categoria("Tablero general para 8 circuitos") == "tableros electricos"
    assert detectar_categoria("Bornera PVC 25mm 60amp") != "ductos/tuberias"


def test_convierte_medida_comercial_imperial_de_tubo():
    assert extraer_especificaciones('Tubo SAP PVC 1/2" Electrico')["diametro_mm"] == 20.0
    assert extraer_especificaciones("Tubo conduit 3/4 pulg")["diametro_mm"] == 25.0
