"""Asocia cada algoritmo a su interfaz completa, sin imponerle controles o tablas."""
from .algoritmos.dijkstra import InterfazDijkstra

INTERFACES = {'dijkstra': InterfazDijkstra}
