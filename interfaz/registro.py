"""Asocia cada algoritmo a su interfaz completa, sin imponerle controles o tablas."""
from .algoritmos.dijkstra import InterfazDijkstra
from .algoritmos.bellman_ford import InterfazBellmanFord
from .algoritmos.warshall_floyd import InterfazWarshallFloyd
from .algoritmos.a_estrella import InterfazAEstrella

INTERFACES = {
    'dijkstra': InterfazDijkstra,
    'bellman_ford': InterfazBellmanFord,
    'warshall_floyd': InterfazWarshallFloyd,
    'a_estrella': InterfazAEstrella,
}
