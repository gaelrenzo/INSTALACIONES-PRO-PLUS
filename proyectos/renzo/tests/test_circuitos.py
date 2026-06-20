import pytest

def calcular_corriente_diseno(potencia_w, tension_v=220, cos_phi=0.9):
    """
    Corriente de empleo: Ib = P / (V * cos_phi)
    """
    if tension_v <= 0 or cos_phi <= 0 or cos_phi > 1.0:
        raise ValueError("Tensión y factor de potencia inválidos.")
    return potencia_w / (tension_v * cos_phi)

def seleccionar_itm(corriente_a):
    """
    Selección comercial de Interruptor Termomagnético (ITM) estándar
    """
    valores_comerciales = [10, 16, 20, 25, 32, 40, 50, 63, 80, 100]
    corriente_minima = 1.25 * corriente_a  # 125% por norma
    
    for val in valores_comerciales:
        if val >= corriente_minima:
            return val
    return valores_comerciales[-1]  # Por defecto el mayor si excede

def test_corriente_diseno():
    # Circuito de alumbrado de 350 W
    ib = calcular_corriente_diseno(350, 220, 0.9)
    # ib = 350 / (220 * 0.9) = 1.767 A
    assert abs(ib - 1.767) < 0.01

def test_seleccion_itm_alumbrado():
    # Alumbrado (Ib = 1.77A -> 1.25 * 1.77 = 2.21A -> ITM sugerido de 10A)
    assert seleccionar_itm(1.77) == 10

def test_seleccion_itm_tomacorrientes():
    # Tomacorrientes (Ib = 10A -> 1.25 * 10 = 12.5A -> ITM IEC de 16A)
    assert seleccionar_itm(10) == 16
    assert seleccionar_itm(12) == 16
    assert seleccionar_itm(25) == 32

def test_valores_invalidos():
    with pytest.raises(ValueError):
        calcular_corriente_diseno(1000, 0, 0.9)
    with pytest.raises(ValueError):
        calcular_corriente_diseno(1000, 220, 1.2)
