import pytest

def calcular_caida_tension_monofasica(corriente_a, longitud_m, seccion_mm2, rho=0.0175):
    """
    Cálculo de caída de tensión monofásica:
    dV = 2 * I * L * rho / Seccion
    """
    if seccion_mm2 <= 0:
        raise ValueError("La sección del conductor debe ser mayor a cero.")
    return (2 * corriente_a * longitud_m * rho) / seccion_mm2

def test_caida_tension_normal():
    # Circuito de tomacorrientes típica: 16A, 15m, 2.5 mm2
    dv = calcular_caida_tension_monofasica(16, 15, 2.5)
    # dv = 2 * 16 * 15 * 0.0175 / 2.5 = 3.36 V
    assert abs(dv - 3.36) < 0.01
    
    # En porcentaje (sistema de 220V)
    pct = (dv / 220) * 100
    # pct = (3.36 / 220) * 100 = 1.527%
    assert pct < 2.5  # Límite CNE para circuitos derivados es 2.5%

def test_caida_tension_alimentador():
    # Alimentador de 32A, 10m, 10 mm2
    dv = calcular_caida_tension_monofasica(32, 10, 10)
    # dv = 2 * 32 * 10 * 0.0175 / 10 = 1.12 V
    assert abs(dv - 1.12) < 0.01
    
    pct = (dv / 220) * 100
    assert pct < 1.5  # Límite CNE para alimentadores es 1.5%

def test_seccion_invalida():
    with pytest.raises(ValueError):
        calcular_caida_tension_monofasica(10, 20, 0)
