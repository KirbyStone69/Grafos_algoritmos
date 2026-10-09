"""Matrices del multigrafo no dirigido; se conserva cada arista paralela.

Adyacencia: número de conexiones por par, sin sumar ni alterar sus pesos.
Incidencia: 1 en los extremos de cada arista (2 para un bucle).
Los pesos se conservan en la lista de aristas para las ayudas de la interfaz.
"""
from dataclasses import dataclass
from algoritmos.tipos import Arista


@dataclass(frozen=True)
class MatricesGrafo:
    nodos: tuple
    aristas: tuple[Arista, ...]
    adyacencia: tuple[tuple[int, ...], ...]
    incidencia: tuple[tuple[int, ...], ...]


def construir_matrices(grafo):
    nodos = tuple(sorted(grafo.nodes))
    indices = {nodo: indice for indice, nodo in enumerate(nodos)}
    aristas = tuple(Arista(u, v, clave, datos['weight'])
                    for u, v, clave, datos in grafo.edges(keys=True, data=True))
    adyacencia = [[0] * len(nodos) for _ in nodos]
    incidencia = [[0] * len(aristas) for _ in nodos]
    for columna, arista in enumerate(aristas):
        u, v = indices[arista.origen], indices[arista.destino]
        adyacencia[u][v] += 1
        if u != v:
            adyacencia[v][u] += 1
        incidencia[u][columna] += 1
        incidencia[v][columna] += 1
    return MatricesGrafo(nodos, aristas, tuple(map(tuple, adyacencia)),
                         tuple(map(tuple, incidencia)))
