"""Orquestación multi-escenario para cálculos eléctricos."""

from __future__ import annotations

import copy
import math
from typing import Any, Dict, List, Optional, Tuple

from electra.dominio.calculos.cne import CNEPeru


def cne_050_200_basic_load(area_m2: Optional[float]) -> float:
    """Carga básica CNE-U 050-200 según área techada."""
    if area_m2 is None:
        return 0.0
    if area_m2 <= 90:
        return 2500.0
    return 2500.0 + 1000.0 * math.ceil((area_m2 - 90.0) / 90.0)


def apply_scenario_overrides(base_circuits: List[Dict], scenario: Dict) -> List[Dict]:
    circuits = copy.deepcopy(base_circuits)
    overrides = scenario.get("circuito_overrides", {})
    for circuit in circuits:
        override = overrides.get(circuit["id"])
        if override:
            circuit.update(override)
    return circuits


def _get_rho(params: Dict) -> float:
    """Resistividad respetando legacy (resistividad_auto, resistividad_cobre_rho)."""
    auto = params.get("resistividad_auto", True)
    if not auto:
        return params.get("resistividad_cobre_rho", params.get("resistividad_rho_mohm", 0.0175))
    return params.get("resistividad_rho_mohm", 0.0175)


def calcular_circuito(circ: Dict, params: Dict) -> Dict:
    pi = circ["potencia_instalada_w"]
    fd = circ["factor_demanda"]
    v_nominal = params.get("tension_v", 220)
    cosphi = params.get("factor_potencia_cosphi", 0.90)
    factor_diseno = params.get("factor_diseno_conductor", 1.25)
    material = params.get("material_conductor", "cobre")
    modo = params.get("modo_instalacion", "ducto")
    rho = _get_rho(params)
    caida_max = params.get("caida_tension_max_derivados_porc", 2.5)

    md = pi * fd
    ib = md / (v_nominal * cosphi) if cosphi > 0 else 0
    id_current = ib * factor_diseno
    section = float(circ.get("seccion_conductor_mm2", 2.5))
    length = circ.get("longitud_m", 15.0)

    cne = CNEPeru()
    ampacity = cne.get_ampacity(section, material, modo)
    itm = cne.find_appropriate_itm(ib, ampacity)
    dv = (2.0 * length * ib * rho) / section if section > 0 else 0
    dv_porc = (dv / v_nominal) * 100.0 if v_nominal > 0 else 0

    descripcion = circ.get("descripcion", "").lower()
    requires_diff = circ.get("requiere_diferencial")
    if requires_diff is None:
        requires_diff = any(
            t in descripcion
            for t in ("tomacorriente", "cocina", "lavadora", "bomba", "banio", "baño")
        )
    diff_rating = 25 if itm <= 20 else (40 if itm <= 32 else 63)
    diff_str = f"2P-{diff_rating}A-30mA" if requires_diff else "Ver diferencial general"

    return {
        "id": circ["id"],
        "descripcion": circ["descripcion"],
        "estado": circ.get("estado", "preliminar"),
        "fuente": circ.get("fuente", "por confirmar"),
        "potencia_instalada_w": round(pi, 2),
        "factor_demanda": fd,
        "maxima_demanda_w": round(md, 2),
        "corriente_empleo_ib_a": round(ib, 3),
        "corriente_diseno_id_a": round(id_current, 3),
        "seccion_conductor_mm2": section,
        "ampacidad_conductor_iz_a": ampacity,
        "longitud_m": length,
        "caida_tension_v": round(dv, 3),
        "caida_tension_porc": round(dv_porc, 3),
        "itm_a": itm,
        "itm_sugerido": f"2P-{itm}A",
        "diferencial_sugerido": diff_str,
        "requiere_diferencial": bool(requires_diff),
        "requiere_tierra": circ.get("requiere_tierra", True),
        "diametro_tubo_pvc_mm": circ.get("diametro_tubo_mm", 20),
        "cumple_conductor": "CUMPLE" if id_current <= ampacity else "SOBRECARGADO",
        "cumple_coordinacion": "CUMPLE" if ib <= itm <= ampacity else "REVISAR ITM",
        "cumple_caida": "CUMPLE" if dv_porc <= caida_max else "EXCEDE LIMITE",
    }


def ejecutar_escenario(data: Dict, escenario: Dict) -> Dict:
    params = data["parametros_electricos"]
    material = params.get("material_conductor", "cobre")
    modo = params.get("modo_instalacion", "ducto")
    rho = _get_rho(params)
    area_total = data["areas"]["techada_total_calculo_m2"]["valor"]

    circuits = apply_scenario_overrides(data["circuitos_base"], escenario)
    calculated = [calcular_circuito(c, params) for c in circuits]

    total_pi = sum(c["potencia_instalada_w"] for c in calculated)
    md_circuitos = sum(c["maxima_demanda_w"] for c in calculated)

    cne_info = escenario.get("cne_050_200", {})
    cne_area = cne_050_200_basic_load(area_total) if cne_info.get("aplicar", True) else 0
    cne_cocina = cne_info.get("cocina_electrica_normativa_w", 0)
    md_cne = cne_area + cne_cocina
    md_adoptada = max(md_circuitos, md_cne)
    metodo = "CNE-U 050-200" if md_cne >= md_circuitos else "Circuitos derivados"

    v_nominal = params["tension_v"]
    cosphi = params.get("factor_potencia_cosphi", 0.90)
    factor_diseno = params.get("factor_diseno_conductor", 1.25)
    caida_max_alim = params.get("caida_tension_max_alimentador_porc", 1.5)

    ib_total = md_adoptada / (v_nominal * cosphi) if cosphi > 0 else 0
    id_total = ib_total * factor_diseno

    cne = CNEPeru()
    alim_section = 10.0
    alim_ampacity = cne.get_ampacity(alim_section, material, modo)
    for sec in [10, 16, 25, 35, 50, 70]:
        amp = cne.get_ampacity(sec, material, modo)
        if amp >= id_total:
            alim_section = sec
            alim_ampacity = amp
            break

    alim_length = data.get("alimentacion_principal", {}).get("longitud_m", 10)
    alim_dv = (2.0 * alim_length * ib_total * rho) / alim_section
    alim_dv_porc = (alim_dv / v_nominal) * 100.0 if v_nominal > 0 else 0
    alim_itm = cne.find_appropriate_itm(ib_total, alim_ampacity)

    return {
        "id": escenario["id"],
        "nombre": escenario["nombre"],
        "estado": escenario.get("estado", "preliminar"),
        "resumen_general": {
            "potencia_instalada_total_w": round(total_pi, 2),
            "maxima_demanda_circuitos_w": round(md_circuitos, 2),
            "cne_050_200_area_w": round(cne_area, 2),
            "cne_050_200_cocina_w": round(cne_cocina, 2),
            "maxima_demanda_cne_w": round(md_cne, 2),
            "maxima_demanda_adoptada_w": round(md_adoptada, 2),
            "metodo_gobernante": metodo,
            "corriente_empleo_ib_total_a": round(ib_total, 2),
            "corriente_diseno_id_total_a": round(id_total, 2),
            "alimentador_seccion_mm2": alim_section,
            "alimentador_ampacidad_iz_a": alim_ampacity,
            "alimentador_longitud_m": alim_length,
            "alimentador_caida_tension_v": round(alim_dv, 3),
            "alimentador_caida_tension_porc": round(alim_dv_porc, 3),
            "alimentador_itm_a": alim_itm,
            "alimentador_itm_sugerido": f"2P-{alim_itm}A",
            "cumple_conductor_alimentador": "CUMPLE" if id_total <= alim_ampacity else "SOBRECARGADO",
            "cumple_coordinacion_alimentador": "CUMPLE" if ib_total <= alim_itm <= alim_ampacity else "REVISAR ITM",
            "cumple_caida_alimentador": "CUMPLE" if alim_dv_porc <= caida_max_alim else "EXCEDE LIMITE",
        },
        "circuitos_calculados": calculated,
    }


def ejecutar_calculos(data: Dict) -> Dict:
    scenarios = {}
    for escenario in data.get("escenarios", []):
        scenarios[escenario["id"]] = ejecutar_escenario(data, escenario)

    design_id = data.get("escenario_dimensionamiento_id") or data["escenarios"][0]["id"]

    return {
        "proyecto": data["proyecto"],
        "propietario": data["propietario"],
        "ubicacion": data.get("ubicacion", {}),
        "areas": data.get("areas", {}),
        "parametros_electricos": data.get("parametros_electricos", {}),
        "alimentacion_principal": data.get("alimentacion_principal", {}),
        "escenario_dimensionamiento_id": design_id,
        "escenario_dimensionamiento": scenarios[design_id],
        "escenarios": scenarios,
    }
