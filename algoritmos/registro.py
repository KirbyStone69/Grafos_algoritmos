"""Catálogo extensible: cada algoritmo declara sus requisitos de pesos.

Cada algoritmo declara su propio contrato de resultado y eventos. No se
incluyen botones de algoritmos que todavía no están implementados.
"""
from dataclasses import dataclass
from typing import Callable
from .dijkstra import ejecutar_dijkstra
from .bellman_ford import ejecutar_bellman_ford
from .warshall_floyd import ejecutar_warshall_floyd


@dataclass(frozen=True)
class Algoritmo:
    identificador: str
    nombre: str
    acepta_negativos: bool
    ejecutar: Callable[..., object]
    grafo_preferido: str | None = None


ALGORITMOS = (
    Algoritmo('dijkstra', 'Dijkstra', False, ejecutar_dijkstra, 'positivo'),
    Algoritmo('bellman_ford', 'Bellman–Ford', True, ejecutar_bellman_ford, 'original'),
    Algoritmo('warshall_floyd', 'Floyd–Warshall', True, ejecutar_warshall_floyd, 'positivo'),
)
