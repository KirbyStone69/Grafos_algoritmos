"""Asocia cada algoritmo a su interfaz completa, sin imponerle controles o tablas."""
from .algoritmos.dijkstra import InterfazDijkstra
from .algoritmos.bellman_ford import InterfazBellmanFord
from .algoritmos.warshall_floyd import InterfazWarshallFloyd

INTERFACES = {'dijkstra': InterfazDijkstra, 'bellman_ford': InterfazBellmanFord, 'warshall_floyd': InterfazWarshallFloyd}
