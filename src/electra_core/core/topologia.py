from __future__ import annotations

import networkx as nx

from electra_core.modelos.topologia import RedElectrica, Tablero, Circuito, Carga


class GrafoTopologico:
    def __init__(self, red: RedElectrica) -> None:
        self.red = red
        self.grafo: nx.DiGraph = nx.DiGraph()
        self._construir()

    def _construir(self) -> None:
        for tablero in self.red.tableros:
            self.grafo.add_node(tablero.nombre, tipo="tablero", datos=tablero)
            for circuito in tablero.circuitos:
                nodo_circuito = f"{tablero.nombre}.{circuito.nombre}"
                self.grafo.add_edge(
                    tablero.nombre, nodo_circuito, tipo="circuito", datos=circuito
                )
                for carga in circuito.cargas:
                    nodo_carga = f"{nodo_circuito}.{carga.nombre}"
                    self.grafo.add_node(nodo_carga, tipo="carga", datos=carga)
                    self.grafo.add_edge(
                        nodo_circuito, nodo_carga, tipo="carga", datos=carga
                    )

    def obtener_tableros(self) -> list[Tablero]:
        return self.red.tableros

    def obtener_circuitos(self, tablero: Tablero) -> list[Circuito]:
        return tablero.circuitos

    def obtener_cargas(self, circuito: Circuito) -> list[Carga]:
        return circuito.cargas

    def camino_critico(self) -> list[str]:
        return list(nx.dag_longest_path(self.grafo, weight="potencia"))
