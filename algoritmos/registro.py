"""Catálogo extensible: cada algoritmo declara sus requisitos de pesos.

Los futuros algoritmos deben respetar el contrato Resultado/Paso. No se
incluyen botones de algoritmos que todavía no están implementados.
"""
from dataclasses import dataclass
from typing import Callable
from .dijkstra import ejecutar_dijkstra
from .tipos import Resultado


@dataclass(frozen=True)
class Algoritmo:
    identificador: str
    nombre: str
    acepta_negativos: bool
    ejecutar: Callable[..., Resultado]


ALGORITMOS = (Algoritmo('dijkstra', 'Dijkstra', False, ejecutar_dijkstra),)
