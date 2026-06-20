import pytest

def calcular_demanda_area(area_m2):
    """
    Cálculo de la demanda básica por área techada (CNE-U Regla 050-200)
    - Primeros 90 m2: 2500 W
    - Siguientes 90 m2 o fracción: 1000 W
    """
    if area_m2 <= 0:
        return 0
    if area_m2 <= 90:
        return 2500
    
    area_restante = area_m2 - 90
    fracciones = (area_restante + 89) // 90  # división entera hacia arriba
    return 2500 + (fracciones * 1000)

def test_demanda_basica_pequena():
    assert calcular_demanda_area(45) == 2500
    assert calcular_demanda_area(90) == 2500

def test_demanda_basica_mediana():
    assert calcular_demanda_area(120) == 3500  # 90m2 (2500) + 30m2 (1000)
    assert calcular_demanda_area(180) == 3500

def test_demanda_basica_grande():
    assert calcular_demanda_area(200) == 4500  # 90m2 (2500) + 90m2 (1000) + 20m2 (1000)

def test_demanda_basica_invalida():
    assert calcular_demanda_area(-10) == 0
    assert calcular_demanda_area(0) == 0
