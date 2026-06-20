from __future__ import annotations

import pandapower as pp
from pandapower import networks as nw

from electra_core.modelos.topologia import RedElectrica, Tablero, Circuito, Cable


class ResolverRed:
    def __init__(self, red: RedElectrica) -> None:
        self.red = red
        self.net = pp.create_empty_network()

    def construir_en_pandapower(self) -> None:
        pp.create_bus(self.net, name="Acometida", vn_kv=self.red.tension_acometida_v / 1000)
        bus_anterior = 0

        for tablero in self.red.tableros:
            pp.create_bus(
                self.net,
                name=tablero.nombre,
                vn_kv=tablero.tension_v / 1000,
            )
            tid = len(self.net.bus) - 1
            pp.create_line(
                self.net,
                from_bus=bus_anterior,
                to_bus=tid,
                length_km=0.010,
                std_type="NAYY 4x50 SE",
                name=f"Linea_{tablero.nombre}",
            )
            lvid = len(self.net.line) - 1
            for circuito in tablero.circuitos:
                pp.create_load(
                    self.net,
                    bus=tid,
                    p_kw=sum(c.potencia_w for c in circuito.cargas) / 1000,
                    name=circuito.nombre,
                )

    def ejecutar_flujo(self) -> dict:
        self.construir_en_pandapower()
        pp.runpp(self.net)
        buses = self.net.res_bus[["vm_pu", "va_degree"]].to_dict(orient="index")
        lines = self.net.res_line[["loading_percent", "i_ka"]].to_dict(orient="index")
        return {"buses": buses, "lines": lines}

    def calcular_cortocircuito(self) -> dict:
        from pandapower.shortcircuit import calc_sc
        calc_sc(self.net, case="max", study="complete", return_as_dict=True)
        sc_result = self.net.res_bus_sc
        return sc_result.to_dict(orient="index")
