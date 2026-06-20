import pytest

def calcular_presupuesto_total(costo_materiales, factor_mano_obra=0.40, igv_porc=0.18):
    """
    Cálculo de presupuesto incluyendo mano de obra e IGV
    """
    if costo_materiales < 0:
        raise ValueError("El costo de materiales no puede ser negativo.")
    mano_obra = costo_materiales * factor_mano_obra
    subtotal = costo_materiales + mano_obra
    igv = subtotal * igv_porc
    total = subtotal + igv
    return {
        "mano_obra": round(mano_obra, 2),
        "subtotal": round(subtotal, 2),
        "igv": round(igv, 2),
        "total": round(total, 2)
    }

def test_presupuesto_normal():
    # Costo materiales de S/ 9021.90
    res = calcular_presupuesto_total(9021.90)
    # mano_obra = 9021.90 * 0.40 = 3608.76
    # subtotal = 9021.90 + 3608.76 = 12630.66
    # igv = 12630.66 * 0.18 = 2273.5188 -> 2273.52
    # total = 12630.66 + 2273.52 = 14904.18
    assert res["mano_obra"] == 3608.76
    assert res["subtotal"] == 12630.66
    assert res["igv"] == 2273.52
    assert res["total"] == 14904.18

def test_presupuesto_cero():
    res = calcular_presupuesto_total(0)
    assert res["total"] == 0.0

def test_costo_negativo():
    with pytest.raises(ValueError):
        calcular_presupuesto_total(-100)
